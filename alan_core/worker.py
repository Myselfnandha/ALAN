# alan_core/worker.py
import time, subprocess, json
from alan_core.planner import Task
from typing import Dict, Any

class Worker:
    def __init__(self, memory, llm_call: callable = None):
        self.memory = memory
        self.llm_call = llm_call  # optional hook for LLM

    def run_shell(self, cmd: str) -> Dict[str,Any]:
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
            return {"stdout": out.decode("utf-8")}
        except Exception as e:
            return {"error": str(e)}

    def execute(self, task: Task) -> Dict[str,Any]:
        t0 = time.time()
        desc = task.description.lower()
        result = {}
        if "scaffold" in desc or "scaffold project" in desc:
            result = {"files": ["README.md","src/","alan_core/"]}
        elif "create core modules" in desc or "core modules" in desc:
            result = {"modules": ["planner","worker","memory","io"]}
        elif "write tests" in desc:
            result = {"tests": ["test_basic_flow.py"]}
        elif "collect logs" in desc:
            result = {"logs": "no logs (simulated)"}
        elif "reproduce" in desc:
            result = {"reproduce": True}
        elif "apply fix" in desc:
            result = {"fixed": True}
        else:
            # fallback to LLM if available
            if self.llm_call:
                result = {"llm": self.llm_call(task.description)}
            else:
                result = {"echo": task.description}
        self.memory.write(kind="task_result", content={"task": task.description, "result": result})
        return {"task_id": task.id, "description": task.description, "result": result, "time": time.time()-t0}
