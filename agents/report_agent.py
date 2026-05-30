import os
import sys
import re

# Ensure project root is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq
from agents.researcher_agent import clean_report_headings

def build_compilation_prompt(validated_research: str, summary: str, critique: str, sources_str: str) -> str:
    """
    Constructs the prompt for report synthesis.
    """
    return f"""You are a Master Report Synthesizer and Academic Editor.
Your job is to take validated research drafts, an executive summary, critic feedback, and citation information, and compile them into a unified, publication-grade, professional research report.

Here is the Executive Summary:
<summary>
{summary}
</summary>

Here is the Quality Critique:
<critique>
{critique}
</critique>

Here is the Validated Research Body:
<research_body>
{validated_research}
</research_body>

Here are the citation sources:
<sources>
{sources_str}
</sources>

### COMPILATION INSTRUCTIONS:
1. Synthesize these inputs into a single, cohesive, logically organized markdown document.
2. The document MUST follow this structure:
   - Document Title (H1)
   - "## Executive Summary" section (H2) containing the distilled summary.
   - Core research chapters (H2) detailing the concepts, applications, advantages, challenges, and future scope.
   - Critique and scoring highlight (incorporating comments on strengths/weaknesses from the Critic).
   - "## References" section containing clean clickable links or references for all sources provided in <sources>.
3. Ensure transitions between sections are smooth, tone is academic and objective, and formatting is clean.
4. STRICT HEADINGS RULE: Main H2 headings MUST use single integers (e.g., '## 1. Executive Summary', '## 2. Core Concepts', etc.).
5. Do NOT include markdown code blocks wrapping the entire report. Output ONLY the compiled markdown report.
"""

def generate_final_report(validated_research: str, summary: str, critique_str: str, sources: list) -> str:
    """
    Synthesizes validated components and references into a final report.
    """
    print("[Report Agent] Generating final comprehensive report...")
    
    if validated_research.startswith("⚠️"):
        return validated_research
        
    # Format sources list
    sources_str = ""
    if sources:
        for idx, src in enumerate(sources, start=1):
            title = src.get("title", f"Source {idx}")
            url = src.get("url", "#")
            sources_str += f"{idx}. {title} ({url})\n"
    else:
        sources_str = "No source references available."
        
    prompt = build_compilation_prompt(validated_research, summary, critique_str, sources_str)
    
    try:
        final_report = ask_groq(prompt).strip()
        
        # Clean markdown code block markers
        final_report = re.sub(r"^```markdown\s*", "", final_report)
        final_report = re.sub(r"^```\s*", "", final_report)
        final_report = re.sub(r"```$", "", final_report).strip()
        
        # Apply standard headings cleaner
        final_report = clean_report_headings(final_report)
        
        print("[Report Agent] Final report compilation complete.")
        return final_report
        
    except Exception as e:
        print(f"[Report Agent Error] Compilation failed: {e}")
        # Fallback combination
        fallback = f"# Research Report (Fallback Comp)\n\n## Executive Summary\n{summary}\n\n## Research Details\n{validated_research}\n\n## References\n{sources_str}"
        return clean_report_headings(fallback)

if __name__ == "__main__":
    print(generate_final_report("Raw facts", "Summary notes", "Good work: 8/10", [{"title": "Source Paper", "url": "https://arxiv.org"}]))
