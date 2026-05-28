"""
Researcher Agent Module — RAG-Enhanced Edition
===============================================
Generates structured, comprehensive research reports using the Groq API.
Now features full Retrieval-Augmented Generation (RAG):
  - Semantic memory retrieval BEFORE research generation
  - Retrieved context injected into the LLM prompt
  - Final report stored back into memory after generation
  - Backward-compatible: returns a dict with 'report' and 'memories' keys

Pipeline:
  User Topic
      ↓
  [Memory Retrieval]  ← retrieve_similar_research via search_memory_context
      ↓
  [Web Search]        ← DuckDuckGo search_web
      ↓
  [Browser Scraping]  ← scrape_article for top 2 results
      ↓
  [Prompt Assembly]   ← memory context + web context + instructions
      ↓
  [Groq Generation]   ← ask_groq with full combined context
      ↓
  Return {"report": str, "memories": list}
"""

import os
import sys

# Add the project root to the Python path so it can find the 'tools' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.groq_client import ask_groq
from tools.web_search_tool import search_web, format_search_results
from tools.browser_tool import scrape_article


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Engineering
# ─────────────────────────────────────────────────────────────────────────────

def create_research_prompt(topic: str,
                            web_context: str = "",
                            source_urls: list = None,
                            memory_context: str = "",
                            plan: dict = None) -> str:
    """
    Constructs the full LLM prompt combining:
      1. Retrieved semantic memory (RAG context)
      2. Live web search results
      3. Deep-scraped article content
      4. Structured report requirements

    Args:
        topic          (str):  The research subject.
        web_context    (str):  Formatted web search + scraped content.
        source_urls    (list): [{title, url}] for the References section.
        memory_context (str):  RAG context block from past research sessions.
        plan           (dict): The Planner Agent's JSON roadmap.

    Returns:
        str: The fully assembled prompt string.
    """
    prompt = (
        "You are an elite AI Research Scientist and Technical Analyst. "
        "Your task is to produce a comprehensive, highly accurate, and professional "
        "research report on the following topic:\n\n"
        f'Topic: "{topic}"\n'
    )

    # ── Inject RAG memory context ──────────────────────────────────────────
    if memory_context:
        prompt += f"\n{memory_context}\n"

    # ── Inject live web data ───────────────────────────────────────────────
    if web_context:
        prompt += f"\n{web_context}\n"

    # ── Build the References block ─────────────────────────────────────────
    references_block = ""
    if source_urls:
        references_block = "\n## 8. References\n"
        for i, src in enumerate(source_urls, start=1):
            title = src.get("title", f"Source {i}")
            url   = src.get("url", "#")
            references_block += f"{i}. [{title}]({url})\n"

    # ── Inject Planner Guidance ───────────────────────────────────────────
    if plan and isinstance(plan, dict):
        objectives = "\n- ".join(plan.get('objectives', []))
        subtopics = "\n- ".join(plan.get('subtopics', []))
        
        prompt += f"""
### STRATEGIC PLANNER GUIDANCE ###
Use the following objectives and subtopics as your primary research focus:
Objectives:
- {objectives}
Subtopics to cover:
- {subtopics}
"""

    # ── Structured report instructions ────────────────────────────────────
    prompt += f"""
Please generate a detailed, structured markdown report. Follow the exact structure
below, using professional headings, bullet points where appropriate, and concise
but deeply technical explanations. Where you have retrieved memory context above,
actively integrate those insights to produce richer, connected analysis.

**Required Report Structure:**

# Research Report: {topic}

## 1. Introduction
High-level overview: what it is, why it matters, current industry relevance.
If related memory exists, note how this topic connects to previous research.

## 2. Core Concepts
Fundamental principles, underlying technologies, or key theories.
Break down complex ideas into professional, accessible terms.

## 3. Applications
Real-world use cases and industry applications. Use bullet points for clarity.

## 4. Advantages
Main benefits, efficiencies, or positive impacts. Why organisations adopt this.

## 5. Challenges
Current limitations, technical hurdles, ethical concerns, or adoption barriers.

## 6. Future Scope
Trajectory, upcoming innovations, and long-term potential (5–10 year horizon).

## 7. Conclusion
Powerful, synthesised concluding paragraph referencing both memory and web data.
{references_block}
"""
    prompt += """
**Output Constraints:**
- Use clean, visually appealing Markdown formatting.
- Tone: objective, academic yet accessible, highly professional.
- Do NOT include conversational filler. Begin directly with the Markdown title.
- STRICT LINK RULE: Do NOT invent, fabricate, or guess any URLs or hyperlinks. NEVER write [text](https://example.com) or any placeholder links.
- STRICT LINK RULE: Only cite sources that were explicitly provided in the web search results above. If you want to reference a source, write its plain URL directly (e.g. https://actual-url.com) — do NOT wrap it in markdown link syntax.
- The ## 8. References section MUST use ONLY the exact URLs provided in the source list — do not modify or invent any URL.
- If memory context was provided, explicitly connect insights across research sessions.
"""
    return prompt.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Main Agent Function
# ─────────────────────────────────────────────────────────────────────────────

def generate_research(topic: str, plan: dict = None) -> dict:
    """
    RAG-enhanced research generation pipeline.

    New workflow vs. the original:
      OLD: web search → scrape → generate
      NEW: memory retrieval → web search → scrape → generate (with memory context and roadmap)

    Args:
        topic (str): The research subject.
        plan (dict): The Planner Agent's JSON roadmap.


    Returns:
        dict: {
            "report"   (str):  AI-generated markdown report.
            "memories" (list): Retrieved memory dicts for UI display.
                               Empty list if no memories were found/relevant.
        }
        On API error, "report" starts with "⚠️" and "memories" is [].
    """
    if not topic:
        return {"report": "Error: Please provide a valid research topic.", "memories": []}

    # ── STEP 0: Retrieve related memories (RAG) ───────────────────────────
    print(f"\n[Memory Retrieval] Searching semantic memory for: '{topic}'")
    try:
        from memory.memory_manager import search_memory_context
        memory_context, retrieved_memories = search_memory_context(
            query=topic,
            n_results=3,
            min_similarity=0.20
        )
        if retrieved_memories:
            print(f"[Memory Injection] Context successfully injected into Researcher Agent.")
        else:
            print("[Memory Retrieval] No relevant memory found. Proceeding without context.")
    except Exception as e:
        print(f"[Memory Retrieval Error] Could not search memory: {e}")
        memory_context, retrieved_memories = "", []

    # ── STEP 1: Web search ────────────────────────────────────────────────
    web_results = search_web(topic)
    web_context = format_search_results(web_results)

    # Build a clean source list for the References section
    source_urls = []
    for r in (web_results or []):
        url   = r.get("url", "")
        title = r.get("title", url)
        if url and url.startswith("http"):
            source_urls.append({"title": title, "url": url})

    # ── STEP 2: Deep scrape top 2 results ────────────────────────────────
    deep_context  = ""
    scraped_count = 0

    if web_results:
        for r in web_results[:2]:
            url = r.get("url")
            if url and url.startswith("http"):
                print(f"[*] Deep Research: Launching browser to scrape content from: {url}")
                article_text = scrape_article(url)
                if article_text:
                    deep_context += f"--- Deep Web Source: {r['title']} ({url}) ---\n"
                    # 1500 chars ≈ 375 tokens — balanced between context and budget
                    deep_context += f"{article_text[:1500]}\n"
                    deep_context += "-" * 50 + "\n\n"
                    scraped_count += 1

        print(f"[*] Deep Research: Successfully gathered detailed context from {scraped_count} webpages.")

    if deep_context:
        web_context += "\n### DEEP SCRAPED WEB PAGE CONTENT ###\n"
        web_context += (
            "The following are actual readable sections scraped from the top web results. "
            "Use this detailed data to write highly specific, factual sections:\n\n"
        )
        web_context += deep_context

    # ── STEP 3: Assemble prompt with full context ─────────────────────────
    print(f"[*] Compiling research parameters for: {topic}...")
    prompt = create_research_prompt(
        topic=topic,
        web_context=web_context,
        source_urls=source_urls,
        memory_context=memory_context,
        plan=plan
    )

    # ── STEP 4: Generate report via Groq ─────────────────────────────────
    print("[*] Transmitting request to Groq AI engine...")
    report = ask_groq(prompt)

    if report.startswith("⚠️"):
        print(f"[Researcher Agent] API quota/rate-limit issue detected: {report[:120]}...")
        return {"report": report, "memories": retrieved_memories}

    return {"report": report, "memories": retrieved_memories}


# ─────────────────────────────────────────────────────────────────────────────
# Refinement & Self-Correction
# ─────────────────────────────────────────────────────────────────────────────

def create_refinement_prompt(topic: str, previous_report: str, critique_json: dict) -> str:
    """
    Constructs the LLM prompt for iterative self-correction.
    
    Args:
        topic           (str): The original research topic.
        previous_report (str): The v1 markdown report to improve.
        critique_json   (dict): Structured feedback from the Critic Agent.
        
    Returns:
        str: Prompt instructing the model to output a refined report.
    """
    weaknesses = "\n- ".join(critique_json.get("weaknesses", ["None noted."]))
    missing = "\n- ".join(critique_json.get("missing_topics", ["None noted."]))
    suggestions = "\n- ".join(critique_json.get("improvement_suggestions", ["None noted."]))

    prompt = f"""You are an elite AI Research Scientist. Your task is to critically refine and optimize an existing research report based on expert feedback.

Topic: "{topic}"

### PREVIOUS REPORT TO IMPROVE ###
{previous_report}

### EXPERT CRITIQUE & FEEDBACK ###
Weaknesses to fix:
- {weaknesses}

Missing Topics to integrate:
- {missing}

Improvement Suggestions to apply:
- {suggestions}

### INSTRUCTIONS ###
1. Generate an updated, fully-optimized version of the research report.
2. Retain all the high-quality insights and structure from the previous report.
3. Directly address the feedback by filling in the missing topics and fixing the weaknesses.
4. Output MUST follow the same professional markdown structure as the original (e.g. ## 1. Introduction, ## 2. Core Concepts, etc).
5. Output ONLY the new markdown report. Do not include conversational filler or explanations of what you changed.
"""
    return prompt.strip()


def refine_research(topic: str, previous_report: str, critique_json: dict) -> str:
    """
    Generates an optimized v2 research report based on Critic feedback.
    Bypasses web scraping to save tokens and time, focusing strictly on reasoning and synthesis.
    
    Args:
        topic           (str): The research subject.
        previous_report (str): The existing report.
        critique_json   (dict): Structured critique data.
        
    Returns:
        str: The optimized markdown report.
    """
    print(f"[Researcher Agent] Initiating self-correction refinement for: '{topic}'...")
    
    prompt = create_refinement_prompt(topic, previous_report, critique_json)
    
    print("[Researcher Agent] Transmitting refinement request to Groq...")
    optimized_report = ask_groq(prompt)
    
    if optimized_report.startswith("⚠️"):
        print(f"[Researcher Agent Error] API quota issue during refinement.")
        
    return optimized_report


# ─────────────────────────────────────────────────────────────────────────────
# Standalone testing
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Researcher Agent Initialization (RAG Mode) ===")
    test_topic = input("Enter a topic to research: ").strip()

    if test_topic:
        print("\n" + "=" * 60)
        result = generate_research(test_topic)
        print("=" * 60)
        print(f"\nRetrieved {len(result['memories'])} past memories.\n")
        print(result["report"])
        print("=" * 60)
    else:
        print("Agent execution cancelled: No topic provided.")
