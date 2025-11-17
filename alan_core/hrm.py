# alan_core/hrm.py
from alan_core.planner import Planner
from alan_core.worker import Worker
from alan_core.memory import Memory

class HRM:
    def __init__(self, llm_call=None):
        self.memory = Memory()
        self.planner = Planner()
        self.worker = Worker(self.memory, llm_call=llm_call)
        self.max_depth = 3

    def run(self, processed_input):
        plan = self.planner.plan(processed_input)
        results = []
        frontier = [(t,1) for t in plan]
        while frontier:
            task,depth = frontier.pop(0)
            if depth > self.max_depth:
                results.append({"task":task.description,"skipped":True})
                continue
            res = self.worker.execute(task)
            results.append(res)
            # adapt: if a task result contains 'fixed' or 'llm' ask for deeper follow-up
            if res.get("result",{}).get("fixed"):
                # create verification task
                v = type(task)(id="verify-"+task.id, description="verify fix", depth=depth+1)
                frontier.insert(0,(v,depth+1))
        self.memory.write(kind="last_results", content=results, long_term=False)
        return results
