import pytest
from app.workflow.routing import (
    calculate_confidence_score,
    evaluate_routing,
    route_after_review,
    CONFIDENCE_THRESHOLD
)

def test_confidence_score_perfect():
    state = {
        "test_results": {"tests_total": 5, "tests_passed": 5, "tests_failed": 0, "pass_rate": 100.0},
        "review_results": {
            "status": "PASS",
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": [],
            "security_issues": [],
            "missing_requirements": []
        }
    }
    score = calculate_confidence_score(state)
    assert score == 100.0

def test_confidence_score_with_test_failures():
    state = {
        "test_results": {"tests_total": 5, "tests_passed": 3, "tests_failed": 2, "pass_rate": 60.0},
        "review_results": {
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": [],
            "security_issues": []
        }
    }
    score = calculate_confidence_score(state)
    # 100 - (2 * 15) = 70.0
    assert score == 70.0

def test_confidence_score_with_security_and_critical_issues():
    state = {
        "test_results": {"tests_total": 10, "tests_passed": 10, "tests_failed": 0, "pass_rate": 100.0},
        "review_results": {
            "critical_issues": ["SQL injection vulnerability"],
            "security_issues": ["Hardcoded secret"],
            "major_issues": ["Missing endpoint"],
            "minor_issues": ["Formatting issue"]
        }
    }
    score = calculate_confidence_score(state)
    # 100 - 25 (critical) - 20 (security) - 10 (major) - 2.5 (minor) = 42.5
    assert score == 42.5

def test_evaluate_routing_pass_gate():
    state = {
        "iteration": 1,
        "max_iterations": 5,
        "test_results": {"tests_total": 5, "tests_passed": 5, "tests_failed": 0, "pass_rate": 100.0},
        "review_results": {
            "status": "PASS",
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": [],
            "security_issues": []
        }
    }
    decision = evaluate_routing(state)
    assert decision["route"] == "evaluator"
    assert decision["quality_gate_passed"] is True
    assert decision["confidence_score"] >= CONFIDENCE_THRESHOLD

def test_evaluate_routing_blocks_on_failing_tests():
    state = {
        "iteration": 1,
        "max_iterations": 5,
        "test_results": {"tests_total": 5, "tests_passed": 4, "tests_failed": 1},
        "review_results": {"critical_issues": [], "major_issues": [], "security_issues": []}
    }
    decision = evaluate_routing(state)
    assert decision["route"] == "debugger"
    assert decision["quality_gate_passed"] is False

def test_evaluate_routing_blocks_on_security_issues():
    state = {
        "iteration": 1,
        "max_iterations": 5,
        "test_results": {"tests_total": 5, "tests_passed": 5, "tests_failed": 0},
        "review_results": {
            "critical_issues": [],
            "major_issues": [],
            "security_issues": ["Unvalidated user input"]
        }
    }
    decision = evaluate_routing(state)
    assert decision["route"] == "debugger"
    assert decision["quality_gate_passed"] is False

def test_evaluate_routing_max_iterations_forces_evaluator():
    state = {
        "iteration": 5,
        "max_iterations": 5,
        "test_results": {"tests_total": 5, "tests_passed": 2, "tests_failed": 3},
        "review_results": {
            "critical_issues": ["Persistent error"],
            "security_issues": []
        }
    }
    decision = evaluate_routing(state)
    assert decision["route"] == "evaluator"
    assert decision["quality_gate_passed"] is False
    assert any("Maximum iterations reached" in r for r in decision["reasons"])

def test_route_after_review_enriches_state():
    state = {
        "iteration": 1,
        "max_iterations": 5,
        "test_results": {"tests_total": 4, "tests_passed": 4, "tests_failed": 0},
        "review_results": {
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": [],
            "security_issues": []
        }
    }
    route = route_after_review(state)
    assert route == "evaluator"
    assert state.get("confidence_score") == 100.0
    assert state.get("routing_metadata") is not None
    assert state["routing_metadata"]["route"] == "evaluator"
