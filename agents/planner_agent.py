import os
import sys
import json
import re

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def build_planner_prompt(topic: str) -> str:
    """
    Constructs an advanced prompt for the Planner Agent to decompose a research topic.
    """
    return f"""You are a Master Strategic Research Planner. Your objective is to architect a highly structured, professional research roadmap before downstream agents begin their investigations.

Topic to Analyze: "{topic}"

Decompose this topic intelligently into logical, sequential research phases. Identify the critical focus areas, core subtopics, analytical angles to investigate, and potential challenges.
Avoid duplicate subtopics. Ensure a logical progression from fundamentals to advanced concepts.
Think like a senior research director commissioning a professional analyst report — the goal is INSIGHT, not just description.

You MUST return your output STRICTLY as a valid JSON object matching the schema below. Do not wrap it in markdown code blocks like ```json.
Output ONLY the raw JSON object.

{{
    "overview": "<string: brief summary of what the research must accomplish and WHY it matters>",
    "objectives": [
        "<string: objective 1 — analytical goal, not just 'understand X'>",
        "<string: objective 2>"
    ],
    "roadmap": [
        "<string: Phase 1 description>",
        "<string: Phase 2 description>"
    ],
    "subtopics": [
        "<string: Core Subtopic 1 (e.g., Fundamentals & Mechanisms)>",
        "<string: Core Subtopic 2>",
        "<string: Core Subtopic 3>"
    ],
    "analytical_angles": [
        "<string: A comparative or causal angle to investigate, e.g., 'Traditional rule-based approaches vs modern ML-driven approaches'>",
        "<string: Another analytical angle, e.g., 'Impact of GPU hardware scaling on model capability'>",
        "<string: Another analytical angle, e.g., 'Open-source vs proprietary ecosystem trade-offs'>"
    ],
    "insight_targets": [
        "<string: Most Important Recent Development — identify and analyze>",
        "<string: Most Significant Strategic Opportunity — identify and analyze>",
        "<string: Most Critical Limitation or Risk — identify and analyze>",
        "<string: Most Important Emerging Trend — identify and analyze>",
        "<string: Most Relevant Research Gap — identify and analyze>"
    ],
    "technical_areas": [
        "<string: technical concept 1>",
        "<string: technical concept 2>"
    ],
    "suggested_order": [
        "<string: Step 1>",
        "<string: Step 2>"
    ],
    "critical_questions": [
        "<string: A key analytical question the research MUST answer>"
    ],
    "focus_areas": [
        "<string: area to prioritize for deep analysis>"
    ],
    "potential_challenges": [
        "<string: hurdle in research or adoption>"
    ],
    "future_opportunities": [
        "<string: specific future trajectory with reasoning>"
    ]
}}
"""

def generate_plan(topic: str) -> dict:
    """
    Main execution function for the Planner Agent.
    
    Args:
        topic (str): The subject to be planned.
        
    Returns:
        dict: A structured dictionary containing the roadmap. Returns None if planning fails.
    """
    print(f"\n[Planner Agent] Analyzing research topic: '{topic}'...")
    
    prompt = build_planner_prompt(topic)
    
    try:
        print("[Planner Agent] Generating investigation roadmap...")
        plan_str = ask_groq(prompt).strip()
        
        if plan_str.startswith("⚠️"):
            print("[Planner Agent Error] Upstream quota error detected.")
            return None
            
        # Clean up possible markdown wrappers
        plan_str = re.sub(r"^```json\s*", "", plan_str)
        plan_str = re.sub(r"^```\s*", "", plan_str)
        plan_str = re.sub(r"```$", "", plan_str).strip()
        
        plan_json = json.loads(plan_str)
        print("[Planner Agent] Research phases created successfully.")
        return plan_json
        
    except json.JSONDecodeError as e:
        print(f"[Planner Agent Error] Failed to parse JSON roadmap: {e}")
        return None
    except Exception as e:
        print(f"[Planner Agent Error] Failed to generate plan: {e}")
        return None

if __name__ == "__main__":
    test_topic = "AI in Healthcare"
    plan = generate_plan(test_topic)
    if plan:
        print(json.dumps(plan, indent=2))
