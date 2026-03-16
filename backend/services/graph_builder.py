"""
NetworkX graph builder and traversal utilities.
Builds a real directed dependency graph from intake data.
The traversal logic is production-ready — only the data source changes in production.
"""

from typing import List, Set
import networkx as nx

from models.intake import Service, Dependency


def build_graph(services: List[Service], dependencies: List[Dependency]) -> nx.DiGraph:
    G = nx.DiGraph()
    for service in services:
        G.add_node(
            service.id,
            name=service.name,
            owner_team=service.owner_team,
            criticality=service.criticality,
            description=service.description,
        )
    for dep in dependencies:
        if dep.from_service in G and dep.to_service in G:
            G.add_edge(
                dep.from_service,
                dep.to_service,
                type=dep.dependency_type,
                strength=dep.strength,
            )
    return G


def get_first_order(G: nx.DiGraph, affected_ids: List[str]) -> Set[str]:
    """All services exactly 1 hop from any affected service (predecessors + successors)."""
    affected_set = set(affected_ids)
    neighbors: Set[str] = set()
    for sid in affected_ids:
        if sid in G:
            neighbors.update(G.predecessors(sid))
            neighbors.update(G.successors(sid))
    return neighbors - affected_set


def get_second_order(
    G: nx.DiGraph, affected_ids: List[str], first_order_ids: Set[str]
) -> Set[str]:
    """All services 2 hops from any affected service, not already in 1-hop or directly affected."""
    affected_set = set(affected_ids)
    second: Set[str] = set()
    for sid in first_order_ids:
        if sid in G:
            second.update(G.predecessors(sid))
            second.update(G.successors(sid))
    return second - affected_set - first_order_ids


def compute_centrality(G: nx.DiGraph) -> dict:
    """Betweenness centrality for all nodes — identifies dependency hubs."""
    if G.number_of_nodes() == 0:
        return {}
    return nx.betweenness_centrality(G)


def get_graph_data(G: nx.DiGraph) -> dict:
    """Graph metadata for prompt context."""
    return {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "centrality": compute_centrality(G),
    }


def get_services_by_ids(services: List[Service], ids: Set[str]) -> List[dict]:
    """Filter services to those with given ids, returned as dicts for prompt serialization."""
    return [s.model_dump() for s in services if s.id in ids]
