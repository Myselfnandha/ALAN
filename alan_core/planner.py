# alan_core/planner.py
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Task:
    id: str
    description: str
    depth: int = 0
    priority: int = 5
    metadata: Dict[str,Any] = field(default_factory=dict)

class Planner:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def plan(self, processed_input: Dict[str,Any]) -> List[Task]:
        intent = processed_input.get("intent","general")
        text = processed_input.get("text","")
        root = Task(id=str(uuid.uuid4()), description=f"{intent}: {text}", depth=0, priority=1)
        return self.decompose(root)

    def decompose(self, task: Task) -> List[Task]:
        desc = task.description.lower()
        subtasks = []
        # rules + fallback
        if "create" in desc or "build" in desc:
            subtasks = [
                Task(id=str(uuid.uuid4()), description="scaffold project", depth=1, priority=2),
                Task(id=str(uuid.uuid4()), description="create core modules", depth=1, priority=3),
                Task(id=str(uuid.uuid4()), description="write tests", depth=1, priority=4),
            ]
        elif "debug" in desc or "fix" in desc:
            subtasks = [
                Task(id=str(uuid.uuid4()), description="collect logs", depth=1, priority=2),
                Task(id=str(uuid.uuid4()), description="reproduce", depth=1, priority=3),
                Task(id=str(uuid.uuid4()), description="apply fix", depth=1, priority=4),
            ]
        else:
            subtasks = [Task(id=str(uuid.uuid4()), description="analyze", depth=1, priority=5)]
        return subtasks
