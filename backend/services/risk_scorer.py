"""Pass 5 — Risk Scoring and Synthesis"""
import logging

from models.analysis import BlastRadiusResult, ImpactNode, ImpactEdge, RiskDimension
import services.llm_client as llm_client
from services.errors import LLMOutputError
from utils.llm_json import parse_llm_json
from utils.prompts import PASS5_SYSTEM, pass5_user

logger = logging.getLogger(__name__)


def score_and_synthesize(
    request_dict: dict,
    pass1: dict,
    pass2: dict,
    pass3: dict,
    pass4: dict,
    all_nodes: list,
    all_edges: list,
) -> BlastRadiusResult:
    """Run Pass 5: synthesize everything into a BlastRadiusResult."""
    text = llm_client.complete(
        PASS5_SYSTEM,
        pass5_user(request_dict, pass1, pass2, pass3, pass4, all_nodes),
        max_tokens=8192,
    )
    synthesis = parse_llm_json(text, "risk scoring and synthesis")

    nodes = _build_nodes(request_dict, pass2, pass3, pass4)
    edges = _build_edges(request_dict)

    risk_dims = []
    for rd in synthesis.get("risk_dimensions", []):
        try:
            risk_dims.append(RiskDimension(**rd))
        except Exception:
            logger.warning("Skipping invalid risk dimension payload: %s", rd, exc_info=True)

    overall_risk_score = synthesis.get("overall_risk_score", 0.5)
    try:
        overall_risk_score = float(overall_risk_score)
    except (TypeError, ValueError) as exc:
        raise LLMOutputError(
            "Analysis failed during risk scoring and synthesis because the model returned an invalid risk score. Please retry."
        ) from exc

    return BlastRadiusResult(
        decision_title=request_dict["decision"]["title"],
        decision_type=request_dict["decision"]["decision_type"],
        overall_risk_score=overall_risk_score,
        overall_verdict=synthesis.get("overall_verdict", "MODERATE"),
        executive_summary=synthesis.get("executive_summary", ""),
        nodes=nodes,
        edges=edges,
        risk_dimensions=risk_dims,
        immediate_actions=synthesis.get("immediate_actions", []),
        questions_to_answer=synthesis.get("questions_to_answer", []),
        confidence_note=synthesis.get(
            "confidence_note",
            "This analysis is grounded in the context you provided. "
            "Nodes marked ◈ are inferred — not explicitly defined in your intake. "
            "In production, connect Backstage, PagerDuty, and your org chart to replace "
            "manual intake with live data.",
        ),
        analysis_passes=[
            {"pass": 1, "name": "Decision Classification", "output": pass1},
            {"pass": 2, "name": "First-Order Impact", "output": pass2},
            {"pass": 3, "name": "Second-Order Propagation", "output": pass3},
            {"pass": 4, "name": "Organizational Impact", "output": pass4},
            {"pass": 5, "name": "Risk Scoring & Synthesis", "output": synthesis},
        ],
    )


def _build_nodes(request_dict: dict, pass2: dict, pass3: dict, pass4: dict) -> list:
    nodes = []
    seen: set = set()

    def add(n: dict):
        nid = n.get("id")
        if not nid or nid in seen:
            return
        seen.add(nid)
        try:
            nodes.append(
                ImpactNode(
                    id=nid,
                    name=n.get("name", nid),
                    type=n.get("type", "service"),
                    impact_level=n.get("impact_level", "direct"),
                    risk_severity=n.get("risk_severity", "medium"),
                    impact_description=n.get("impact_description", ""),
                    recommended_actions=n.get("recommended_actions", []),
                    is_inferred=bool(n.get("is_inferred", False)),
                )
            )
        except Exception:
            logger.warning("Skipping invalid impact node payload: %s", n, exc_info=True)

    for n in pass2.get("directly_affected_impacts", []):
        add(n)
    for n in pass2.get("first_order_impacts", []):
        add(n)
    for n in pass3.get("second_order_impacts", []):
        add(n)
    for n in pass4.get("team_impacts", []):
        add(n)
    for n in pass4.get("process_impacts", []):
        add(n)
    for n in pass4.get("external_impacts", []):
        add(n)

    # Add unaffected services
    for svc in request_dict["services"]:
        if svc["id"] not in seen:
            nodes.append(
                ImpactNode(
                    id=svc["id"],
                    name=svc["name"],
                    type="service",
                    impact_level="unaffected",
                    risk_severity="none",
                    impact_description="Not directly impacted by this decision based on dependency analysis.",
                    recommended_actions=[],
                    is_inferred=False,
                )
            )
            seen.add(svc["id"])

    return nodes


def _build_edges(request_dict: dict) -> list:
    edges = []
    seen: set = set()

    for dep in request_dict["dependencies"]:
        key = (dep["from_service"], dep["to_service"])
        if key in seen:
            continue
        seen.add(key)
        strength = 0.9 if dep["strength"] == "hard" else 0.4
        edges.append(
            ImpactEdge(
                source=dep["from_service"],
                target=dep["to_service"],
                relationship=dep["dependency_type"],
                strength=strength,
            )
        )

    return edges
