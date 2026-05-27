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

Decompose this topic intelligently into logical, sequential research phases. Identify the critical focus areas, core subtopics, and potential challenges.
Avoid duplicate subtopics. Ensure a logical progression from fundamentals to advanced concepts.

You MUST return your output STRICTLY as a valid JSON object matching the schema below. Do not wrap it in markdown code blocks like ```json.
Output ONLY the raw JSON object.

{{
    "overview": "<string: brief summary of what the research must accomplish>",
    "objectives": [
        "<string: objective 1>",
        "<string: objective 2>"
    ],
    "roadmap": [
        "<string: Phase 1 description>",
        "<string: Phase 2 description>"
    ],
    "subtopics": [
        "<string: Core Subtopic 1 (e.g., Fundamentals)>",
        "<string: Core Subtopic 2>",
        "<string: Core Subtopic 3>"
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
        "<string: key question to answer>"
    ],
    "focus_areas": [
        "<string: area to prioritize>"
    ],
    "potential_challenges": [
        "<string: hurdle in research or adoption>"
    ],
    "future_opportunities": [
        "<string: future trajectory>"
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
