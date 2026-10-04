from app.workflow.state import DevelopmentState

def route_after_review(state: DevelopmentState) -> str:
    if not state:
        return "evaluator"

    test_results = state.get("test_results") or {}
    review_results = state.get("review_results") or {}

    iteration = state.get("iteration") or 1
    max_iterations = state.get("max_iterations") or 5

    # Always route to evaluator when max iterations reached
    if iteration >= max_iterations:
        return "evaluator"

    tests_failed = test_results.get("tests_failed", 0) if isinstance(test_results, dict) else 0
    critical_issues = len(review_results.get("critical_issues") or []) if isinstance(review_results, dict) else 0
    major_issues = len(review_results.get("major_issues") or []) if isinstance(review_results, dict) else 0
    security_issues = len(review_results.get("security_issues") or []) if isinstance(review_results, dict) else 0

    if tests_failed > 0 or critical_issues > 0 or major_issues > 0 or security_issues > 0:
        return "debugger"

    # Quality gate passed
    return "evaluator"
