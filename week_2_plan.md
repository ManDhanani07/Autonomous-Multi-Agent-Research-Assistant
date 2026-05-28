# 🚀 Nexus AI OS: Week 2 & Week 3 Implementation Plan

This document outlines the core engineering tasks for **Week 2** and **Week 3** of the Autonomous Multi-Agent Research Assistant. It describes exactly what we will do, how it will be done, the underlying logic, and the impact it will have on the system.

---

## 📅 WEEK 2: Core Agent Pipeline & Integration

### 1. Live Web Search & Browser Integration

*   **📋 What We Do:** Wire the search scrapers (`tools/web_search_tool.py`) and headless browser readers (`tools/browser_tool.py`) directly into the **Elite Researcher Agent** (`agents/researcher_agent.py`).
*   **🛠 How We Do It:** 
    1. Update `researcher_agent.py` to accept search query parameters.
    2. Call the Google/DuckDuckGo scraper to extract top URL links before drafting.
    3. Use Playwright to extract raw text content from those pages, and feed them directly into the LLM prompt as **Factual Context**.
*   **🧠 The Logic:** An LLM cannot provide accurate research from static training data alone. Grounding it in live, external web documents forces it to cite actual web sources, reducing hallucinations to near-zero.
*   **📈 The Impact (Affect):** High real-time accuracy and a genuine **References** section with actual, clickable URLs pointing to real papers.
*   **⏭ Next Steps:** Filter search results to prioritize academic portals.

---

### 2. Agentic Self-Correction & Refinement Loops

*   **📋 What We Do:** Establish an automated feedback loop between the **AI Critic Agent** (`agents/critic_agent.py`) and the **Elite Researcher Agent** (`agents/researcher_agent.py`).
*   **🛠 How We Do It:** 
    1. Check the Critic's score (e.g., out of 10) after each draft.
    2. If the score is below the target threshold (e.g., `8.0/10`), trigger a **Refinement Loop**.
    3. Send the draft and the Critic's feedback report back to the Researcher, instructing it to address the gaps and rewrite. Repeat this up to 3 times.
*   **🧠 The Logic:** Single-turn generation often misses details. Mimicking the academic peer-review loop forces the AI to check its own work, correct formatting issues, and elaborate on gaps.
*   **📈 The Impact (Affect):** The output quality drastically improves without the user needing to ask for edits manually.
*   **⏭ Next Steps:** Render the step-by-step correction history in the Streamlit UI.

---

### 3. RAG Memory Recall & Context Ingestion

*   **📋 What We Do:** Implement the semantic retrieval (search) path in the **Memory Manager** (`memory/memory_manager.py`) so the Researcher can retrieve and read historical research data.
*   **🛠 How We Do It:** 
    1. Query the ChromaDB vector database using cosine similarity on the topic embedding.
    2. Retrieve relevant historical research papers previously written by the system.
    3. Format and inject them as **Historical Core Context** at the top of the Researcher's prompt.
*   **🧠 The Logic:** An assistant should not start from scratch if it has researched a similar topic before. Ingesting memory ensures the agent can answer compound questions (e.g., building on yesterday's research).
*   **📈 The Impact (Affect):** Cumulative knowledge base that references previous sessions and highlights connections between past and present topics.
*   **⏭ Next Steps:** Add deduplication to prevent storing redundant information.

---

### 4. Full Pipeline Integration (Planner & Report Agents)

*   **📋 What We Do:** Fully integrate `planner_agent.py` and `report_agent.py` into the main Streamlit frontend workflow execution chain.
*   **🛠 How We Do It:** 
    1. **Planner Agent Integration:** The Planner generates a strategic Markdown Roadmap before research starts, displayed to the user.
    2. **Report Agent Integration:** Feed the final corrected drafts of all sections to the Report Agent to compile the chapters, apply a clean Markdown layout, format headers, and generate a table of contents.
*   **🧠 The Logic:** Separating concerns guarantees high-quality outputs: the Planner focuses on direction, the Researcher on factual data gathering, the Critic on validation, and the Report Agent on editorial presentation.
*   **📈 The Impact (Affect):** Complete, unified workflow (planning-to-publication) in a single click.
*   **⏭ Next Steps:** Integrate an "Export to PDF" button that compiles the report into a downloadable document.

---

## 📅 WEEK 3: Production Enhancements & Academic Scaling

### 1. Academic Search APIs Integration (NASA/arXiv ADS)

*   **📋 What We Do:** Integrate professional academic search APIs (like Semantic Scholar, arXiv, or NASA PubSpace/ADS API) alongside the general web search tool.
*   **🛠 How We Do It:** 
    1. Create a new module `tools/academic_search_tool.py` that connects to these API endpoints.
    2. Extract metadata such as peer-reviewed status, citation counts, and publication date.
    3. Prioritize high-impact academic sources in the Researcher's context.
*   **🧠 The Logic:** NASA researchers and scientists require peer-reviewed journal papers (like Nature, IEEE, or arXiv) rather than standard commercial web blogs.
*   **📈 The Impact (Affect):** Upgrades the assistant from a general web summary engine to a **rigorous scientific research tool** worthy of advanced academic research.
*   **⏭ Next Steps:** Auto-generate BibTeX citation records for each source.

---

### 2. Full-Length PDF Parsing & Extraction

*   **📋 What We Do:** Implement a document processing engine that can extract text, tables, and references from full-length research PDFs.
*   **🛠 How We Do It:** 
    1. Integrate Python libraries like `pdfplumber` or `pypdf` into our extractor.
    2. Implement a sliding window chunking algorithm to handle long, 20+ page academic PDFs.
    3. Generate individual section summaries of the PDF files before feeding them to the Researcher Agent.
*   **🧠 The Logic:** Primary technical research is written in academic PDFs. Standard web scrapers cannot extract metadata or structured text from locked or dense PDF layouts.
*   **📈 The Impact (Affect):** The agent can ingest and comprehend highly technical formulas, tables, and data figures directly.
*   **⏭ Next Steps:** Implement OCR (Optical Character Recognition) using Tesseract for scanned PDF documents.

---

### 3. LaTeX Export & BibTeX Bibliography Generator

*   **📋 What We Do:** Enable professional formatting exports including structured LaTeX templates and automatically formatted BibTeX citations.
*   **🛠 How We Do It:** 
    1. Write a compilation module in `report_agent.py` that formats the Markdown output into a LaTeX document (`.tex`).
    2. Auto-generate a `references.bib` file containing all URL/academic citation keys used in the research process.
    3. Offer a download button in the UI for the compiled `.tex` zip package.
*   **🧠 The Logic:** Academic researchers write papers in LaTeX, not Markdown. Providing pre-formatted LaTeX files speeds up the drafting process for academic submission.
*   **📈 The Impact (Affect):** Researchers can immediately compile, print, or submit the generated papers to journals.
*   **⏭ Next Steps:** Implement styles that match standard journal formats (e.g., IEEE, ACM, Nature templates).

---

### 4. Multi-User Workspaces & Isolated Vector Contexts

*   **📋 What We Do:** Implement isolated user workspaces and multiple active ChromaDB vector databases.
*   **🛠 How We Do It:** 
    1. Update `chroma_store.py` to support dynamic namespace/collection switching.
    2. Assign active collections based on the user's project ID or session key.
    3. Allow researchers to create separate workspaces (e.g., "Aerospace Project," "Material Science Project") that do not blend contexts.
*   **🧠 The Logic:** NASA researchers work on completely different programs (e.g., rocket fuels vs. satellite orbital mechanics). Blending these datasets in a single vector pool degrades RAG query relevance.
*   **📈 The Impact (Affect):** Perfect context isolation, high query relevance, and the ability to maintain private or project-specific databases.
*   **⏭ Next Steps:** Enable sharing or merging of specific workspaces between users.
