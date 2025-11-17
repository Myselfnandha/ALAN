# alan_core/memory.py
import time, uuid, json, os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List

@dataclass
class MemoryItem:
    id: str
    ts: float
    kind: str
    content: Any

class Memory:
    def __init__(self, long_term_path="alan_memory.json"):
        self.short = []
        self.long = {}
        self.long_term_path = long_term_path
        if os.path.exists(long_term_path):
            try:
                data = json.load(open(long_term_path))
                for k,v in data.items():
                    self.long[k] = MemoryItem(**v)
            except Exception:
                pass

    def write(self, kind, content, long_term=False):
        item = MemoryItem(id=str(uuid.uuid4()), ts=time.time(), kind=kind, content=content)
        if long_term:
            self.long[item.id] = asdict(item)
            self._flush()
        else:
            self.short.append(asdict(item))
            if len(self.short) > 200: self.short.pop(0)
        return item

    def retrieve(self, q=None, limit=10):
        results = []
        pool = list(self.short) + list(self.long.values())
        if q:
            q = q.lower()
            for i in pool:
                if q in str(i.get("content","")).lower() or q in i.get("kind",""):
                    results.append(i)
        else:
            results = pool
        return results[:limit]

    def _flush(self):
        try:
            json.dump(self.long, open(self.long_term_path,"w"), indent=2)
        except Exception:
            pass
