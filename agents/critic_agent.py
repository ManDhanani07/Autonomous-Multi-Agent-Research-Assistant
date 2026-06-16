import os
import sys

# Ensure the project root is in the python path to allow importing tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def build_critic_prompt(research_text: str, summary_text: str, topic: str = "", previous_critique: dict = None) -> str:
    """
    Constructs an advanced, structured prompt for the Critic Agent with scoring rubrics,
    topic-aware expected coverage checks, and upgraded JSON schema.
    """
    topic_context = ""
    if topic:
        topic_context = f"\nResearch Topic Requested: \"{topic}\"\n"

    refinement_context = ""
    if previous_critique:
        prev_score = previous_critique.get("score", "N/A")
        prev_weaknesses = "\n- ".join(previous_critique.get("weaknesses", []))
        prev_missing = "\n- ".join(previous_critique.get("missing_research_areas", previous_critique.get("missing_areas", [])))
        
        refinement_context = f"""
### REFINE EVALUATION CONTEXT (COMPARATIVE CRITIQUE) ###
This report is a refined/optimized draft of a previous version that scored {prev_score}/10.
The previous draft had the following identified gaps:
Weaknesses to fix:
- {prev_weaknesses}
Missing topics to integrate:
- {prev_missing}

Compare the new report against the previous gaps. If the author successfully addressed the weaknesses and missing topics, you should reward their effort by increasing the score accordingly (moving it up into the 8.5 to 10.0 range if resolved with high research quality).
"""

    prompt = f"""You are a Senior AI Research Analyst and Critic. Your objective is to rigorously evaluate an AI-generated research report and its executive summary.
{topic_context}
Your core responsibilities:
1. **Topic-Aware Expected Coverage Analysis**:
   - Deduce the standard academic/industry subtopics that a comprehensive report on "{topic}" must cover. For example, if the topic is "Artificial Intelligence & Deep Learning", expected topics include Neural Networks, CNNs, RNNs, Transformers, Attention Mechanisms, LLMs, Reinforcement Learning, Optimization, and Applications.
   - Contrast the report content and subtopics against this list. Every missing expected topic must be reported in `missing_research_areas`.
2. **Specific Content Evaluation**:
   - Evaluate the depth, clarity, and completeness of the research.
   - Do NOT repeat or summarize the research content. Focus strictly on evaluating the research quality.
   - All comments in `strengths`, `weaknesses`, `missing_research_areas`, and `improvement_priorities` must be derived from actual report content, referencing specific topics, methods, or sections. Avoid generic feedback or boilerplate phrases.
3. **Scoring and Suitability Verdict**:
   - Provide an objective overall score out of 10 (use floats, e.g., 7.5).
   - Evaluate coverage of each major section individually (e.g. Introduction, Core Concepts, Technical Depth, Applications, Challenges, Future Outlook) and provide scores.
   - Determine suitability of this report (students, professionals, researchers, publication-level work).
4. Do NOT hallucinate. Be objective, highly critical, yet constructive.

### SCORING RUBRICS ###
- **9.0 - 10.0 (Exceptional)**: Technically complete, covers all critical aspects of the topic with outstanding depth and clear academic structure. No major gaps or missing topics.
- **8.0 - 8.9 (Very Good)**: High quality, covers all main areas, but has minor suggestions for structural polishing or minor formatting improvements.
- **7.0 - 7.9 (Good / Average)**: Solid effort, but has noticeable gaps (e.g. missing sections, shallow explanations of core principles, or lack of references).
- **Below 7.0 (Needs Improvement)**: Major gaps in content, incorrect facts, or poorly structured.
{refinement_context}
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
  "research_grade": "<string: Excellent / Very Good / Good / Fair / Poor>",
  "coverage_analysis": {{
    "Introduction": "<string: e.g. 9/10 - specific comment on introduction coverage>",
    "Core Concepts": "<string: e.g. 8/10 - specific comment on core concepts coverage>",
    "Technical Depth": "<string: e.g. 7/10 - specific comment on technical depth coverage>",
    "Applications": "<string: e.g. 9/10 - specific comment on applications coverage>",
    "Challenges": "<string: e.g. 8/10 - specific comment on challenges coverage>",
    "Future Outlook": "<string: e.g. 8/10 - specific comment on future outlook coverage>"
  }},
  "strengths": [
    "<string strength 1 - referencing actual topics found in the report>",
    "<string strength 2 - referencing actual topics found in the report>"
  ],
  "weaknesses": [
    "<string weakness 1 - referencing actual missing depth or poor coverage found in the report>",
    "<string weakness 2 - referencing actual missing depth or poor coverage found in the report>"
  ],
  "missing_research_areas": [
    "<string missing expected subtopic 1>",
    "<string missing expected subtopic 2>"
  ],
  "improvement_priorities": {{
    "High Priority": [
      "<string high priority recommendation 1>",
      "<string high priority recommendation 2>"
    ],
    "Medium Priority": [
      "<string medium priority recommendation 1>"
    ],
    "Low Priority": [
      "<string low priority recommendation 1>"
    ]
  }},
  "confidence_level": "<string: e.g. High / Medium / Low>",
  "final_verdict": "<string final judgment explaining suitability for students, professionals, researchers, or publication-level work>"
}}
"""
    return prompt

import json
import re

def critique_research(research_text: str, summary_text: str, topic: str = "", previous_critique: dict = None) -> dict:
    """
    Main execution function for the Critic Agent.
    
    Args:
        research_text     (str):  The extensive research data.
        summary_text      (str):  The executive summary.
        topic             (str):  The original research topic.
        previous_critique (dict): Feedback dictionary from a previous loop iteration.
        
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
    prompt = build_critic_prompt(research_text, summary_text, topic, previous_critique)
    
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
