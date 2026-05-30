import os
import sys
import time
import asyncio
from typing import Callable, Any, Dict, List

# Ensure project root is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents
from agents.planner_agent import generate_plan
from agents.researcher_agent import generate_research, refine_research
from agents.fact_validation_agent import validate_research_facts
from agents.summarizer_agent import summarize_research
from agents.critic_agent import critique_research
from agents.report_agent import generate_final_report
from memory.memory_manager import save_research_to_memory, search_memory_context

class Task:
    def __init__(self, task_id: str, name: str, dependencies: List[str], run_func: Callable, max_retries: int = 3):
        self.task_id = task_id
        self.name = name
        self.dependencies = dependencies
        self.run_func = run_func
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        self.retry_count = 0
        self.max_retries = max_retries

class AgentOrchestrator:
    def __init__(self, topic: str, workspace: str = "default", status_callback: Callable = None):
        self.topic = topic
        self.workspace = workspace
        self.status_callback = status_callback
        self.tasks: Dict[str, Task] = {}
        self.pipeline_status = "IDLE"  # IDLE, RUNNING, COMPLETED, FAILED
        self.logs: List[str] = []
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        
        self._initialize_dag()

    def _log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
        if self.status_callback:
            self.status_callback(self)

    def _initialize_dag(self):
        """
        Creates all tasks in the 9-stage multi-agent research pipeline.
        """
        # Define tasks with their run functions and dependencies
        self.tasks["planner"] = Task(
            task_id="planner",
            name="1. Strategic Planner Agent",
            dependencies=[],
            run_func=self._run_planner
        )
        
        # Parallel subtopics will be dynamically generated once the planner finishes.
        # But we initialize placeholders so they are visible in the graph.
        for i in range(3):
            self.tasks[f"researcher_{i}"] = Task(
                task_id=f"researcher_{i}",
                name=f"2. Researcher Agent: Subtopic {chr(65+i)}",
                dependencies=["planner"],
                run_func=lambda task, idx=i: self._run_researcher(idx)
            )
            
        self.tasks["fact_validation"] = Task(
            task_id="fact_validation",
            name="3. Fact Validation Agent",
            dependencies=["researcher_0", "researcher_1", "researcher_2"],
            run_func=self._run_fact_validation
        )
        
        self.tasks["rag_enhancement"] = Task(
            task_id="rag_enhancement",
            name="4. Memory/RAG Enhancement",
            dependencies=["fact_validation"],
            run_func=self._run_rag_enhancement
        )
        
        self.tasks["summarizer"] = Task(
            task_id="summarizer",
            name="5. Summarizer Agent",
            dependencies=["rag_enhancement"],
            run_func=self._run_summarizer
        )
        
        self.tasks["critic"] = Task(
            task_id="critic",
            name="6. Critic Agent",
            dependencies=["summarizer", "rag_enhancement"],
            run_func=self._run_critic
        )
        
        self.tasks["self_correction"] = Task(
            task_id="self_correction",
            name="7. Self-Correction Loop",
            dependencies=["critic"],
            run_func=self._run_self_correction
        )
        
        self.tasks["report_generator"] = Task(
            task_id="report_generator",
            name="8. Report Generator Agent",
            dependencies=["self_correction"],
            run_func=self._run_report_generator
        )
        
        self.tasks["memory_storage"] = Task(
            task_id="memory_storage",
            name="9. Memory Storage",
            dependencies=["report_generator"],
            run_func=self._run_memory_storage
        )

    # ── Task Execution Functions ─────────────────────────────────────────────
    
    async def _run_planner(self, task: Task) -> dict:
        self._log("Planner Agent: Structuring research roadmap...")
        loop = asyncio.get_running_loop()
        plan = await loop.run_in_executor(None, generate_plan, self.topic)
        if not plan:
            raise ValueError("Planner failed to generate strategic research objectives.")
            
        # Dynamically set subtopic names in the task descriptions
        subtopics = plan.get("subtopics", [])
        for i in range(3):
            sub_name = subtopics[i] if i < len(subtopics) else f"Subtopic {chr(65+i)}"
            self.tasks[f"researcher_{i}"].name = f"2. Researcher Agent: {sub_name[:35]}"
            
        self._log(f"Planner Agent: Strategy structured successfully with {len(subtopics)} subtopics.")
        return plan

    async def _run_researcher(self, subtopic_idx: int) -> dict:
        task = self.tasks[f"researcher_{subtopic_idx}"]
        plan_task = self.tasks["planner"]
        plan = plan_task.result
        
        subtopics = plan.get("subtopics", [])
        if subtopic_idx < len(subtopics):
            subtopic = subtopics[subtopic_idx]
        else:
            subtopic = f"{self.topic} Details Part {subtopic_idx+1}"
            
        self._log(f"Researcher Agent {subtopic_idx+1}: Initiating deep search for '{subtopic}'...")
        loop = asyncio.get_running_loop()
        
        # Call generate_research inside thread pool
        research_result = await loop.run_in_executor(
            None, 
            generate_research, 
            subtopic, 
            plan, 
            self.workspace
        )
        
        report_text = research_result.get("report", "")
        if report_text.startswith("⚠️"):
            raise ValueError(f"Researcher hit API errors: {report_text[:100]}")
            
        self._log(f"Researcher Agent {subtopic_idx+1}: Search completed for '{subtopic}' (Gathered {len(research_result.get('sources', []))} sources).")
        return {
            "subtopic": subtopic,
            "report": report_text,
            "sources": research_result.get("sources", []),
            "pdf_chunks": research_result.get("pdf_chunks", []),
            "academic_papers": research_result.get("academic_papers", []),
            "fallback_used": research_result.get("fallback_used", False)
        }

    async def _run_fact_validation(self, task: Task) -> dict:
        self._log("Fact Validation Agent: Evaluating subtopic report drafts...")
        
        # Compile all subtopic reports
        subtopic_reports = []
        for i in range(3):
            res_task = self.tasks[f"researcher_{i}"]
            subtopic_reports.append({
                "subtopic": res_task.result["subtopic"],
                "report": res_task.result["report"]
            })
            
        loop = asyncio.get_running_loop()
        validated_text = await loop.run_in_executor(
            None,
            validate_research_facts,
            subtopic_reports
        )
        
        if validated_text.startswith("⚠️"):
            raise ValueError(f"Fact Validation Agent failed: {validated_text[:100]}")
            
        # Run granular claims verification against all collected references
        self._log("Fact Validation Agent: Extracting claims and checking against sources...")
        from agents.fact_validator_agent import validate_report_with_sources
        
        sources = []
        pdf_chunks = []
        for i in range(3):
            res_task = self.tasks[f"researcher_{i}"]
            if res_task.result:
                sources.extend(res_task.result.get("sources", []))
                pdf_chunks.extend(res_task.result.get("pdf_chunks", []))
                
        validation_res = await loop.run_in_executor(
            None,
            validate_report_with_sources,
            validated_text,
            sources,
            pdf_chunks
        )
        
        self._log(f"Fact Validation Agent: Completed verification. Trust Score: {validation_res['trust_score']}%")
        return {
            "validated_text": validation_res["validated_text"],
            "trust_score": validation_res["trust_score"],
            "hallucination_score": validation_res["hallucination_score"],
            "confidence_label": validation_res["confidence_label"],
            "claims_validation": validation_res["claims_validation"],
            "warnings": validation_res["warnings"]
        }

    async def _run_rag_enhancement(self, task: Task) -> dict:
        self._log("RAG Enhancement: Retrieving past database context...")
        loop = asyncio.get_running_loop()
        
        # Retrieve past memories
        memory_context, retrieved_memories = await loop.run_in_executor(
            None,
            search_memory_context,
            self.topic,
            3,
            0.20,
            self.workspace
        )
        
        self._log(f"RAG Enhancement: Retrieved {len(retrieved_memories)} historical memories.")
        return {
            "context": memory_context,
            "memories": retrieved_memories
        }

    async def _run_summarizer(self, task: Task) -> str:
        self._log("Summarizer Agent: Creating executive summary findings...")
        validated_text = self.tasks["fact_validation"].result["validated_text"]
        
        loop = asyncio.get_running_loop()
        summary = await loop.run_in_executor(
            None,
            summarize_research,
            validated_text
        )
        
        if summary.startswith("⚠️"):
            raise ValueError(f"Summarizer failed: {summary[:100]}")
            
        self._log("Summarizer Agent: Executive summary completed.")
        return summary

    async def _run_critic(self, task: Task) -> dict:
        self._log("Critic Agent: Rating and reviewing consolidated research quality...")
        validation_res = self.tasks["fact_validation"].result
        validated_text = validation_res["validated_text"]
        summary = self.tasks["summarizer"].result
        
        # Inject fact-check trust score and warning metadata so the Critic can penalize if needed
        trust_score = validation_res.get("trust_score", 100.0)
        warnings = validation_res.get("warnings", [])
        
        validation_meta = f"\n\n### FACT CHECK METADATA (DO NOT REMOVE)\n- Fact Trust Score: {trust_score}%\n- Hallucination Score: {100.0 - trust_score}%\n"
        if warnings:
            validation_meta += "- Unsupported Claims Detected:\n" + "\n".join([f"  * {w}" for w in warnings]) + "\n"
            
        research_text_for_critic = validated_text + validation_meta
        
        loop = asyncio.get_running_loop()
        critique = await loop.run_in_executor(
            None,
            critique_research,
            research_text_for_critic,
            summary
        )
        
        if "error" in critique:
            raise ValueError(f"Critic failed: {critique.get('error')}")
            
        # Apply hallucination penalty based on Trust Score to force correction loop
        score = critique.get("score", 0.0)
        if trust_score < 85.0:
            penalty = round((85.0 - trust_score) / 10.0, 1)
            score = max(1.0, round(score - penalty, 1))
            critique["score"] = score
            critique["weaknesses"] = critique.get("weaknesses", []) + [f"Low Fact Trust Score ({trust_score}%). Unsupported claims detected."]
            self._log(f"Critic Agent: Applied hallucination penalty of -{penalty}. Adjusted score: {score}/10.")
            
        self._log(f"Critic Agent: Evaluation complete. Score: {score}/10.")
        return critique

    async def _run_self_correction(self, task: Task) -> dict:
        validated_text = self.tasks["fact_validation"].result["validated_text"]
        critique = self.tasks["critic"].result
        score = float(critique.get("score", 0.0))
        
        if score >= 8.5:
            self._log(f"Self-Correction: Quality score {score} >= 8.5. Skipping refinement loop.")
            task.status = "SKIPPED"
            return {
                "refined_text": validated_text,
                "refined_summary": self.tasks["summarizer"].result,
                "refined_critique": critique,
                "final_critique": critique,
                "original_critique": critique,
                "optimized": False,
                "score_delta": 0.0
            }
            
        self._log(f"Self-Correction: Quality score {score} < 8.5. Initiating refinement loop...")
        loop = asyncio.get_running_loop()
        
        refined_text = await loop.run_in_executor(
            None,
            refine_research,
            self.topic,
            validated_text,
            critique
        )
        
        if refined_text.startswith("⚠️"):
            self._log("Self-Correction Warning: Refinement failed. Using original validated drafts.")
            return {
                "refined_text": validated_text,
                "refined_summary": self.tasks["summarizer"].result,
                "refined_critique": critique,
                "final_critique": critique,
                "original_critique": critique,
                "optimized": False,
                "score_delta": 0.0
            }
            
        # Re-summarize & Re-critique
        self._log("Self-Correction: Generating improved summary for refined draft...")
        refined_summary = await loop.run_in_executor(None, summarize_research, refined_text)
        
        self._log("Self-Correction: Evaluating refined draft score...")
        refined_critique = await loop.run_in_executor(None, critique_research, refined_text, refined_summary)
        
        refined_score = float(refined_critique.get("score", 0.0))
        delta = round(refined_score - score, 1)
        self._log(f"Self-Correction: Complete. Original: {score} | Refined: {refined_score} | Delta: {delta}")
        
        if refined_score > score:
            self._log("Self-Correction: Retaining optimized v2 draft.")
            return {
                "refined_text": refined_text,
                "refined_summary": refined_summary,
                "refined_critique": refined_critique,
                "final_critique": refined_critique,
                "original_critique": critique,
                "optimized": True,
                "score_delta": delta
            }
        else:
            self._log("Self-Correction: Optimized draft did not score higher. Reverting to validated v1 drafts.")
            return {
                "refined_text": validated_text,
                "refined_summary": self.tasks["summarizer"].result,
                "refined_critique": critique,
                "final_critique": critique,
                "original_critique": critique,
                "optimized": False,
                "score_delta": delta
            }

    async def _run_report_generator(self, task: Task) -> str:
        self._log("Report Generator Agent: Compiling publication-grade report layout...")
        
        # Read correction loop outputs
        corr_result = self.tasks["self_correction"].result
        text_body = corr_result["refined_text"]
        summary = corr_result["refined_summary"]
        crit_dict = corr_result["refined_critique"]
        
        # Combine all sources gathered from subtopics, deduplicated and limited to top 10
        sources = []
        seen_source_keys = set()
        for i in range(3):
            res_task = self.tasks[f"researcher_{i}"]
            if res_task.result:
                for src in res_task.result.get("sources", []):
                    url = src.get("url", "")
                    title = src.get("title", "")
                    key = url if url else title
                    if key and key not in seen_source_keys:
                        seen_source_keys.add(key)
                        sources.append(src)
        sources = sources[:10]
                    
        critique_str = f"Score: {crit_dict.get('score', 'N/A')}/10\nStrengths: {crit_dict.get('strengths')}\nSuggestions: {crit_dict.get('improvement_suggestions')}"
        
        loop = asyncio.get_running_loop()
        final_report = await loop.run_in_executor(
            None,
            generate_final_report,
            text_body,
            summary,
            critique_str,
            sources
        )
        
        self._log("Report Generator Agent: Finished formatting markdown layouts and reference links.")
        return final_report

    async def _run_memory_storage(self, task: Task) -> bool:
        self._log("Memory Storage: Archiving report into ChromaDB index...")
        
        final_report = self.tasks["report_generator"].result
        corr_result = self.tasks["self_correction"].result
        summary = corr_result["refined_summary"]
        crit_dict = corr_result["refined_critique"]
        
        crit_str = str(crit_dict)
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            save_research_to_memory,
            self.topic,
            final_report,
            summary,
            crit_str,
            self.workspace
        )
        
        self._log("Memory Storage: Successfully archived report in long-term memory.")
        return True

    # ── DAG Core Asynchronous Loop ───────────────────────────────────────────
    
    async def run(self):
        """
        Executes the DAG using dependency-based task parallelization.
        """
        self.start_time = time.time()
        self.pipeline_status = "RUNNING"
        self._log(f"Initializing Neural multi-agent pipeline for topic: '{self.topic}'")
        
        # Main execution loop
        while True:
            # Check completed / failed tasks
            all_completed = True
            pipeline_failed = False
            
            for t_id, task in self.tasks.items():
                if task.status == "FAILED" and task.retry_count >= task.max_retries:
                    pipeline_failed = True
                if task.status not in ["COMPLETED", "SKIPPED"]:
                    all_completed = False
                    
            if pipeline_failed:
                self.pipeline_status = "FAILED"
                self.end_time = time.time()
                self.duration = round(self.end_time - self.start_time, 1)
                self._log("Pipeline execution aborted due to critical agent failure.")
                break
                
            if all_completed:
                self.pipeline_status = "COMPLETED"
                self.end_time = time.time()
                self.duration = round(self.end_time - self.start_time, 1)
                self._log("All agents completed successfully. Research ready.")
                break
                
            # Scan for tasks that are ready to run
            ready_tasks: List[Task] = []
            for t_id, task in self.tasks.items():
                if task.status not in ["PENDING", "FAILED"]:
                    continue
                if task.status == "FAILED" and task.retry_count >= task.max_retries:
                    continue
                    
                # Verify dependencies are completed
                deps_met = True
                for dep_id in task.dependencies:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status not in ["COMPLETED", "SKIPPED"]:
                        deps_met = False
                        break
                
                if deps_met:
                    ready_tasks.append(task)
                    
            if not ready_tasks:
                # Waiting for active tasks to finish
                await asyncio.sleep(0.2)
                continue
                
            # Launch ready tasks concurrently
            async_tasks = [self._execute_task(task) for task in ready_tasks]
            await asyncio.gather(*async_tasks)

    async def _execute_task(self, task: Task):
        """
        Executes a single task, managing timing, status, and retries.
        """
        if task.status == "FAILED":
            task.retry_count += 1
            self._log(f"Retrying task '{task.task_id}' (Attempt {task.retry_count}/{task.max_retries})...")
            
        task.status = "RUNNING"
        task.start_time = time.time()
        self._log(f"Agent Active: {task.name}")
        
        try:
            task.result = await task.run_func(task)
            task.end_time = time.time()
            task.duration = round(task.end_time - task.start_time, 1)
            
            # Skip tasks might modify status internally (e.g. self_correction)
            if task.status != "SKIPPED":
                task.status = "COMPLETED"
                
            self._log(f"Agent Completed: {task.name} ({task.duration}s)")
            
        except Exception as e:
            task.end_time = time.time()
            task.duration = round(task.end_time - task.start_time, 1)
            task.error = str(e)
            task.status = "FAILED"
            self._log(f"Agent Failed: {task.name} ({task.duration}s). Error: {e}")
            
            if task.retry_count >= task.max_retries:
                self._log(f"Task '{task.task_id}' exceeded max retries. Mark pipeline failed.")

if __name__ == "__main__":
    # Test orchestrator locally
    async def main():
        orchestrator = AgentOrchestrator("Quantum Computing in Finance")
        await orchestrator.run()
        
    asyncio.run(main())
