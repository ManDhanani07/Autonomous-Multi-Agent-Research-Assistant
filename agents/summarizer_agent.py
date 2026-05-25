import os
import sys

# Ensure the project root is in the python path to allow importing tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq

def build_summarizer_prompt(research_text: str) -> str:
    """
    Constructs an advanced, structured prompt for the Summarizer Agent.
    
    This function isolates the prompt engineering logic, making the agent
    modular and easy to integrate into future multi-agent workflows 
    (like CrewAI or AutoGen).
    
    Args:
        research_text (str): The raw text that needs to be summarized.
        
    Returns:
        str: The fully constructed prompt for the LLM.
    """
    prompt = f"""You are an elite AI Summarization Agent. Your objective is to analyze a comprehensive research report and distill it into a highly concise, professional summary. 

Your core responsibilities:
1. Analyze the full research report thoroughly.
2. Extract the most critical insights.
3. Remove fluff, repetitive information, and unnecessary details.
4. Preserve important technical context and accuracy.
5. Do NOT hallucinate or inject external information.

Here is the raw research text:
<research_text>
{research_text}
</research_text>

Please generate your summary STRICTLY following the format below. Use markdown headers:

## Executive Summary
[Provide a high-level, impactful 2-3 paragraph overview of the entire report.]

## Key Findings
* [Bullet point 1]
* [Bullet point 2]
* [Bullet point 3]

## Important Technologies
* [List the core tools, algorithms, or platforms mentioned]

## Main Challenges
* [Outline the primary obstacles, limitations, or risks discussed]

## Future Opportunities
* [Highlight future directions, implications, or areas for growth]

Ensure your tone is objective, professional, and beginner-friendly yet technically accurate. Only output the requested sections. Do not include any conversational filler text.
"""
    return prompt

def summarize_research(research_text: str) -> str:
    """
    Main execution function for the Summarizer Agent.
    
    This function takes a long research report, processes it through the 
    Llama 3.3 70B model via the Groq API, and returns a cleanly formatted summary.
    
    Args:
        research_text (str): The extensive research data to be summarized.
        
    Returns:
        str: The structured, concise markdown summary.
    """
    print("[Summarizer Agent] Initializing analysis of research report...")
    
    # 1. Construct the specialized prompt
    prompt = build_summarizer_prompt(research_text)
    
    # 2. Call the LLM via our centralized Groq client
    try:
        summary_result = ask_groq(prompt)
        print("[Summarizer Agent] Summary successfully generated.")
        return summary_result
    except Exception as e:
        print(f"[Summarizer Agent Error] Failed to generate summary. Details: {str(e)}")
        return f"Error generating summary: {str(e)}"

# ==========================================
# Debug/Testing Block
# ==========================================
if __name__ == "__main__":
    # A small sample text to test the agent locally
    sample_research = """
    Quantum Machine Learning (QML) is an emerging interdisciplinary research area at the intersection of quantum physics and machine learning. 
    The primary goal is to leverage quantum computing to process data and solve machine learning tasks faster than classical computers. 
    Recent advancements in quantum hardware, such as IBM's Eagle processor, have allowed researchers to test variational quantum algorithms. 
    However, the field faces significant challenges, including quantum decoherence, high error rates, and the lack of fault-tolerant qubits. 
    Despite this, future opportunities are vast, particularly in areas like drug discovery, financial modeling, and complex system simulation, 
    where classical computers struggle with exponential scaling. Researchers are actively working on quantum error correction protocols 
    to make these algorithms commercially viable by the next decade.
    """
    
    print("--- Running Summarizer Agent Test ---")
    result = summarize_research(sample_research)
    print("\n" + "="*40 + "\n")
    print(result)
    print("\n" + "="*40 + "\n")
