from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "idle"
        self.logs = []
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic based on the state"""
        pass
