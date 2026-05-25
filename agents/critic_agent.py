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
5. Analyze clarity, readability, and professional tone.
6. Provide an objective score out of 10 with a brief justification.
7. Do NOT hallucinate. Be objective, highly critical, yet constructive.

Here is the Executive Summary:
<summary>
{summary_text}
</summary>

Here is the Full Research Report:
<research>
{research_text}
</research>

Please generate your critique STRICTLY following the format below. Use markdown headers:

# AI Critic Analysis

## Overall Research Quality
[Evaluate depth, clarity, completeness, technical quality, and professionalism]

## Missing Topics
[Identify missing concepts, ignored trends, missing industry applications, and absent technical details]

## Weak Sections
[Find shallow explanations, repetitive content, vague sections, poor transitions]

## Technical Improvements
[Suggest deeper technical analysis, better examples, stronger structure, and improved research logic]

## Clarity Evaluation
[Analyze readability, formatting, organization, and professional tone]

## Suggested Enhancements
[Provide actionable recommendations, future additions, and advanced improvements]

## Final Review Score
[Generate a score out of 10 and provide a brief justification]

Ensure your tone is objective, professional, and analytical. Only output the requested sections. Do not include any conversational filler text.
"""
    return prompt

def critique_research(research_text: str, summary_text: str) -> str:
    """
    Main execution function for the Critic Agent.
    
    Args:
        research_text (str): The extensive research data.
        summary_text (str): The executive summary.
        
    Returns:
        str: The structured, concise markdown critique.
    """
    print("[Critic Agent] Initializing critique of research report and summary...")
    
    # 1. Construct the specialized prompt
    prompt = build_critic_prompt(research_text, summary_text)
    
    # 2. Call the LLM via our centralized Groq client
    try:
        critique_result = ask_groq(prompt)
        print("[Critic Agent] Critique successfully generated.")
        return critique_result
    except Exception as e:
        print(f"[Critic Agent Error] Failed to generate critique. Details: {str(e)}")
        return f"Error generating critique: {str(e)}"

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
