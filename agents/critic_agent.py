import os
import sys

# Ensure the project root is in the python path to allow importing tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def build_critic_prompt(research_text: str, summary_text: str) -> str:
    """
    Constructs an advanced, structured prompt for the Critic Agent.
    
    Args:
        research_text (str): The full research report to evaluate.
        summary_text (str): The executive summary of the research.
        
    Returns:
        str: The fully constructed prompt for the LLM.
    """
    prompt = f"""You are a Senior AI Research Analyst and Critic. Your objective is to rigorously evaluate an AI-generated research report and its executive summary.

Your core responsibilities:
1. Evaluate the depth, clarity, and completeness of the research.
2. Identify missing topics, concepts, or industry applications.
3. Find weak sections (e.g., shallow explanations, vague transitions).
4. Suggest technical improvements for a stronger structure.
5. Provide an objective score out of 10 (use floats, e.g., 7.5).
6. Do NOT hallucinate. Be objective, highly critical, yet constructive.

Here is the Executive Summary:
<summary>
{summary_text}
</summary>

Here is the Full Research Report:
<research>
{research_text}
</research>

Please generate your critique STRICTLY as a valid JSON object. Do NOT wrap it in markdown code blocks like ```json. Output ONLY the raw JSON object.
Use the following exact schema:

{{
  "score": <float between 1.0 and 10.0>,
  "strengths": [
    "<string>",
    "<string>"
  ],
  "weaknesses": [
    "<string>",
    "<string>"
  ],
  "missing_topics": [
    "<string>",
    "<string>"
  ],
  "improvement_suggestions": [
    "<string>",
    "<string>"
  ],
  "clarity_evaluation": "<string detailed analysis of readability and professional tone>"
}}
"""
    return prompt

import json
import re

def critique_research(research_text: str, summary_text: str) -> dict:
    """
    Main execution function for the Critic Agent.
    
    Args:
        research_text (str): The extensive research data.
        summary_text (str): The executive summary.
        
    Returns:
        dict: The structured JSON critique. If an error occurs, returns a dict with 'error'.
    """
    print("[Critic Agent] Initializing critique of research report and summary...")

    # --- Guard: propagate upstream errors cleanly without wasting tokens ---
    if research_text.startswith("⚠️") or summary_text.startswith("⚠️"):
        print("[Critic Agent] Upstream agent error detected — skipping critique.")
        error_msg = research_text if research_text.startswith("⚠️") else summary_text
        return {"error": error_msg}

    # --- Token budget: cap both inputs to avoid exceeding the daily quota ---
    MAX_RESEARCH_CHARS = 100_000
    MAX_SUMMARY_CHARS  = 20_000
    if len(research_text) > MAX_RESEARCH_CHARS:
        research_text = research_text[:MAX_RESEARCH_CHARS] + "\n\n[... truncated for token budget ...]"
    if len(summary_text) > MAX_SUMMARY_CHARS:
        summary_text = summary_text[:MAX_SUMMARY_CHARS] + "\n\n[... truncated for token budget ...]"
    
    # 1. Construct the specialized prompt
    prompt = build_critic_prompt(research_text, summary_text)
    
    # 2. Call the LLM via our centralized Groq client
    try:
        critique_result_str = ask_groq(prompt).strip()
        
        # Clean up any potential markdown code blocks the LLM might have output despite instructions
        critique_result_str = re.sub(r"^```json\s*", "", critique_result_str)
        critique_result_str = re.sub(r"^```\s*", "", critique_result_str)
        critique_result_str = re.sub(r"```$", "", critique_result_str).strip()
        
        critique_json = json.loads(critique_result_str)
        print(f"[Critic Agent] Critique successfully generated. Score: {critique_json.get('score', 'N/A')}/10")
        return critique_json
    except json.JSONDecodeError as e:
        print(f"[Critic Agent Error] Failed to parse JSON. Raw output: {critique_result_str[:200]}...")
        return {"error": f"Failed to parse JSON critique: {str(e)}"}
    except Exception as e:
        print(f"[Critic Agent Error] Failed to generate critique. Details: {str(e)}")
        return {"error": f"⚠️ **Critic Agent Error:** {str(e)}"}

# ==========================================
# Debug/Testing Block
# ==========================================
if __name__ == "__main__":
    sample_research = "Quantum Machine Learning (QML) is an emerging field..."
    sample_summary = "QML combines quantum computing and machine learning..."
    
    print("--- Running Critic Agent Test ---")
    result = critique_research(sample_research, sample_summary)
    print("\n" + "="*40 + "\n")
    print(result)
    print("\n" + "="*40 + "\n")
