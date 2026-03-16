"""Unit tests for the NetworkX graph builder and traversal utilities."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models.intake import Service, Dependency
from services.graph_builder import (
    build_graph,
    get_first_order,
    get_second_order,
    compute_centrality,
    get_services_by_ids,
)


@pytest.fixture
def sample_services():
    return [
        Service(id="auth", name="Auth Service", owner_team="platform", criticality="critical", description="Auth"),
        Service(id="profile", name="Profile Service", owner_team="product", criticality="high", description="Profile"),
        Service(id="gateway", name="API Gateway", owner_team="devex", criticality="high", description="Gateway"),
        Service(id="notify", name="Notification Service", owner_team="devex", criticality="medium", description="Notify"),
        Service(id="billing", name="Billing Service", owner_team="payments", criticality="high", description="Billing"),
    ]


@pytest.fixture
def sample_deps():
    return [
        Dependency(from_service="gateway", to_service="auth", dependency_type="sync-api", strength="hard"),
        Dependency(from_service="auth", to_service="profile", dependency_type="database", strength="hard"),
        Dependency(from_service="notify", to_service="profile", dependency_type="async-event", strength="soft"),
        Dependency(from_service="billing", to_service="auth", dependency_type="sync-api", strength="hard"),
    ]


def test_build_graph(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    assert G.number_of_nodes() == 5
    assert G.number_of_edges() == 4
    assert "auth" in G
    assert G["gateway"]["auth"]["type"] == "sync-api"


def test_get_first_order_single_affected(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    # auth is affected — first order: gateway, profile, billing (all direct neighbors)
    first = get_first_order(G, ["auth"])
    assert "gateway" in first
    assert "profile" in first
    assert "billing" in first
    assert "auth" not in first


def test_get_first_order_excludes_affected(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    first = get_first_order(G, ["auth", "profile"])
    assert "auth" not in first
    assert "profile" not in first
    assert "gateway" in first


def test_get_second_order(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    affected = ["auth"]
    first = get_first_order(G, affected)
    second = get_second_order(G, affected, first)
    # auth's first-order includes profile, gateway, billing
    # second-order from profile → notify
    assert "notify" in second
    assert "auth" not in second


def test_centrality(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    centrality = compute_centrality(G)
    # auth is the hub — should have highest centrality
    assert "auth" in centrality
    assert centrality["auth"] >= centrality["notify"]


def test_get_services_by_ids(sample_services, sample_deps):
    result = get_services_by_ids(sample_services, {"auth", "profile"})
    ids = [s["id"] for s in result]
    assert "auth" in ids
    assert "profile" in ids
    assert "gateway" not in ids


def test_empty_graph():
    G = build_graph([], [])
    assert G.number_of_nodes() == 0
    first = get_first_order(G, ["nonexistent"])
    assert first == set()


def test_unknown_affected_service(sample_services, sample_deps):
    G = build_graph(sample_services, sample_deps)
    first = get_first_order(G, ["does-not-exist"])
    assert first == set()
