from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.workflow.state import DevelopmentState
from app.workflow.nodes import (
    requirement_node,
    planner_node,
    coder_node,
    tester_node,
    reviewer_node,
    debugger_node,
    evaluator_node,
    documentor_node
)
from app.workflow.routing import route_after_review

memory = MemorySaver()

def build_graph_a():
    workflow = StateGraph(DevelopmentState)

    workflow.add_node("requirement", requirement_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("documentor", documentor_node)

    workflow.set_entry_point("requirement")

    workflow.add_conditional_edges("requirement", lambda state: END if state.get("status") == "FAILED" else "planner")
    workflow.add_conditional_edges("planner", lambda state: END if state.get("status") == "FAILED" else "coder")
    # Single pass: Coder directly goes to Evaluator
    workflow.add_conditional_edges("coder", lambda state: END if state.get("status") == "FAILED" else "evaluator")
    workflow.add_conditional_edges("evaluator", lambda state: END if state.get("status") == "FAILED" else "documentor")
    workflow.add_edge("documentor", END)

    return workflow.compile(checkpointer=memory)

def build_graph_b():
    workflow = StateGraph(DevelopmentState)

    workflow.add_node("requirement", requirement_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("debugger", debugger_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("documentor", documentor_node)

    workflow.set_entry_point("requirement")

    workflow.add_conditional_edges("requirement", lambda state: END if state.get("status") == "FAILED" else "planner")
    workflow.add_conditional_edges("planner", lambda state: END if state.get("status") == "FAILED" else "coder")
    workflow.add_conditional_edges("coder", lambda state: END if state.get("status") == "FAILED" else "tester")
    workflow.add_conditional_edges("tester", lambda state: END if state.get("status") == "FAILED" else "reviewer")

    def route_after_review_with_failure_check(state: DevelopmentState):
        if state.get("status") == "FAILED":
            return END
        return route_after_review(state)

    workflow.add_conditional_edges(
        "reviewer",
        route_after_review_with_failure_check,
        {
            "debugger": "debugger",
            "evaluator": "evaluator",
            END: END
        }
    )

    workflow.add_conditional_edges("debugger", lambda state: END if state.get("status") == "FAILED" else "tester")
    workflow.add_conditional_edges("evaluator", lambda state: END if state.get("status") == "FAILED" else "documentor")
    workflow.add_edge("documentor", END)

    return workflow.compile(checkpointer=memory)

experiment_a_graph = build_graph_a()
experiment_b_graph = build_graph_b()
# Keep development_graph for backwards compatibility if needed, or point it to B
development_graph = experiment_b_graph
