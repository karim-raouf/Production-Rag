import threading
from typing import Any, Dict, Optional

class ModelStore:
    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def load(self, name: str, model_object: Any) -> None:
        with self._lock:
            self._models[name] = model_object
            print(f"Model '{name}' loaded successfully.")

    def get(self, name: str) -> Optional[Any]:
        return self._models.get(name)

    def clear(self) -> None:
        with self._lock:
            self._models.clear()
            print("All models unloaded.")

# Global instance shared by ALL modules
global_ml_store = ModelStore()