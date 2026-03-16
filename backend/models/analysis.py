from typing import List, Literal, Dict, Any
from pydantic import BaseModel


class ImpactNode(BaseModel):
    id: str
    name: str
    type: Literal["decision", "service", "team", "process", "external"]
    impact_level: Literal["direct", "second-order", "third-order", "unaffected"]
    risk_severity: Literal["critical", "high", "medium", "low", "none"]
    impact_description: str
    recommended_actions: List[str]
    is_inferred: bool


class ImpactEdge(BaseModel):
    source: str
    target: str
    relationship: str
    strength: float  # 0.0–1.0


class RiskDimension(BaseModel):
    dimension: Literal["technical", "delivery", "people", "compliance", "financial"]
    score: float  # 0.0–1.0
    summary: str
    top_risks: List[str]
    mitigations: List[str]


class BlastRadiusResult(BaseModel):
    decision_title: str
    decision_type: str
    overall_risk_score: float
    overall_verdict: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    executive_summary: str
    nodes: List[ImpactNode]
    edges: List[ImpactEdge]
    risk_dimensions: List[RiskDimension]
    immediate_actions: List[str]
    questions_to_answer: List[str]
    confidence_note: str
    analysis_passes: List[Dict[str, Any]]
