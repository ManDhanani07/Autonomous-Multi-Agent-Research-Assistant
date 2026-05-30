import os
import sys
import re

# Ensure project root is in the Python path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def build_validation_prompt(raw_research_data: str) -> str:
    """
    Constructs the prompt for the Fact Validation Agent.
    """
    return f"""You are an elite AI Fact Validation Agent. Your goal is to review, verify, and clean draft research reports before they are synthesized into a final report.

Your responsibilities:
1. Identify any contradictory claims between different sections (e.g. if one section says X is impossible and another says X was achieved).
2. Scan for unverified statistical claims, vague generalizations, or obvious hallucinations (e.g. referencing non-existent models or fabricated figures).
3. If errors or contradictions are found, resolve them logically or flag them with clear inline validation notes: "[FACT CHECK: Resolved X to Y]".
4. Return a consolidated, factually validated, and clean markdown text merging all drafts.
5. Keep the content highly technical, academic, and detailed. Do NOT summarize or shorten the research. Preserve all useful information.

Here is the draft research text to validate:
<draft_research>
{raw_research_data}
</draft_research>

Please produce the consolidated, verified markdown report. Output ONLY the validated markdown content. Do not include conversational prefaces or conclusions.
"""

def validate_research_facts(subtopic_reports: list[dict]) -> str:
    """
    Consolidates subtopic drafts and runs fact validation.
    
    Args:
        subtopic_reports (list[dict]): A list of dicts, each with 'subtopic' and 'report' keys.
        
    Returns:
        str: Factually validated consolidated research report.
    """
    print("[Fact Validation Agent] Consolidating and validating parallel research drafts...")
    
    if not subtopic_reports:
        return "⚠️ Error: No research drafts provided for validation."
        
    # Combine drafts with subtopic markers
    combined_drafts = ""
    for idx, item in enumerate(subtopic_reports, start=1):
        sub = item.get("subtopic", f"Subtopic {idx}")
        rep = item.get("report", "")
        combined_drafts += f"\n\n=== DRAFT: {sub} ===\n{rep}\n"
        
    # Guard against upstream error propagation
    if "⚠️" in combined_drafts:
        print("[Fact Validation Agent] Upstream errors detected in drafts. Skipping validation.")
        return combined_drafts
        
    # Token budget: truncate if extremely long
    MAX_INPUT_CHARS = 10_000
    if len(combined_drafts) > MAX_INPUT_CHARS:
        combined_drafts = combined_drafts[:MAX_INPUT_CHARS] + "\n\n[... truncated for validation budget ...]"
        
    prompt = build_validation_prompt(combined_drafts)
    
    try:
        validated_report = ask_groq(prompt).strip()
        
        # Clean potential markdown wrappers
        validated_report = re.sub(r"^```markdown\s*", "", validated_report)
        validated_report = re.sub(r"^```\s*", "", validated_report)
        validated_report = re.sub(r"```$", "", validated_report).strip()
        
        print("[Fact Validation Agent] Consolidation and verification complete.")
        return validated_report
    except Exception as e:
        print(f"[Fact Validation Agent Error] Validation loop failed. Details: {e}")
        return f"⚠️ **Fact Validation Agent Error:** {e}\n\nFallback Raw Drafts:\n{combined_drafts}"

if __name__ == "__main__":
    test_drafts = [
        {"subtopic": "Introduction to QML", "report": "QML runs on quantum computers. It achieves 1000x speedup today."},
        {"subtopic": "QML Challenges", "report": "Quantum computer hardware is highly noisy and no actual commercial speedup is currently demonstrated."}
    ]
    print(validate_research_facts(test_drafts))
