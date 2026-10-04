from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.schemas import RequirementAnalysisOutput
from app.core.llm import generate_with_fallback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os

class RequirementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Requirement Agent", "Analyzes raw user requirements into structured format.")
        
    def get_input_schema(self) -> Dict[str, Any]:
        return {"user_requirement": "str"}

    def get_output_schema(self) -> Dict[str, Any]:
        return RequirementAnalysisOutput.model_json_schema()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_req = state.get("user_requirement", "")
        if not user_req:
            raise ValueError("No user_requirement found in state.")

        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "requirement_agent.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        parser = PydanticOutputParser(pydantic_object=RequirementAnalysisOutput)
        format_instructions = parser.get_format_instructions()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Requirement:\n{requirement}\n\n{format_instructions}")
        ])
        
        formatted_prompt = prompt_template.format_messages(
            requirement=user_req,
            format_instructions=format_instructions
        )
        
        result: RequirementAnalysisOutput = generate_with_fallback(formatted_prompt, RequirementAnalysisOutput)
        
        return {
            "requirements": result.model_dump(),
            "status": "REQUIREMENT_ANALYSIS_COMPLETED"
        }
