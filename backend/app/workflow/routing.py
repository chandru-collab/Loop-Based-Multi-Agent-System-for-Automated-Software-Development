import logging
from typing import Dict, Any, List
from app.workflow.state import DevelopmentState

logger = logging.getLogger(__name__)

# Quality threshold: minimum confidence score required to pass quality gate without debugging
CONFIDENCE_THRESHOLD = 80.0

def calculate_confidence_score(state: DevelopmentState) -> float:
    """
    Computes an empirical confidence score (0.0 to 100.0) based on:
    - Test execution results (pass rate and failure penalties)
    - Security vulnerabilities (critical risk penalty)
    - Code review issues (critical, major, and minor defects)
    - Missing requirements
    """
    if not state:
        return 100.0

    test_results = state.get("test_results") or {}
    review_results = state.get("review_results") or {}

    score = 100.0

    # 1. Test results impact
    if isinstance(test_results, dict):
        tests_failed = test_results.get("tests_failed", 0)
        tests_total = test_results.get("tests_total", 0)
        pass_rate = test_results.get("pass_rate")

        if tests_failed > 0:
            score -= tests_failed * 15.0
        elif pass_rate is not None and tests_total > 0:
            pass_ratio = pass_rate / 100.0 if pass_rate > 1.0 else pass_rate
            score -= (1.0 - pass_ratio) * 20.0

    # 2. Review results impact
    if isinstance(review_results, dict):
        critical_issues = len(review_results.get("critical_issues") or [])
        security_issues = len(review_results.get("security_issues") or [])
        major_issues = len(review_results.get("major_issues") or [])
        minor_issues = len(review_results.get("minor_issues") or [])
        missing_reqs = len(review_results.get("missing_requirements") or [])

        score -= critical_issues * 25.0
        score -= security_issues * 20.0
        score -= major_issues * 10.0
        score -= minor_issues * 2.5
        score -= missing_reqs * 15.0

    return max(0.0, min(100.0, round(score, 1)))

def evaluate_routing(state: DevelopmentState) -> Dict[str, Any]:
    """
    Evaluates current state against quality gates and confidence thresholds.
    Returns detailed decision metadata.
    """
    if not state:
        return {
            "route": "evaluator",
            "confidence_score": 100.0,
            "threshold": CONFIDENCE_THRESHOLD,
            "quality_gate_passed": True,
            "reasons": ["Empty state, defaulting to evaluator"],
            "breakdown": {}
        }

    iteration = state.get("iteration") or 1
    max_iterations = state.get("max_iterations") or 5
    test_results = state.get("test_results") or {}
    review_results = state.get("review_results") or {}

    tests_failed = test_results.get("tests_failed", 0) if isinstance(test_results, dict) else 0
    critical_issues = len(review_results.get("critical_issues") or []) if isinstance(review_results, dict) else 0
    security_issues = len(review_results.get("security_issues") or []) if isinstance(review_results, dict) else 0
    major_issues = len(review_results.get("major_issues") or []) if isinstance(review_results, dict) else 0
    minor_issues = len(review_results.get("minor_issues") or []) if isinstance(review_results, dict) else 0
    missing_reqs = len(review_results.get("missing_requirements") or []) if isinstance(review_results, dict) else 0

    confidence = calculate_confidence_score(state)
    reasons: List[str] = []

    breakdown = {
        "tests_failed": tests_failed,
        "critical_issues": critical_issues,
        "security_issues": security_issues,
        "major_issues": major_issues,
        "minor_issues": minor_issues,
        "missing_requirements": missing_reqs
    }

    # Condition 1: Max iterations limit reached
    if iteration >= max_iterations:
        reasons.append(f"Maximum iterations reached ({iteration}/{max_iterations}). Forcing progression to Evaluator.")
        return {
            "route": "evaluator",
            "confidence_score": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "quality_gate_passed": False,
            "reasons": reasons,
            "breakdown": breakdown
        }

    # Condition 2: Blocking defects
    blocking_defects = []
    if tests_failed > 0:
        blocking_defects.append(f"{tests_failed} test failure(s)")
    if critical_issues > 0:
        blocking_defects.append(f"{critical_issues} critical issue(s)")
    if security_issues > 0:
        blocking_defects.append(f"{security_issues} security vulnerability(ies)")
    if major_issues > 0:
        blocking_defects.append(f"{major_issues} major issue(s)")

    if blocking_defects:
        reasons.append(f"Blocking defects found ({', '.join(blocking_defects)}). Routing to Debugger for repair.")
        return {
            "route": "debugger",
            "confidence_score": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "quality_gate_passed": False,
            "reasons": reasons,
            "breakdown": breakdown
        }

    # Condition 3: Confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        reasons.append(f"Confidence score {confidence}% is below threshold {CONFIDENCE_THRESHOLD}%. Routing to Debugger for refinement.")
        return {
            "route": "debugger",
            "confidence_score": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "quality_gate_passed": False,
            "reasons": reasons,
            "breakdown": breakdown
        }

    # Condition 4: Quality gate satisfied with high confidence
    reasons.append(f"Quality gate passed with high confidence ({confidence}% >= {CONFIDENCE_THRESHOLD}%). Routing to Evaluator.")
    return {
        "route": "evaluator",
        "confidence_score": confidence,
        "threshold": CONFIDENCE_THRESHOLD,
        "quality_gate_passed": True,
        "reasons": reasons,
        "breakdown": breakdown
    }

def route_after_review(state: DevelopmentState) -> str:
    """
    Adaptive, confidence-based router used by LangGraph conditional edges.
    Routes to 'evaluator' if quality gate is met with high confidence (or max iterations reached),
    or 'debugger' if automated repairs are required.
    """
    decision = evaluate_routing(state)
    logger.info(
        f"[Confidence-Based Router] Route: {decision['route']} | "
        f"Score: {decision['confidence_score']}% | Reasons: {'; '.join(decision['reasons'])}"
    )

    if isinstance(state, dict):
        state["confidence_score"] = decision["confidence_score"]
        state["routing_metadata"] = decision

    return decision["route"]

