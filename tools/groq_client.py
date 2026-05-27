import os
import re
import time
import threading
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError

# Load environment variables from .env file
# override=True ensures values from .env always win over stale OS env vars
load_dotenv(override=True)

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------
PRIMARY_MODEL  = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"    # Active lightweight fallback

# Max tokens per completion (keeps daily spend predictable)
MAX_COMPLETION_TOKENS = 1500

# Hard character cap on prompts  (~3 000 tokens worth of text)
PROMPT_CHAR_LIMIT = 12_000

# Retry settings for transient / per-minute errors
MAX_RETRIES = 3
BASE_DELAY  = 5   # seconds for first retry (doubles each attempt)

# Thread-level lock so concurrent Streamlit threads don't step on each other
_rate_limit_lock = threading.Lock()

# -----------------------------------------------------------------------
# Key Rotation
# -----------------------------------------------------------------------

def _load_api_keys() -> list[str]:
    """
    Reads ALL Groq API keys defined in the .env file.

    Looks for:
        GROQ_API_KEY       – always required (key #1)
        GROQ_API_KEY_2     – optional second key
        GROQ_API_KEY_3     – optional third key
        ... and so on up to GROQ_API_KEY_9

    Returns a deduplicated list of valid (non-placeholder) keys in order.
    """
    keys = []
    # Always check the primary key first
    primary = os.getenv("GROQ_API_KEY", "").strip()
    if primary and not primary.startswith("YOUR_"):
        keys.append(primary)

    # Then check numbered extras: GROQ_API_KEY_2 … GROQ_API_KEY_9
    for i in range(2, 10):
        extra = os.getenv(f"GROQ_API_KEY_{i}", "").strip()
        if extra and not extra.startswith("YOUR_") and extra not in keys:
            keys.append(extra)

    if not keys:
        raise ValueError(
            "No valid GROQ_API_KEY found in .env. "
            "Please set GROQ_API_KEY (and optionally GROQ_API_KEY_2, etc.)."
        )

    return keys


def _make_client(api_key: str) -> OpenAI:
    """Returns an OpenAI SDK client pointed at the Groq API endpoint."""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


# Keep a module-level reference to the loaded keys so we only read .env once
# per process (re-loaded on first call inside ask_groq).
_api_keys: list[str] | None = None

def _get_api_keys() -> list[str]:
    global _api_keys
    if _api_keys is None:
        # Re-read .env every time we (re)load keys so newly added keys
        # are picked up without restarting the Streamlit server.
        load_dotenv(override=True)
        _api_keys = _load_api_keys()
    return _api_keys


def _invalidate_key_cache():
    """Call this when all keys are exhausted so the next request re-reads .env."""
    global _api_keys
    _api_keys = None


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _parse_wait_seconds(error_message: str) -> float:
    """
    Parses Groq's '...try again in Xm Ys' hint from a 429 error body
    and returns the number of seconds to wait.
    Falls back to BASE_DELAY if the pattern isn't found.
    """
    match = re.search(r"try again in\s*(?:(\d+)m)?(\d+(?:\.\d+)?)s", str(error_message))
    if match:
        minutes = int(match.group(1)) if match.group(1) else 0
        seconds = float(match.group(2))
        return minutes * 60 + seconds
    return float(BASE_DELAY)


def _truncate_prompt(prompt: str) -> str:
    """
    Hard-caps the prompt at PROMPT_CHAR_LIMIT characters to avoid burning
    the daily token budget on a single request.
    Preserves both the header and tail of the prompt.
    """
    if len(prompt) <= PROMPT_CHAR_LIMIT:
        return prompt
    half = PROMPT_CHAR_LIMIT // 2
    return (
        prompt[:half]
        + "\n\n[... content truncated to fit token budget ...]\n\n"
        + prompt[-half:]
    )


def _is_daily_quota_error(error_str: str) -> bool:
    return (
        ("429" in error_str or "rate_limit_exceeded" in error_str)
        and ("tokens per day" in error_str.lower() or "tpd" in error_str.lower())
    )

def _is_per_minute_quota_error(error_str: str) -> bool:
    return (
        ("429" in error_str or "rate_limit_exceeded" in error_str)
        and not _is_daily_quota_error(error_str)
    )

def _is_permanent_error(error_str: str) -> bool:
    """400-class errors that will never succeed on retry."""
    return (
        "400" in error_str
        or "model_decommissioned" in error_str
        or "invalid_request_error" in error_str
    )


# -----------------------------------------------------------------------
# Core public function
# -----------------------------------------------------------------------

def ask_groq(prompt: str, max_tokens: int = MAX_COMPLETION_TOKENS) -> str:
    """
    Sends a prompt to the Groq API and returns the AI response.

    Rotation strategy:
      For every API key defined in .env (GROQ_API_KEY, GROQ_API_KEY_2, …):
        → Try PRIMARY_MODEL  (llama-3.3-70b-versatile)
        → On daily-quota hit → try FALLBACK_MODEL (llama-3.1-8b-instant)
        → On daily-quota hit on fallback → move to the NEXT API KEY
      Only after all keys × all models are exhausted → return a clean error.

    Error classification:
      • Daily quota (TPD 429) → skip model / key immediately
      • Per-minute quota (TPM 429) → wait parsed seconds, retry
      • Permanent (400 / decommissioned) → skip model immediately
      • Transient (5xx / network) → exponential back-off, retry

    Args:
        prompt     (str): Input text to send to the model.
        max_tokens (int): Maximum completion tokens to request.

    Returns:
        str: AI response text, or a user-friendly ⚠️ error message.
    """
    prompt = _truncate_prompt(prompt)

    api_keys = _get_api_keys()
    num_keys = len(api_keys)

    last_error     = None
    exhausted_keys = 0

    for key_idx, api_key in enumerate(api_keys):
        key_label  = f"Key #{key_idx + 1}" if num_keys > 1 else "API key"
        client     = _make_client(api_key)
        key_daily_quota_hit = False

        for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
            model_quota_hit = False

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=0.7,
                    )
                    return response.choices[0].message.content

                except OpenAIError as e:
                    error_str = str(e)
                    last_error = e

                    # ── Daily quota exhausted ──────────────────────────────
                    if _is_daily_quota_error(error_str):
                        print(
                            f"[Groq Client] ⚠️  Daily quota exhausted for "
                            f"model '{model}' ({key_label}). "
                            + ("Rotating to next API key..." if key_idx + 1 < num_keys else "No more keys to try.")
                        )
                        model_quota_hit = True
                        break  # stop retrying this model; try fallback / next key

                    # ── Permanent error (400, decommissioned, etc.) ────────
                    elif _is_permanent_error(error_str):
                        print(
                            f"[Groq Client] ❌ Permanent error on '{model}' "
                            f"({key_label}) — skipping retries."
                        )
                        last_error = e
                        break  # don't retry this model

                    # ── Per-minute rate limit ──────────────────────────────
                    elif _is_per_minute_quota_error(error_str):
                        wait_secs = min(_parse_wait_seconds(error_str), 90)
                        print(
                            f"[Groq Client] ⏳ Per-minute limit on '{model}' "
                            f"({key_label}). Waiting {wait_secs:.0f}s "
                            f"(attempt {attempt}/{MAX_RETRIES})..."
                        )
                        time.sleep(wait_secs)

                    # ── Transient error (5xx, network, etc.) ───────────────
                    else:
                        delay = BASE_DELAY * (2 ** (attempt - 1))
                        print(
                            f"[Groq Client] ⚠️  Transient error on '{model}' "
                            f"({key_label}), attempt {attempt}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)

                except Exception as e:
                    last_error = e
                    delay = BASE_DELAY * (2 ** (attempt - 1))
                    print(
                        f"[Groq Client] ⚠️  Unexpected error (attempt {attempt}): "
                        f"{e}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)

            if model_quota_hit:
                key_daily_quota_hit = True
                # Don't try the other model on this key if daily quota is gone
                break

        if key_daily_quota_hit and key_idx + 1 < num_keys:
            print(
                f"[Groq Client] 🔑 Rotating from {key_label} → Key #{key_idx + 2}..."
            )
            continue  # try next API key

        if key_daily_quota_hit:
            exhausted_keys += 1

    # ── All keys × all models exhausted ────────────────────────────────────
    err_str = str(last_error) if last_error else ""

    if exhausted_keys == num_keys or _is_daily_quota_error(err_str):
        wait_hint = _parse_wait_seconds(err_str)
        minutes   = int(wait_hint // 60)
        seconds   = int(wait_hint % 60)
        key_hint  = (
            f"All **{num_keys} API key(s)** have hit their daily quota."
            if num_keys > 1
            else "Your API key has hit its daily quota."
        )
        # Invalidate the key cache so the NEXT request re-reads .env
        # This means if the user adds a new key to .env, it works immediately
        # on the next button click — no restart required.
        _invalidate_key_cache()
        return (
            f"⚠️ **Daily API token quota reached.**\n\n"
            f"{key_hint} "
            f"Quota resets in approximately **{minutes}m {seconds}s**.\n\n"
            f"**Options to fix this:**\n"
            f"- ⏳ Wait for the quota to reset and try again.\n"
            f"- 🔑 Add more keys to your `.env` file: "
            f"`GROQ_API_KEY_2=...`, `GROQ_API_KEY_3=...`\n"
            f"  *(Get a free key at https://console.groq.com/)*\n"
            f"- 🚀 Upgrade to [Groq Dev Tier](https://console.groq.com/settings/billing) "
            f"for a much higher daily limit."
        )

    return (
        f"⚠️ **AI Engine temporarily unavailable.**\n\n"
        f"All retry attempts failed. Last error: `{last_error}`\n\n"
        f"Please check your API keys and network connection, then try again."
    )


# -----------------------------------------------------------------------
# Legacy helper — kept for backward compatibility
# -----------------------------------------------------------------------

def get_groq_client() -> OpenAI:
    """Returns a client using the first valid API key. Kept for compatibility."""
    return _make_client(_get_api_keys()[0])
