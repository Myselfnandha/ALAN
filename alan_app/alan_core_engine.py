"""
alan_core_engine.py

Fundamental, minimal, and extendable core engine for "Alan".
Provides:
 - InputProcessor: simple parsing + normalization
 - Memory: short-term + long-term store with simple retrieval
 - Planner: two-level hierarchical planner (produces subtasks)
 - Worker: executes simple tasks and reports results
 - Planner-Worker loop: dynamic depth handling and local gradient-like updates
 - OutputRenderer: formats outputs for user

This file is intentionally simple and meant as a starting point for iterative improvement
and integration into a larger system. Add async, models, and persistence later.

Run directly to see a demonstration flow.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Optional, Tuple
import time
import uuid
import pprint

pp = pprint.PrettyPrinter(indent=2)

# ------------------------
# Utilities
# ------------------------

def now_ts() -> float:
    return time.time()

# ------------------------
# Memory
# ------------------------

@dataclass
class MemoryItem:
    id: str
    timestamp: float
    kind: str
    content: Any
    score: float = 1.0

class Memory:
    """Simple in-memory store with short-term (list) and long-term (dict) access.
    Supports retrieval by simple keyword matching and recency boosting.
    """
    def __init__(self):
        self.short_term: List[MemoryItem] = []
        self.long_term: Dict[str, MemoryItem] = {}

    def write(self, kind: str, content: Any, long_term: bool = False) -> MemoryItem:
        item = MemoryItem(id=str(uuid.uuid4()), timestamp=now_ts(), kind=kind, content=content)
        if long_term:
            self.long_term[item.id] = item
        else:
            self.short_term.append(item)
            # keep short-term bounded
            if len(self.short_term) > 100:
                self.short_term.pop(0)
        return item

    def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        # naive scoring: keyword presence + recency
        def score(item: MemoryItem) -> float:
            s = 0.0
            text = str(item.content).lower()
            if query.lower() in text:
                s += 10.0
            # recency (simple)
            s += max(0.0, 1.0 - (now_ts() - item.timestamp) / 3600.0)
            s += item.score
            return s

        candidates = list(self.short_term) + list(self.long_term.values())
        candidates.sort(key=score, reverse=True)
        return candidates[:limit]

# ------------------------
# Input / Output
# ------------------------

class InputProcessor:
    """Minimal parsing: trim, lower, simple intent heuristics."""
    def preprocess(self, raw: str) -> Dict[str, Any]:
        text = raw.strip()
        intent = self._detect_intent(text)
        tokens = text.split()
        return {"raw": raw, "text": text, "intent": intent, "tokens": tokens}

    def _detect_intent(self, text: str) -> str:
        t = text.lower()
        if t.startswith("create") or t.startswith("build"):
            return "create"
        if t.startswith("fix") or t.startswith("debug"):
            return "debug"
        if t.endswith("?"):
            return "query"
        return "general"

class OutputRenderer:
    def render(self, result: Any) -> str:
        # make output human friendly
        if isinstance(result, dict) or isinstance(result, list):
            return pp.pformat(result)
        return str(result)

# ------------------------
# Planner / Worker
# ------------------------

@dataclass
class Task:
    id: str
    description: str
    depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class Planner:
    """Two-level hierarchical planner: planner produces high-level plan then decomposes.
    This is a simplified deterministic planner for demonstration.
    """
    def __init__(self):
        pass

    def plan(self, processed_input: Dict[str, Any]) -> List[Task]:
        intent = processed_input.get("intent", "general")
        text = processed_input.get("text", "")
        root = Task(id=str(uuid.uuid4()), description=f"Handle intent={intent}: {text}", depth=0)

        # Level-1 decomposition
        subtasks = self.decompose(root)
        return subtasks

    def decompose(self, task: Task) -> List[Task]:
        # naive rules for decomposition
        desc = task.description.lower()
        if "create" in desc or "build" in desc:
            return [
                Task(id=str(uuid.uuid4()), description="scaffold project structure", depth=1),
                Task(id=str(uuid.uuid4()), description="create core modules", depth=1),
                Task(id=str(uuid.uuid4()), description="write basic tests", depth=1),
            ]
        if "debug" in desc or "fix" in desc:
            return [
                Task(id=str(uuid.uuid4()), description="reproduce issue", depth=1),
                Task(id=str(uuid.uuid4()), description="apply fix", depth=1),
                Task(id=str(uuid.uuid4()), description="write regression test", depth=1),
            ]
        # default split
        return [Task(id=str(uuid.uuid4()), description="analyze", depth=1), Task(id=str(uuid.uuid4()), description="respond", depth=1)]

class Worker:
    """Executes tasks. In real system this runs models, tools, or external calls.
    Here we provide synchronous deterministic behaviors for each basic task.
    """
    def __init__(self, memory: Memory):
        self.memory = memory

    def execute(self, task: Task) -> Dict[str, Any]:
        # Simulated execution time and result
        t0 = now_ts()
        result = None
        if "scaffold" in task.description:
            result = {"files": ["README.md", "src/", "alan_core/"]}
        elif "core modules" in task.description:
            result = {"modules": ["planner", "worker", "memory", "io"]}
        elif "tests" in task.description:
            result = {"tests": ["test_basic_flow.py"]}
        elif "reproduce" in task.description:
            result = {"status": "reproduced sample input"}
        elif "apply fix" in task.description:
            result = {"status": "fix applied"}
        elif "analyze" in task.description:
            result = {"analysis": "short analysis summary"}
        elif "respond" in task.description:
            result = {"response": "Here's a helpful answer."}
        else:
            # fallback echo
            result = {"echo": task.description}

        # small effect on memory (local gradient-like update)
        self.memory.write(kind="task_result", content={"task": task.description, "result": result})

        duration = now_ts() - t0
        return {"task_id": task.id, "description": task.description, "result": result, "time": duration}

# ------------------------
# Planner-Worker loop (HRM-like)
# ------------------------

class AlanCore:
    def __init__(self):
        self.memory = Memory()
        self.input = InputProcessor()
        self.output = OutputRenderer()
        self.planner = Planner()
        self.worker = Worker(self.memory)
        # dynamic depth control
        self.max_depth = 2

    def process(self, raw_input: str) -> str:
        processed = self.input.preprocess(raw_input)
        # store input in memory
        self.memory.write(kind="user_input", content=processed)

        # top-level plan
        tasks = self.planner.plan(processed)

        # planner-worker loop with dynamic depth and local updates (very simple)
        results = []
        frontier: List[Tuple[Task, int]] = [(t, 1) for t in tasks]

        while frontier:
            task, depth = frontier.pop(0)
            # quick depth check
            if depth > self.max_depth:
                # skip or summarize
                results.append({"task": task.description, "skipped": True})
                continue

            exec_result = self.worker.execute(task)
            results.append(exec_result)

            # Based on simple heuristic, the planner may decompose further
            if "scaffold" in task.description and depth < self.max_depth:
                # spawn lower-level tasks
                sub = [Task(id=str(uuid.uuid4()), description="create README", depth=depth+1), Task(id=str(uuid.uuid4()), description="create src folder", depth=depth+1)]
                for s in sub:
                    frontier.insert(0, (s, depth+1))

        # store results
        self.memory.write(kind="last_results", content=results, long_term=False)

        # render output
        return self.output.render({"summary": f"Processed input '{processed['text']}'", "results": results})

# ------------------------
# Demo / quick test
# ------------------------

if __name__ == "__main__":
    core = AlanCore()

    examples = [
        "Create a new Alan project with core engine",
        "Debug why build fails",
        "What's the status of the system?",
    ]

    for ex in examples:
        print("\n--- INPUT --->", ex)
        out = core.process(ex)
        print(out)

    # show memory
    print("\n--- MEMORY (recent) ---")
    recent = core.memory.retrieve("alan", limit=10)
    for r in recent:
        print(r.kind, r.content)
