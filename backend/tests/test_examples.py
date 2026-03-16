"""
Tests for all 3 example scenarios — validating the data model and graph traversal
without calling the Claude API.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from routers.examples import EXAMPLES
from services.graph_builder import (
    build_graph,
    get_first_order,
    get_second_order,
    compute_centrality,
)


@pytest.mark.parametrize("example_id", ["db-migration", "api-deprecation", "platform-reorg"])
def test_example_loads(example_id):
    """All 3 examples must be present and parseable."""
    assert example_id in EXAMPLES
    req = EXAMPLES[example_id]
    assert len(req.services) > 0
    assert len(req.dependencies) > 0
    assert len(req.teams) > 0
    assert req.decision.title


@pytest.mark.parametrize("example_id", ["db-migration", "api-deprecation", "platform-reorg"])
def test_example_graph_builds(example_id):
    """Graph must build from each example without errors."""
    req = EXAMPLES[example_id]
    G = build_graph(req.services, req.dependencies)
    assert G.number_of_nodes() == len(req.services)
    assert G.number_of_edges() == len(req.dependencies)


@pytest.mark.parametrize("example_id", ["db-migration", "api-deprecation", "platform-reorg"])
def test_example_service_ids_are_valid(example_id):
    """All dependency service IDs must reference existing services."""
    req = EXAMPLES[example_id]
    service_ids = {s.id for s in req.services}
    for dep in req.dependencies:
        assert dep.from_service in service_ids, (
            f"{example_id}: dep.from_service '{dep.from_service}' not in services"
        )
        assert dep.to_service in service_ids, (
            f"{example_id}: dep.to_service '{dep.to_service}' not in services"
        )


@pytest.mark.parametrize("example_id", ["db-migration", "api-deprecation", "platform-reorg"])
def test_example_team_ownership_is_valid(example_id):
    """All team-owned service IDs must reference existing services."""
    req = EXAMPLES[example_id]
    service_ids = {s.id for s in req.services}
    for team in req.teams:
        for svc_id in team.owns:
            assert svc_id in service_ids, (
                f"{example_id}: team '{team.id}' owns '{svc_id}' which is not a service"
            )


@pytest.mark.parametrize("example_id", ["db-migration", "api-deprecation", "platform-reorg"])
def test_example_affected_services_exist(example_id):
    """Decision affected_services must all reference existing services."""
    req = EXAMPLES[example_id]
    service_ids = {s.id for s in req.services}
    for sid in req.decision.affected_services:
        assert sid in service_ids, (
            f"{example_id}: affected_service '{sid}' not in services"
        )


# ── DB Migration specific ────────────────────────────────────────────────────

def test_db_migration_critical_services():
    """auth-service and session-manager should be critical in db-migration."""
    req = EXAMPLES["db-migration"]
    critical = {s.id for s in req.services if s.criticality == "critical"}
    assert "auth-service" in critical
    assert "session-manager" in critical


def test_db_migration_first_order_graph():
    """
    In db-migration, auth-service is affected.
    api-gateway and session-manager call auth-service (hard sync-api), so they
    should be in first-order.
    user-profile-service is called by auth-service (database), also first-order.
    """
    req = EXAMPLES["db-migration"]
    G = build_graph(req.services, req.dependencies)
    first = get_first_order(G, ["auth-service"])
    assert "api-gateway" in first, "api-gateway calls auth-service, must be first-order"
    assert "session-manager" in first, "session-manager calls auth-service, must be first-order"
    assert "user-profile-service" in first, "auth-service calls user-profile-service, must be first-order"


def test_db_migration_second_order_graph():
    """
    notification-service depends on user-profile-service (async-event).
    user-profile-service is first-order from auth-service, so notification-service is second-order.
    """
    req = EXAMPLES["db-migration"]
    G = build_graph(req.services, req.dependencies)
    affected = ["auth-service"]
    first = get_first_order(G, affected)
    assert "user-profile-service" in first, "user-profile-service must be first-order from auth-service"
    second = get_second_order(G, affected, first)
    assert "notification-service" in second, (
        "notification-service is async-event consumer of user-profile-service, must be second-order"
    )


def test_db_migration_auth_is_hub():
    """auth-service should have highest betweenness centrality in db-migration graph."""
    req = EXAMPLES["db-migration"]
    G = build_graph(req.services, req.dependencies)
    centrality = compute_centrality(G)
    auth_c = centrality.get("auth-service", 0)
    for svc_id, c in centrality.items():
        if svc_id != "auth-service":
            assert auth_c >= c, (
                f"auth-service (centrality={auth_c:.3f}) should be >= {svc_id} ({c:.3f})"
            )


# ── API Deprecation specific ─────────────────────────────────────────────────

def test_api_deprecation_payments_v1_has_hard_consumers():
    """payments-v1 must have hard-dependency consumers (checkout, billing, mobile, partner)."""
    req = EXAMPLES["api-deprecation"]
    hard_consumers = {
        d.from_service for d in req.dependencies
        if d.to_service == "payments-v1" and d.strength == "hard"
    }
    assert "checkout-service" in hard_consumers
    assert "billing-service" in hard_consumers
    assert "mobile-app-backend" in hard_consumers
    assert "partner-integration-layer" in hard_consumers


def test_api_deprecation_first_order_is_wide():
    """payments-v1 deprecation should have 4+ first-order impacts."""
    req = EXAMPLES["api-deprecation"]
    G = build_graph(req.services, req.dependencies)
    first = get_first_order(G, ["payments-v1"])
    assert len(first) >= 4, f"Expected 4+ first-order services, got {len(first)}: {first}"


# ── Platform Reorg specific ──────────────────────────────────────────────────

def test_platform_reorg_no_code_changes():
    """Platform reorg is decision_type='reorg', not 'migration' or 'architecture'."""
    req = EXAMPLES["platform-reorg"]
    assert req.decision.decision_type == "reorg"


def test_platform_reorg_many_affected_services():
    """Reorg affects 6 platform-owned services."""
    req = EXAMPLES["platform-reorg"]
    assert len(req.decision.affected_services) == 6


def test_platform_reorg_product_services_are_second_order():
    """
    auth-service and payments-core are owned by Product team and depend
    on platform services. They should be reachable via second-order traversal.
    """
    req = EXAMPLES["platform-reorg"]
    G = build_graph(req.services, req.dependencies)
    affected = req.decision.affected_services
    first = get_first_order(G, affected)
    second = get_second_order(G, affected, first)
    reachable = set(affected) | first | second
    assert "auth-service" in reachable, "auth-service must be reachable from platform services"
    assert "payments-core" in reachable, "payments-core must be reachable from platform services"
