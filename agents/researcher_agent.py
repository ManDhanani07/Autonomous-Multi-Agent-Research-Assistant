"""
Researcher Agent Module
This module provides a professional AI Researcher Agent for generating 
structured and comprehensive research reports using the Groq API.
Designed to be modular and easily integrated into larger multi-agent frameworks like CrewAI or LangGraph.
"""

import os
import sys

# Add the project root to the Python path so it can find the 'tools' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq
from tools.web_search_tool import search_web, format_search_results
from tools.browser_tool import scrape_article

def create_research_prompt(topic: str, web_context: str = "") -> str:
    """
    Constructs an advanced, highly-engineered system prompt for the Groq model.
    This prompt enforces a strict professional structure and high-quality markdown output.
    
    Args:
        topic (str): The subject of the research.
        web_context (str): Real-time web search results to integrate.
        
    Returns:
        str: The fully constructed prompt string.
    """
    prompt = f"""
You are an elite AI Research Scientist and Technical Analyst. Your task is to provide a comprehensive, 
highly accurate, and professional research report on the following topic:

Topic: "{topic}"
"""

    if web_context:
        prompt += f"""
{web_context}
"""

    prompt += f"""
Please generate a detailed, structured markdown report. You must follow the exact structure outlined below, 
using professional headings, bullet points where appropriate for readability, and concise but deeply technical explanations.

**Required Report Structure:**

# Research Report: {topic}

## 1. Introduction
Provide a clear, high-level overview of the topic. What is it, why is it important, and what is its current relevance in the industry?

## 2. Core Concepts
Explain the fundamental principles, underlying technologies, or key theories related to the topic. Break down complex ideas into understandable professional terms.

## 3. Applications
List and describe the primary real-world use cases and industry applications. Use bullet points for clarity.

## 4. Advantages
What are the main benefits, efficiencies, or positive impacts? Highlight why organizations or individuals adopt this.

## 5. Challenges
Discuss the current limitations, technical hurdles, ethical concerns, or adoption barriers. Be objective and factual.

## 6. Future Scope
Analyze the future trajectory, upcoming innovations, and long-term potential of this topic over the next 5-10 years.

## 7. Conclusion
Summarize the key takeaways in a powerful concluding paragraph.

**Output Constraints:**
- Use clean and visually appealing Markdown formatting.
- Ensure the tone is objective, academic yet accessible, and highly professional.
- Do not include any conversational filler (e.g., "Here is the report"). Begin directly with the Markdown title.
"""
    return prompt.strip()

def generate_research(topic: str) -> str:
    """
    Generates a professional research report by orchestrating the prompt creation and API call.
    
    Args:
        topic (str): The research subject.
        
    Returns:
        str: The AI-generated markdown report.
    """
    if not topic:
        return "Error: Please provide a valid research topic."
        
    # Step 1: Collect live web data search results
    web_results = search_web(topic)
    web_context = format_search_results(web_results)
    
    # Step 2: Open top 2 articles and scrape their contents
    deep_context = ""
    scraped_count = 0
    
    if web_results:
        # We only scrape the top 2 results to stay within context windows and keep execution fast
        for r in web_results[:2]:
            url = r.get("url")
            if url and url.startswith("http"):
                print(f"[*] Deep Research: Launching browser to scrape content from: {url}")
                article_text = scrape_article(url)
                if article_text:
                    deep_context += f"--- Deep Web Source: {r['title']} ({url}) ---\n"
                    # Limit the scraped content to the first 3000 characters to prevent prompt bloat
                    deep_context += f"{article_text[:3000]}\n"
                    deep_context += "-" * 50 + "\n\n"
                    scraped_count += 1
                    
        print(f"[*] Deep Research: Successfully gathered detailed context from {scraped_count} webpages.")
        
    if deep_context:
        web_context += "\n### DEEP SCRAPED WEB PAGE CONTENT ###\n"
        web_context += "The following are actual detailed readable sections scraped from the top web results. Use this detailed data to write highly specific, factual sections:\n\n"
        web_context += deep_context
        
    print(f"[*] Compiling research parameters for: {topic}...")
    # Step 3: Combine it with Groq LLM reasoning
    prompt = create_research_prompt(topic, web_context)
    
    print("[*] Transmitting request to Groq AI engine...")
    # Call the reusable ask_groq function from our tools module
    report = ask_groq(prompt)
    
    return report

# For standalone testing of the agent
if __name__ == "__main__":
    print("=== Researcher Agent Initialization ===")
    test_topic = input("Enter a topic to research: ").strip()
    
    if test_topic:
        print("\n" + "="*60)
        output = generate_research(test_topic)
        print("="*60)
        print("\n" + output + "\n")
        print("="*60)
    else:
        print("Agent execution cancelled: No topic provided.")
