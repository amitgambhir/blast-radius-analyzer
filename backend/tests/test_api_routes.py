"""
High-level API route tests using FastAPI's TestClient.
LLM calls are mocked at the llm_client.complete level so these run without
any API key and are provider-agnostic.
"""

import concurrent.futures
import sys
import os
import json
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Health ───────────────────────────────────────────────────────────────────


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


# ── Examples endpoints ───────────────────────────────────────────────────────


def test_list_examples():
    r = client.get("/api/examples")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    ids = {ex["id"] for ex in data}
    assert ids == {"db-migration", "api-deprecation", "platform-reorg"}


def test_get_example_db_migration():
    r = client.get("/api/examples/db-migration")
    assert r.status_code == 200
    body = r.json()
    assert (
        body["decision"]["title"]
        == "Migrating user auth database from PostgreSQL to Aurora"
    )
    assert len(body["services"]) == 5
    assert len(body["teams"]) == 3


def test_get_example_api_deprecation():
    r = client.get("/api/examples/api-deprecation")
    assert r.status_code == 200
    body = r.json()
    assert body["decision"]["decision_type"] == "api-change"
    assert len(body["services"]) == 7


def test_get_example_platform_reorg():
    r = client.get("/api/examples/platform-reorg")
    assert r.status_code == 200
    body = r.json()
    assert body["decision"]["decision_type"] == "reorg"


def test_get_example_not_found():
    r = client.get("/api/examples/does-not-exist")
    assert r.status_code == 404


# ── Request validation ───────────────────────────────────────────────────────


def test_analyze_rejects_missing_decision_title():
    """Backend should return 422 if required fields are missing."""
    r = client.post(
        "/api/analyze",
        json={
            "services": [
                {
                    "id": "a",
                    "name": "A",
                    "owner_team": "t",
                    "criticality": "high",
                    "description": "d",
                }
            ],
            "dependencies": [],
            "teams": [
                {
                    "id": "t",
                    "name": "Team",
                    "owns": ["a"],
                    "size": 5,
                    "focus": "product",
                }
            ],
            "decision": {
                # title is missing
                "description": "test",
                "decision_type": "migration",
                "affected_services": ["a"],
                "timeline": "weeks",
                "reversibility": "moderate",
            },
        },
    )
    assert r.status_code == 422


def test_analyze_rejects_invalid_criticality():
    """Invalid enum value for criticality should return 422."""
    r = client.post(
        "/api/analyze",
        json={
            "services": [
                {
                    "id": "a",
                    "name": "A",
                    "owner_team": "t",
                    "criticality": "ultra-critical",
                    "description": "d",
                }
            ],
            "dependencies": [],
            "teams": [],
            "decision": {
                "title": "Test",
                "description": "test",
                "decision_type": "migration",
                "affected_services": [],
                "timeline": "weeks",
                "reversibility": "moderate",
            },
        },
    )
    assert r.status_code == 422


def test_analyze_rejects_invalid_decision_type():
    """Invalid decision_type enum should return 422."""
    r = client.post(
        "/api/analyze",
        json={
            "services": [],
            "dependencies": [],
            "teams": [],
            "decision": {
                "title": "Test",
                "description": "test",
                "decision_type": "INVALID",
                "affected_services": [],
                "timeline": "weeks",
                "reversibility": "moderate",
            },
        },
    )
    assert r.status_code == 422


# ── Analysis with mocked LLM ─────────────────────────────────────────────────

MOCK_PASS1 = {
    "decision_class": "Hard cutover database migration",
    "primary_risk_category": "technical",
    "secondary_risk_categories": ["delivery"],
    "playbook_notes": "Validate connection strings before cutover.",
    "key_concerns": ["Schema compatibility", "Connection pool exhaustion"],
    "blast_radius_prediction": "moderate",
    "critical_path_services": ["auth-service"],
}

MOCK_PASS2 = {
    "directly_affected_impacts": [
        {
            "id": "auth-service",
            "name": "Authentication Service",
            "type": "service",
            "impact_level": "direct",
            "risk_severity": "critical",
            "impact_description": "Database connection strings must be updated.",
            "impact_mechanism": "Connection string change",
            "recommended_actions": ["Update connection strings before cutover"],
            "is_inferred": False,
        }
    ],
    "first_order_impacts": [
        {
            "id": "api-gateway",
            "name": "API Gateway",
            "type": "service",
            "impact_level": "direct",
            "risk_severity": "high",
            "impact_description": "Auth validation may fail during migration window.",
            "impact_mechanism": "sync-api call to auth-service",
            "recommended_actions": ["Implement circuit breaker"],
            "is_inferred": False,
            "dependency_path": "auth-service → api-gateway",
        }
    ],
    "pass2_summary": "2 direct impacts, 1 first-order impact found.",
}

MOCK_PASS3 = {
    "second_order_impacts": [],
    "propagation_patterns": [],
    "pass3_summary": "No second-order propagation identified.",
}

MOCK_PASS4 = {
    "team_impacts": [
        {
            "id": "platform-org",
            "name": "Platform Team — Org Impact",
            "type": "team",
            "impact_level": "direct",
            "risk_severity": "high",
            "impact_description": "Platform team owns migration coordination.",
            "workload_impact": "2-3 engineer-weeks",
            "roadmap_disruption": "Q2 feature work delayed",
            "sla_risk": "99.9% uptime SLA at risk during window",
            "stakeholder_commitments": "None identified",
            "recommended_actions": ["Schedule maintenance window"],
            "is_inferred": False,
            "owns_services": ["auth-service"],
        }
    ],
    "process_impacts": [],
    "external_impacts": [],
    "communication_overhead": "Cross-team coordination required.",
    "change_management_requirements": ["Document rollback plan"],
    "pass4_summary": "Platform team carries primary org impact.",
}

MOCK_PASS5 = {
    "overall_risk_score": 0.72,
    "overall_verdict": "HIGH",
    "executive_summary": "This migration poses HIGH risk due to undocumented direct DB connections.",
    "risk_dimensions": [
        {
            "dimension": "technical",
            "score": 0.8,
            "summary": "Hard cutover risk.",
            "top_risks": ["Schema mismatch"],
            "mitigations": ["Run schema diff"],
        },
        {
            "dimension": "delivery",
            "score": 0.6,
            "summary": "Timeline is tight.",
            "top_risks": ["Rollback complexity"],
            "mitigations": ["Blue-green migration"],
        },
        {
            "dimension": "people",
            "score": 0.4,
            "summary": "Team is experienced.",
            "top_risks": ["On-call fatigue"],
            "mitigations": ["Stagger shifts"],
        },
        {
            "dimension": "compliance",
            "score": 0.3,
            "summary": "No compliance blockers.",
            "top_risks": ["Audit trail gap"],
            "mitigations": ["Log all migration steps"],
        },
        {
            "dimension": "financial",
            "score": 0.5,
            "summary": "Downtime cost moderate.",
            "top_risks": ["Lost revenue during window"],
            "mitigations": ["Off-peak window"],
        },
    ],
    "immediate_actions": [
        "Audit all direct DB connections",
        "Run schema diff",
        "Draft rollback plan",
    ],
    "questions_to_answer": [
        "Are there undocumented direct DB consumers?",
        "What is the rollback SLA?",
    ],
    "confidence_note": "This analysis is grounded in the context you provided. Nodes marked ◈ are inferred.",
}


_PASS_RESPONSES = [
    json.dumps(MOCK_PASS1),
    json.dumps(MOCK_PASS2),
    json.dumps(MOCK_PASS3),
    json.dumps(MOCK_PASS4),
    json.dumps(MOCK_PASS5),
]


def test_analyze_sync_returns_blast_radius_result():
    """
    Full analysis pipeline with mocked LLM calls.
    Verifies the 5-pass orchestration, graph traversal integration, and
    BlastRadiusResult assembly without hitting any real API.
    """
    call_count = 0

    def mock_complete(system, user, max_tokens=2048):
        nonlocal call_count
        resp = _PASS_RESPONSES[call_count]
        call_count += 1
        return resp

    with patch("services.llm_client.complete", side_effect=mock_complete):
        import services.llm_client as lc

        lc.reset()

        r = client.post(
            "/api/analyze",
            json={
                "services": [
                    {
                        "id": "auth-service",
                        "name": "Authentication Service",
                        "owner_team": "platform",
                        "criticality": "critical",
                        "description": "Auth",
                    },
                    {
                        "id": "api-gateway",
                        "name": "API Gateway",
                        "owner_team": "devex",
                        "criticality": "high",
                        "description": "Gateway",
                    },
                    {
                        "id": "user-profile-service",
                        "name": "User Profile",
                        "owner_team": "product",
                        "criticality": "high",
                        "description": "Profile",
                    },
                ],
                "dependencies": [
                    {
                        "from_service": "api-gateway",
                        "to_service": "auth-service",
                        "dependency_type": "sync-api",
                        "strength": "hard",
                    },
                    {
                        "from_service": "auth-service",
                        "to_service": "user-profile-service",
                        "dependency_type": "database",
                        "strength": "hard",
                    },
                ],
                "teams": [
                    {
                        "id": "platform",
                        "name": "Platform",
                        "owns": ["auth-service"],
                        "size": 6,
                        "focus": "platform",
                    },
                    {
                        "id": "devex",
                        "name": "DevEx",
                        "owns": ["api-gateway"],
                        "size": 4,
                        "focus": "platform",
                    },
                ],
                "decision": {
                    "title": "Migrating auth DB to Aurora",
                    "description": "Hard cutover migration",
                    "decision_type": "migration",
                    "affected_services": ["auth-service"],
                    "timeline": "immediate",
                    "reversibility": "hard",
                },
                "additional_context": None,
            },
        )

    assert r.status_code == 200, r.text
    body = r.json()

    # Core result fields
    assert body["overall_verdict"] == "HIGH"
    assert body["overall_risk_score"] == pytest.approx(0.72)
    assert body["decision_title"] == "Migrating auth DB to Aurora"
    assert body["decision_type"] == "migration"

    # 5 risk dimensions
    assert len(body["risk_dimensions"]) == 5
    dims = {d["dimension"] for d in body["risk_dimensions"]}
    assert dims == {"technical", "delivery", "people", "compliance", "financial"}

    # Nodes present (direct + first-order + unaffected)
    assert len(body["nodes"]) > 0
    node_ids = {n["id"] for n in body["nodes"]}
    assert "auth-service" in node_ids
    assert "api-gateway" in node_ids

    # Edges present
    assert len(body["edges"]) > 0

    # Actions and questions
    assert len(body["immediate_actions"]) >= 1
    assert len(body["questions_to_answer"]) >= 1

    # Confidence note always present
    assert body["confidence_note"]

    # Analysis passes log
    assert len(body["analysis_passes"]) == 5
    pass_nums = [p["pass"] for p in body["analysis_passes"]]
    assert pass_nums == [1, 2, 3, 4, 5]

    # LLM called exactly 5 times (once per pass)
    assert call_count == 5


def test_analyze_stream_emits_sse_events():
    """
    SSE streaming endpoint must emit progress + pass_complete + result + complete events.
    """
    _responses = iter(_PASS_RESPONSES)

    with patch(
        "services.llm_client.complete", side_effect=lambda s, u, **kw: next(_responses)
    ):
        import services.llm_client as lc

        lc.reset()

        with client.stream(
            "POST",
            "/api/analyze/stream",
            json={
                "services": [
                    {
                        "id": "svc-a",
                        "name": "Service A",
                        "owner_team": "team-x",
                        "criticality": "high",
                        "description": "d",
                    },
                    {
                        "id": "svc-b",
                        "name": "Service B",
                        "owner_team": "team-x",
                        "criticality": "medium",
                        "description": "d",
                    },
                ],
                "dependencies": [
                    {
                        "from_service": "svc-a",
                        "to_service": "svc-b",
                        "dependency_type": "sync-api",
                        "strength": "hard",
                    },
                ],
                "teams": [
                    {
                        "id": "team-x",
                        "name": "Team X",
                        "owns": ["svc-a", "svc-b"],
                        "size": 4,
                        "focus": "product",
                    },
                ],
                "decision": {
                    "title": "Test decision",
                    "description": "Testing SSE stream",
                    "decision_type": "architecture",
                    "affected_services": ["svc-a"],
                    "timeline": "weeks",
                    "reversibility": "moderate",
                },
                "additional_context": None,
            },
        ) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

            event_types = []
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    event_types.append(event["type"])

    assert "progress" in event_types
    assert "pass_complete" in event_types
    assert "result" in event_types
    assert "complete" in event_types

    result_events = [t for t in event_types if t == "result"]
    assert len(result_events) == 1

    complete_events = [t for t in event_types if t == "complete"]
    assert len(complete_events) == 1


def test_analyze_sync_returns_502_for_invalid_llm_json():
    with patch("services.llm_client.complete", return_value="not-json"):
        import services.llm_client as lc

        lc.reset()

        r = client.post(
            "/api/analyze",
            json={
                "services": [
                    {
                        "id": "svc-a",
                        "name": "Service A",
                        "owner_team": "team-x",
                        "criticality": "high",
                        "description": "d",
                    },
                ],
                "dependencies": [],
                "teams": [
                    {
                        "id": "team-x",
                        "name": "Team X",
                        "owns": ["svc-a"],
                        "size": 4,
                        "focus": "product",
                    },
                ],
                "decision": {
                    "title": "Test decision",
                    "description": "Testing invalid JSON",
                    "decision_type": "architecture",
                    "affected_services": ["svc-a"],
                    "timeline": "weeks",
                    "reversibility": "moderate",
                },
                "additional_context": None,
            },
        )

    assert r.status_code == 502
    assert "invalid JSON" in r.json()["detail"]


def test_analyze_stream_hides_internal_error_details():
    with patch("services.llm_client.complete", return_value="not-json"):
        import services.llm_client as lc

        lc.reset()

        with client.stream(
            "POST",
            "/api/analyze/stream",
            json={
                "services": [
                    {
                        "id": "svc-a",
                        "name": "Service A",
                        "owner_team": "team-x",
                        "criticality": "high",
                        "description": "d",
                    },
                ],
                "dependencies": [],
                "teams": [
                    {
                        "id": "team-x",
                        "name": "Team X",
                        "owns": ["svc-a"],
                        "size": 4,
                        "focus": "product",
                    },
                ],
                "decision": {
                    "title": "Test decision",
                    "description": "Testing invalid JSON",
                    "decision_type": "architecture",
                    "affected_services": ["svc-a"],
                    "timeline": "weeks",
                    "reversibility": "moderate",
                },
                "additional_context": None,
            },
        ) as response:
            assert response.status_code == 200

            error_event = None
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    if event["type"] == "error":
                        error_event = event
                        break

    assert error_event is not None
    assert "detail" not in error_event
    assert "invalid JSON" in error_event["message"]


def test_analyze_rejects_too_many_services():
    services = [
        {
            "id": f"svc-{index}",
            "name": f"Service {index}",
            "owner_team": "team-x",
            "criticality": "high",
            "description": "d",
        }
        for index in range(201)
    ]

    r = client.post(
        "/api/analyze",
        json={
            "services": services,
            "dependencies": [],
            "teams": [
                {
                    "id": "team-x",
                    "name": "Team X",
                    "owns": [],
                    "size": 4,
                    "focus": "product",
                },
            ],
            "decision": {
                "title": "Test",
                "description": "test",
                "decision_type": "migration",
                "affected_services": ["svc-0"],
                "timeline": "weeks",
                "reversibility": "moderate",
            },
        },
    )

    assert r.status_code == 422


def test_request_size_limit_returns_413():
    with client.stream(
        "POST",
        "/api/analyze",
        content="{}",
        headers={"content-length": "999999"},
    ) as response:
        assert response.status_code == 413


def test_analyze_sync_returns_502_for_llm_timeout():
    class TimeoutFuture:
        def result(self, timeout=None):
            raise concurrent.futures.TimeoutError()

        def cancel(self):
            return True

    with patch("services.llm_client._executor.submit", return_value=TimeoutFuture()):
        import services.llm_client as lc

        lc.reset()

        r = client.post(
            "/api/analyze",
            json={
                "services": [
                    {
                        "id": "svc-a",
                        "name": "Service A",
                        "owner_team": "team-x",
                        "criticality": "high",
                        "description": "d",
                    },
                ],
                "dependencies": [],
                "teams": [
                    {
                        "id": "team-x",
                        "name": "Team X",
                        "owns": ["svc-a"],
                        "size": 4,
                        "focus": "product",
                    },
                ],
                "decision": {
                    "title": "Test decision",
                    "description": "Testing timeout handling",
                    "decision_type": "architecture",
                    "affected_services": ["svc-a"],
                    "timeline": "weeks",
                    "reversibility": "moderate",
                },
                "additional_context": None,
            },
        )

    assert r.status_code == 502
    assert "timeout" in r.json()["detail"].lower()
