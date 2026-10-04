from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.schemas import DevelopmentPlanOutput
from app.core.llm import generate_with_fallback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import json
import os

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Planner Agent", "Generates an architectural blueprint from structured requirements.")
        
    def get_input_schema(self) -> Dict[str, Any]:
        return {"requirements": "dict"}

    def get_output_schema(self) -> Dict[str, Any]:
        return DevelopmentPlanOutput.model_json_schema()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        requirements = state.get("requirements")
        if not requirements:
            raise ValueError("No requirements found in state. Run RequirementAgent first.")

        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "planner_agent.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        parser = PydanticOutputParser(pydantic_object=DevelopmentPlanOutput)
        format_instructions = parser.get_format_instructions()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Structured Requirement Analysis:\n{requirements}\n\n{format_instructions}")
        ])
        
        formatted_prompt = prompt_template.format_messages(
            requirements=json.dumps(requirements, indent=2),
            format_instructions=format_instructions
        )
        
        result: DevelopmentPlanOutput = generate_with_fallback(formatted_prompt, DevelopmentPlanOutput)
        
        return {
            "plan": result.model_dump(),
            "status": "PLANNING_COMPLETED"
        }
