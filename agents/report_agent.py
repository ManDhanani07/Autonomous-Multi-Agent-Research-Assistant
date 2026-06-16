import os
import sys
import re

# Ensure project root is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq
from agents.researcher_agent import clean_report_headings

import json

def build_compilation_prompt(validated_research: str, summary: str, critique_dict: dict, sources_str: str, academic_count: int, web_count: int) -> str:
    """
    Constructs the prompt for report synthesis.
    """
    score = critique_dict.get("score", "N/A")
    grade = critique_dict.get("research_grade", "N/A")
    confidence = critique_dict.get("confidence_level", "N/A")
    verdict = critique_dict.get("final_verdict", "N/A")

    coverage_dict = critique_dict.get("coverage_analysis", {})
    if isinstance(coverage_dict, dict):
        coverage = "\n".join([f"- **{sec}**: {val}" for sec, val in coverage_dict.items()])
    else:
        coverage = str(coverage_dict)

    strengths = "\n".join([f"- {s}" for s in critique_dict.get("strengths", [])]) if critique_dict.get("strengths") else "- None noted."
    weaknesses = "\n".join([f"- {w}" for w in critique_dict.get("weaknesses", [])]) if critique_dict.get("weaknesses") else "- None noted."
    
    missing_list = critique_dict.get("missing_research_areas", critique_dict.get("missing_areas", critique_dict.get("missing_topics", [])))
    missing_areas = "\n".join([f"- {m}" for m in missing_list]) if missing_list else "- None noted."
    
    imp_priorities = critique_dict.get("improvement_priorities", {})
    if isinstance(imp_priorities, dict) and imp_priorities:
        priorities_list = []
        for prio, items in imp_priorities.items():
            if isinstance(items, list):
                for item in items:
                    priorities_list.append(f"- **{prio}**: {item}")
            elif isinstance(items, str):
                priorities_list.append(f"- **{prio}**: {items}")
        suggestions = "\n".join(priorities_list) if priorities_list else "- None noted."
    else:
        suggestions = "\n".join([f"- {i}" for i in critique_dict.get("improvement_recommendations", critique_dict.get("improvement_suggestions", []))]) if critique_dict.get("improvement_recommendations") or critique_dict.get("improvement_suggestions") else "- None noted."

    return f"""You are a Master Report Synthesizer and Academic Editor.
Your job is to take validated research drafts, an executive summary, critic feedback, and citation information, and compile them into a unified, publication-grade, professional research report.

Here is the Executive Summary:
<summary>
{summary}
</summary>

Here is the Quality Critique:
<critique>
Score: {score}/10
Research Grade: {grade}
Coverage Analysis:
{coverage}
Strengths:
{strengths}
Weaknesses:
{weaknesses}
Missing Research Areas:
{missing_areas}
Improvement Priorities:
{suggestions}
Confidence Level: {confidence}
Final Verdict: {verdict}
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
2. The document MUST follow EXACTLY this H2 section structure. You must rewrite, expand, and structure the research body and summary data into these 13 numbered H2 sections in order:

## 1. Executive Summary
- Brief overview of the topic
- Main findings
- Key conclusions
- Important recommendations

## 2. Introduction
- Topic background
- Problem statement
- Research objectives
- Scope of study
- Importance of the topic

## 3. Research Methodology
- Detail the sources used
- Academic papers analyzed
- Web sources reviewed
- Research approach and data collection methods

## 4. Core Concepts & Foundations
- Key definitions
- Fundamental theories
- Technical background
- Important terminology

## 5. Current State of the Field
- Latest developments
- Industry trends
- Recent breakthroughs
- Current implementations

## 6. Detailed Technical Analysis
- Deep technical discussion
- Comparative analysis (Traditional vs Modern approaches with a comparison table where applicable)
- Multiple perspectives and competing approaches
- Supporting evidence and key observations
- Causal analysis: WHY the field is evolving as it is

## 7. Applications & Use Cases
- Real-world applications in structured format per industry (Current Usage / Business Value / Adoption Status / Future Potential)
- Industry adoption case studies
- Success stories and measurable outcomes

## 8. Advantages & Opportunities
- Main benefits with causal explanations
- Strategic positioning opportunities
- Competitive moats and first-mover advantages
- Economic implications

## 9. Challenges & Limitations
- Technical limitations with root-cause analysis
- Risks and adoption barriers
- Ethical and regulatory concerns

## 10. Future Outlook
- Short-Term (1–2 Years): expected developments, near-term risks
- Medium-Term (3–5 Years): maturation points, transformation potential
- Long-Term (5–10 Years): paradigm shifts, speculative scenarios

## 11. Key Insights & Strategic Findings
Present the top 5 strategic insights in this exact format for each:
**Insight [N]: [Title]**
- **Observation:** [Specific finding]
- **Impact:** [Strategic implication]
- **Evidence:** [Grounded in research]

## 12. Expert Recommendations
Present targeted, actionable recommendations for each of these audiences:
- **For Researchers:** Top open problems and methodological guidance
- **For Businesses & Decision-Makers:** Adoption timing, risk management, KPIs
- **For Engineers & Developers:** Best practices, tools, technical pitfalls
- **For Policy Makers:** Regulatory gaps, governance frameworks, competitiveness

## 13. Conclusion
- Final assessment
- Summary of findings
- Research objectives achieved
- Overall significance

## 14. References & Source Summary
Academic Papers Reviewed: {academic_count}
Web Sources Analyzed: {web_count}
Research Databases Used: Semantic Scholar, arXiv, CrossRef

### Cited References
Using ONLY the sources provided below, render each as a numbered markdown clickable link in this exact format:
[N]. [Title of Paper or Article](URL)

Sources to render as clickable links:
{sources_str}

IMPORTANT: Do NOT invent, modify, or fabricate any URLs. Every link must use the exact URL provided. Render ALL provided sources as clickable links.

3. Ensure transitions between sections are smooth, tone is academic and objective, and formatting is clean.
4. STRICT HEADING NUMBERING: Number the main H2 headings exactly as '## 1. Executive Summary', '## 2. Introduction', etc. NEVER write subheadings as '## 1.1', '## 1.0', or '## 2.0'. H2 headings must use only integers: 1 to 14.
5. Do NOT include markdown code blocks wrapping the entire report. Output ONLY the compiled markdown report.
"""

def generate_final_report(validated_research: str, summary: str, critique_str: any, sources: list) -> str:
    """
    Synthesizes validated components and references into a final report.
    """
    print("[Report Agent] Generating final comprehensive report...")
    
    if validated_research.startswith("⚠️"):
        return validated_research
        
    # Ensure critique is treated as a dict
    critique_dict = {}
    if isinstance(critique_str, dict):
        critique_dict = critique_str
    elif isinstance(critique_str, str):
        # Try parsing it as JSON just in case
        try:
            critique_dict = json.loads(critique_str)
        except Exception:
            score_match = re.search(r"Score:\s*([\d\.]+)", critique_str)
            score = score_match.group(1) if score_match else "N/A"
            critique_dict = {
                "score": score,
                "research_grade": "N/A",
                "coverage_analysis": {},
                "strengths": [critique_str] if critique_str else [],
                "weaknesses": [],
                "missing_research_areas": [],
                "improvement_priorities": {},
                "confidence_level": "N/A",
                "final_verdict": "N/A"
            }
    elif critique_str is None:
        critique_dict = {}

    # Count unique academic and web sources
    academic_sources = [s for s in sources if s.get("type") in ["academic", "pdf"]]
    web_sources = [s for s in sources if s.get("type") == "web"]
    
    academic_count = len(academic_sources)
    web_count = len(web_sources)

    # Format sources list (limit list to top 10 for references to keep bibliography clean)
    sources_str = ""
    sliced_sources = sources[:10]
    if sliced_sources:
        for idx, src in enumerate(sliced_sources, start=1):
            title = src.get("title", f"Source {idx}")
            url = src.get("url", "#")
            sources_str += f"{idx}. {title} ({url})\n"
    else:
        sources_str = "No source references available."
        
    prompt = build_compilation_prompt(validated_research, summary, critique_dict, sources_str, academic_count, web_count)
    
    try:
        # Use 8000 tokens — the final 15-section compiled report needs full headroom
        final_report = ask_groq(prompt, max_tokens=8000).strip()
        
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
    print(generate_final_report("Raw facts", "Summary notes", {"score": 8.0, "strengths": ["Good work"]}, [{"title": "Source Paper", "url": "https://arxiv.org", "type": "academic"}]))
