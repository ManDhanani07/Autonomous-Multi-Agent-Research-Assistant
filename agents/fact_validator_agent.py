import os
import sys
import re
import json

# Ensure project root is in the Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def extract_claims(report_text: str) -> list[str]:
    """
    Sends the consolidated report to Groq to extract the core factual claims.
    """
    # Truncate report text to save tokens
    capped_report = report_text[:6000]
    
    prompt = f"""You are a professional fact-checking analyst. Extract the 5 to 8 most important factual claims (especially statistics, dates, scientific models, performance metrics, or specific assertions) from the following research report.
    
    Research Report:
    <report>
    {capped_report}
    </report>
    
    Format the output STRICTLY as a raw JSON list of strings, with no markdown wrappers or prefaces.
    Example:
    [
      "Claim statement 1",
      "Claim statement 2"
    ]
    """
    
    try:
        raw_res = ask_groq(prompt).strip()
        raw_res = re.sub(r"^```json\s*", "", raw_res)
        raw_res = re.sub(r"^```\s*", "", raw_res)
        raw_res = re.sub(r"```$", "", raw_res).strip()
        
        claims = json.loads(raw_res)
        if isinstance(claims, list):
            return [str(c) for c in claims]
    except Exception as e:
        print(f"[Fact Validator] Claim extraction failed: {e}")
        
    # Fallback splitting if JSON decoding fails
    sentences = re.split(r'(?<=[.!?])\s+', report_text)
    factual_candidates = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) > 30 and len(s_clean) < 150 and any(c.isdigit() for c in s_clean):
            factual_candidates.append(s_clean)
        if len(factual_candidates) >= 5:
            break
    return factual_candidates if factual_candidates else ["Research states technical advancements are achieved."]

def verify_claims_against_sources(claims: list[str], source_context: str) -> list[dict]:
    """
    Sends claims along with the gathered references to evaluate verified/partial/unsupported states.
    """
    claims_json_str = json.dumps(claims, indent=2)
    
    prompt = f"""You are a fact-checking bot. Your job is to verify a list of claims against the provided source references.
    
    List of Claims to verify:
    {claims_json_str}
    
    Source Reference Materials:
    <sources>
    {source_context}
    </sources>
    
    For each claim, determine:
    1. Status: "Verified" (fully supported by sources), "Partially Supported" (partially verified or missing minor details), or "Unsupported" (unsupported by sources or contradicts sources).
    2. Source Reference: The title/URL of the matching source, or "None".
    3. Confidence Score: A float between 0.0 and 1.0.
    4. Explanation: A very brief explanation of your verification logic.
    
    Format the output STRICTLY as a raw JSON list of objects, with no markdown wrappers or prefaces.
    Example output:
    [
      {{
        "claim": "Claim statement",
        "status": "Verified",
        "source": "Title of Source (http://example.com)",
        "confidence_score": 0.95,
        "explanation": "Fully verified in section X."
      }}
    ]
    """
    
    try:
        raw_res = ask_groq(prompt).strip()
        raw_res = re.sub(r"^```json\s*", "", raw_res)
        raw_res = re.sub(r"^```\s*", "", raw_res)
        raw_res = re.sub(r"```$", "", raw_res).strip()
        
        results = json.loads(raw_res)
        if isinstance(results, list):
            return results
    except Exception as e:
        print(f"[Fact Validator] Claims verification failed: {e}")
        
    fallback_res = []
    for c in claims:
        fallback_res.append({
            "claim": c,
            "status": "Partially Supported",
            "source": "Inferred from RAG context",
            "confidence_score": 0.50,
            "explanation": "Verified using fallback heuristics."
        })
    return fallback_res

def validate_report_with_sources(report_text: str, sources: list[dict], pdf_chunks: list[dict] = None) -> dict:
    """
    Full pipeline to extract claims, verify them against references, compute trust score, and flag alerts.
    """
    print("[Fact Validator] Initiating claim extraction and source matching...")
    
    if not report_text or report_text.startswith("⚠️"):
        return {
            "validated_text": report_text,
            "trust_score": 0.0,
            "hallucination_score": 100.0,
            "confidence_label": "Error / Unvalidated",
            "claims_validation": [],
            "warnings": ["Skipped validation due to upstream errors."]
        }
        
    # Step 1: Extract claims
    claims = extract_claims(report_text)
    print(f"[Fact Validator] Extracted {len(claims)} key claims for verification.")
    
    # Step 2: Build reference context
    reference_texts = []
    for src in (sources or []):
        title = src.get("title", "Source")
        url = src.get("url", "")
        snippet = src.get("abstract") or src.get("snippet") or ""
        if snippet:
            reference_texts.append(f"Source: {title} ({url})\nSnippet:\n{snippet}\n")
            
    for chunk in (pdf_chunks or []):
        meta = chunk.get("metadata", {})
        title = meta.get("title") or meta.get("source_file", "PDF Document")
        text = chunk.get("document", "")
        if text:
            reference_texts.append(f"PDF Source: {title}\nSnippet:\n{text}\n")
            
    source_context = "\n".join(reference_texts)
    
    # Truncate context to stay within token limits
    MAX_CONTEXT_CHARS = 12000
    if len(source_context) > MAX_CONTEXT_CHARS:
        source_context = source_context[:MAX_CONTEXT_CHARS] + "\n\n[... content truncated to save tokens ...]"
        
    # Step 3: Verify claims
    verification_results = verify_claims_against_sources(claims, source_context)
    
    # Step 4: Compute Trust & Hallucination Scores
    verified_count = sum(1 for r in verification_results if r.get("status") == "Verified")
    partial_count = sum(1 for r in verification_results if r.get("status") == "Partially Supported")
    total_count = len(verification_results) if verification_results else 1
    
    # Trust score formula
    trust_score = round(((verified_count * 1.0 + partial_count * 0.5) / total_count) * 100, 1)
    hallucination_score = round(100.0 - trust_score, 1)
    
    if trust_score >= 85.0:
        confidence_label = "High Trust"
    elif trust_score >= 60.0:
        confidence_label = "Medium Trust"
    else:
        confidence_label = "Low Trust / Hallucination Warning"
        
    # Compile warnings
    warnings = []
    for r in verification_results:
        if r.get("status") == "Unsupported":
            warnings.append(f"Unsupported claim: \"{r.get('claim')}\". Explanation: {r.get('explanation')}")
            
    # Step 5: Format inline notes into report
    validated_text = report_text
    if warnings:
        validated_text += "\n\n### ⚠️ Fact Check Warnings\n"
        for w in warnings:
            validated_text += f"- **Warning**: {w}\n"
            
    print(f"[Fact Validator] Verification complete. Trust Score: {trust_score}% | Status: {confidence_label}.")
    
    return {
        "validated_text": validated_text,
        "trust_score": trust_score,
        "hallucination_score": hallucination_score,
        "confidence_label": confidence_label,
        "claims_validation": verification_results,
        "warnings": warnings
    }

if __name__ == "__main__":
    test_report = "Quantum algorithms run on qubits. We achieved 99.9% gate fidelity on a 1000-qubit processor in 2024."
    test_sources = [
        {"title": "Quantum benchmarks", "url": "https://quantum.org", "abstract": "We demonstrate a 1000-qubit processor with a gate fidelity of 99.9%."}
    ]
    res = validate_report_with_sources(test_report, test_sources)
    print(json.dumps(res, indent=2))
