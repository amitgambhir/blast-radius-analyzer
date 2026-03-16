"""
All Claude prompts for the 5-pass blast radius analysis engine.
Isolated here for easy tuning and documentation.
"""
import json

SYSTEM_BASE = """You are a senior engineering architect and risk analyst specializing in blast radius analysis — mapping the second and third-order impacts of engineering decisions before they are made.

Your analysis is grounded in specific system context provided by the user. You reason carefully about technical, organizational, and process impacts. You distinguish between what is explicitly stated in the context versus what you are inferring.

CRITICAL RULE: Return ONLY valid JSON. No markdown code fences. No preamble. No explanation outside the JSON. Pure JSON only."""


# ─────────────────────────────────────────────
# PASS 1 — Decision Classification
# ─────────────────────────────────────────────

PASS1_SYSTEM = SYSTEM_BASE + """

Pass 1 — Decision Classification
Classify the decision type, identify the primary risk category, and determine which analysis approach to apply. Your output will be used as context for all subsequent passes."""


def pass1_user(req: dict) -> str:
    d = req["decision"]
    services_summary = [f"{s['id']} ({s['criticality']})" for s in req["services"]]
    teams_summary = [f"{t['id']} owns: {', '.join(t['owns'])}" for t in req["teams"]]
    return f"""Analyze and classify this engineering decision.

DECISION:
Title: {d['title']}
Type: {d['decision_type']}
Description: {d['description']}
Timeline: {d['timeline']}
Reversibility: {d['reversibility']}
Directly affected services: {d['affected_services']}

SYSTEM CONTEXT:
Services: {_j(services_summary)}
Teams: {_j(teams_summary)}
Additional context: {req.get('additional_context') or 'None provided'}

Return exactly this JSON structure:
{{
  "decision_class": "refined specific classification e.g. 'Hard-cutover database migration during maintenance window with undocumented direct DB connections'",
  "primary_risk_category": "technical|delivery|people|compliance|financial",
  "secondary_risk_categories": ["other applicable categories"],
  "playbook_notes": "Specific considerations and gotchas for this exact decision type — not generic advice",
  "key_concerns": ["3-5 specific, concrete concerns grounded in the decision details"],
  "blast_radius_prediction": "narrow|moderate|wide|organization-wide",
  "critical_path_services": ["service ids most likely on the critical path"]
}}"""


# ─────────────────────────────────────────────
# PASS 2 — First-Order Impact
# ─────────────────────────────────────────────

PASS2_SYSTEM = SYSTEM_BASE + """

Pass 2 — First-Order Technical Impact Analysis
Analyze the direct (1-hop) technical impacts on services immediately connected to the affected services.
NetworkX graph traversal has already computed which services are 1 hop away. You are reasoning about the specific impact on each."""


def _trim_svc(s: dict, desc_limit: int = 300) -> dict:
    """Return a service dict with description trimmed for prompt efficiency."""
    if not s.get("description") or len(s["description"]) <= desc_limit:
        return s
    return {**s, "description": s["description"][:desc_limit] + "…"}


def pass2_user(req: dict, pass1: dict, first_order_svcs: list, graph_data: dict) -> str:
    affected = req["decision"]["affected_services"]
    affected_details = [_trim_svc(s) for s in req["services"] if s["id"] in affected]
    first_order_svcs = [_trim_svc(s) for s in first_order_svcs]
    relevant_deps = [
        d for d in req["dependencies"]
        if d["from_service"] in affected or d["to_service"] in affected
        or d["from_service"] in {s["id"] for s in first_order_svcs}
        or d["to_service"] in {s["id"] for s in first_order_svcs}
    ]
    return f"""Analyze first-order technical impacts.

PASS 1 FINDINGS:
Class: {pass1.get('decision_class')}
Primary risk: {pass1.get('primary_risk_category')}
Key concerns: {_j(pass1.get('key_concerns', []))}

DIRECTLY AFFECTED SERVICES (the decision targets):
{_j(affected_details)}

FIRST-ORDER NEIGHBORS (1-hop, computed by NetworkX graph traversal):
{_j(first_order_svcs)}

RELEVANT DEPENDENCIES:
{_j(relevant_deps)}

DECISION DESCRIPTION: {req['decision']['description']}
TIMELINE: {req['decision']['timeline']} | REVERSIBILITY: {req['decision']['reversibility']}
ADDITIONAL CONTEXT: {req.get('additional_context') or 'None'}

For each directly affected service AND each first-order neighbor, analyze the specific technical impact.
Set is_inferred=false for services explicitly listed in the intake.

Return exactly this JSON structure:
{{
  "directly_affected_impacts": [
    {{
      "id": "service-id",
      "name": "Service Name",
      "type": "service",
      "impact_level": "direct",
      "risk_severity": "critical|high|medium|low",
      "impact_description": "Specific description of how this service is impacted — what breaks, what degrades, what must change",
      "impact_mechanism": "exact technical mechanism: schema change, connection string update, API contract break, etc.",
      "recommended_actions": ["specific action 1", "specific action 2"],
      "is_inferred": false
    }}
  ],
  "first_order_impacts": [
    {{
      "id": "service-id",
      "name": "Service Name",
      "type": "service",
      "impact_level": "direct",
      "risk_severity": "critical|high|medium|low",
      "impact_description": "Specific description of propagated impact",
      "impact_mechanism": "how impact travels from affected service to this one",
      "recommended_actions": ["specific action"],
      "is_inferred": false,
      "dependency_path": "affected-service-id → this-service-id"
    }}
  ],
  "pass2_summary": "1-2 sentence summary of first-order technical blast radius"
}}"""


# ─────────────────────────────────────────────
# PASS 3 — Second-Order Propagation
# ─────────────────────────────────────────────

PASS3_SYSTEM = SYSTEM_BASE + """

Pass 3 — Second-Order Propagation Analysis
Analyze how first-order impacts propagate to second-order services (2 hops from affected services).
Reason about whether each impact signal is dampened (soft/async) or amplified (hard/sync) as it travels."""


def pass3_user(req: dict, pass1: dict, pass2: dict, second_order_svcs: list) -> str:
    high_sev = [
        i["id"] + ": " + i.get("impact_description", "")[:80]
        for i in (pass2.get("directly_affected_impacts", []) + pass2.get("first_order_impacts", []))
        if i.get("risk_severity") in ("critical", "high")
    ]
    second_order_svcs = [_trim_svc(s) for s in second_order_svcs]
    second_order_ids = {s["id"] for s in second_order_svcs}
    first_order_ids = {
        i["id"]
        for i in (pass2.get("directly_affected_impacts", []) + pass2.get("first_order_impacts", []))
    }
    relevant_ids = second_order_ids | first_order_ids
    relevant_deps = [
        d for d in req["dependencies"]
        if d["from_service"] in relevant_ids or d["to_service"] in relevant_ids
    ]
    return f"""Analyze second-order impact propagation.

PASS 1: {pass1.get('decision_class')} — {pass1.get('primary_risk_category')} risk
PASS 2 HIGH-SEVERITY FIRST-ORDER IMPACTS:
{_j(high_sev)}
PASS 2 SUMMARY: {pass2.get('pass2_summary', '')}

SECOND-ORDER SERVICES (2-hop, computed by NetworkX):
{_j(second_order_svcs)}

RELEVANT DEPENDENCIES (involving first- or second-order services):
{_j(relevant_deps)}

DECISION: {req['decision']['title']}
TIMELINE: {req['decision']['timeline']}

For each second-order service: which first-order service carries the impact here, is it dampened or amplified, and what is the specific mechanism?

Return exactly this JSON structure:
{{
  "second_order_impacts": [
    {{
      "id": "service-id",
      "name": "Service Name",
      "type": "service",
      "impact_level": "second-order",
      "risk_severity": "critical|high|medium|low|none",
      "impact_description": "Specific description of second-order impact",
      "propagation_vector": "first-order-service-id that carries impact here",
      "propagation_mechanism": "dampened|amplified|lateral",
      "dampening_factors": ["why impact is reduced, if dampened"],
      "amplification_factors": ["why impact grows, if amplified"],
      "recommended_actions": ["specific action"],
      "is_inferred": false
    }}
  ],
  "propagation_patterns": [
    {{
      "pattern": "description of a propagation pattern observed",
      "severity": "critical|high|medium|low",
      "services_involved": ["service ids"]
    }}
  ],
  "pass3_summary": "1-2 sentence summary of second-order propagation dynamics"
}}"""


# ─────────────────────────────────────────────
# PASS 4 — Organizational Impact
# ─────────────────────────────────────────────

PASS4_SYSTEM = SYSTEM_BASE + """

Pass 4 — Organizational Impact Mapping
This is the differentiator pass. Most tools stop at technical impact.
Map technical impacts to human and organizational impacts: team workload, roadmap disruption, SLA risks, stakeholder commitments, communication overhead, morale.
Be specific about which teams are affected and how. This is what a Staff Engineer or Engineering Manager actually needs to know."""


def pass4_user(req: dict, pass1: dict, pass2: dict, pass3: dict) -> str:
    high_sev_svcs = [
        i["id"]
        for i in (
            pass2.get("directly_affected_impacts", [])
            + pass2.get("first_order_impacts", [])
            + pass3.get("second_order_impacts", [])
        )
        if i.get("risk_severity") in ("critical", "high")
    ]
    return f"""Map technical impacts to organizational impacts.

DECISION: {req['decision']['title']}
TYPE: {req['decision']['decision_type']} | TIMELINE: {req['decision']['timeline']} | REVERSIBILITY: {req['decision']['reversibility']}

TEAMS (with ownership):
{_j(req['teams'])}

HIGH-SEVERITY TECHNICAL IMPACTS ON SERVICES: {_j(list(set(high_sev_svcs)))}
PASS 1 KEY CONCERNS: {_j(pass1.get('key_concerns', []))}
PASS 3 PROPAGATION PATTERNS: {_j(pass3.get('propagation_patterns', []))}

ADDITIONAL CONTEXT: {req.get('additional_context') or 'None provided'}

For each team: analyze workload impact, roadmap disruption, SLA risk, and stakeholder commitments.
Also identify process impacts and any external stakeholder impacts.

Return exactly this JSON structure:
{{
  "team_impacts": [
    {{
      "id": "team-id-org-impact",
      "name": "Team Name — Org Impact",
      "type": "team",
      "impact_level": "direct|second-order|third-order",
      "risk_severity": "critical|high|medium|low|none",
      "impact_description": "Specific org impact: workload increase, context switching, coordination overhead",
      "workload_impact": "concrete workload change description",
      "roadmap_disruption": "which roadmap items are at risk and how",
      "sla_risk": "any SLA or commitment at risk",
      "stakeholder_commitments": "external commitments affected",
      "recommended_actions": ["specific org action"],
      "is_inferred": false,
      "owns_services": ["service ids this team owns that are affected"]
    }}
  ],
  "process_impacts": [
    {{
      "id": "process-id",
      "name": "Process Name",
      "type": "process",
      "impact_level": "direct|second-order",
      "risk_severity": "critical|high|medium|low",
      "impact_description": "What process is disrupted and how",
      "recommended_actions": ["action"],
      "is_inferred": true
    }}
  ],
  "external_impacts": [
    {{
      "id": "external-id",
      "name": "External Stakeholder/Partner/Customer",
      "type": "external",
      "impact_level": "second-order|third-order",
      "risk_severity": "critical|high|medium|low|none",
      "impact_description": "External-facing impact",
      "recommended_actions": ["action"],
      "is_inferred": true
    }}
  ],
  "communication_overhead": "description of coordination and communication overhead this decision creates",
  "change_management_requirements": ["specific change management action needed"],
  "pass4_summary": "2-3 sentence summary of organizational blast radius — this is the part most tools miss"
}}"""


# ─────────────────────────────────────────────
# PASS 5 — Risk Scoring and Synthesis
# ─────────────────────────────────────────────

PASS5_SYSTEM = SYSTEM_BASE + """

Pass 5 — Risk Scoring and Synthesis
Synthesize all previous pass findings into a complete risk assessment.
Score each dimension 0.0–1.0. Compute overall risk score. Write an executive summary a VP Engineering can act on.
Generate specific immediate actions and open questions. Be direct and concrete — no generic advice."""


def pass5_user(req: dict, pass1: dict, pass2: dict, pass3: dict, pass4: dict, all_nodes: list) -> str:
    direct_critical = [
        i["id"] for i in (pass2.get("directly_affected_impacts", []) + pass2.get("first_order_impacts", []))
        if i.get("risk_severity") == "critical"
    ]
    return f"""Synthesize all analysis passes into a complete risk assessment.

DECISION: {req['decision']['title']}
TYPE: {req['decision']['decision_type']} | TIMELINE: {req['decision']['timeline']} | REVERSIBILITY: {req['decision']['reversibility']}

PASS 1 — Classification:
  Class: {pass1.get('decision_class')}
  Primary risk: {pass1.get('primary_risk_category')}
  Blast radius prediction: {pass1.get('blast_radius_prediction')}
  Key concerns: {_j(pass1.get('key_concerns', []))}

PASS 2 — First-Order:
  Summary: {pass2.get('pass2_summary')}
  Critical services: {_j(direct_critical)}

PASS 3 — Second-Order:
  Summary: {pass3.get('pass3_summary')}
  Patterns: {_j([p.get('pattern', '') for p in pass3.get('propagation_patterns', [])])}

PASS 4 — Org Impact:
  Summary: {pass4.get('pass4_summary')}
  Overhead: {pass4.get('communication_overhead')}
  Teams impacted: {_j([t['id'] for t in pass4.get('team_impacts', [])])}
  External: {_j([e['name'] for e in pass4.get('external_impacts', [])])}

TOTAL NODES: {len(all_nodes)}
ADDITIONAL CONTEXT: {req.get('additional_context') or 'None'}

Score dimensions 0.0–1.0: 0.0–0.3=LOW, 0.31–0.5=MODERATE, 0.51–0.75=HIGH, 0.76–1.0=CRITICAL

Return exactly this JSON structure:
{{
  "overall_risk_score": 0.0,
  "overall_verdict": "LOW|MODERATE|HIGH|CRITICAL",
  "executive_summary": "3-4 sentences for a VP Engineering. State the decision, the key risks discovered, and the recommended posture. Be direct. Mention the most surprising or non-obvious finding.",
  "risk_dimensions": [
    {{
      "dimension": "technical",
      "score": 0.0,
      "summary": "1-2 sentence technical risk summary",
      "top_risks": ["specific risk 1", "specific risk 2", "specific risk 3"],
      "mitigations": ["specific mitigation 1", "specific mitigation 2"]
    }},
    {{
      "dimension": "delivery",
      "score": 0.0,
      "summary": "1-2 sentence delivery risk summary",
      "top_risks": ["risk"],
      "mitigations": ["mitigation"]
    }},
    {{
      "dimension": "people",
      "score": 0.0,
      "summary": "1-2 sentence people/org risk summary",
      "top_risks": ["risk"],
      "mitigations": ["mitigation"]
    }},
    {{
      "dimension": "compliance",
      "score": 0.0,
      "summary": "1-2 sentence compliance risk summary",
      "top_risks": ["risk"],
      "mitigations": ["mitigation"]
    }},
    {{
      "dimension": "financial",
      "score": 0.0,
      "summary": "1-2 sentence financial risk summary",
      "top_risks": ["risk"],
      "mitigations": ["mitigation"]
    }}
  ],
  "immediate_actions": [
    "Specific concrete action — not generic advice",
    "Second immediate action",
    "Third immediate action"
  ],
  "questions_to_answer": [
    "Specific question the team must answer before proceeding",
    "Second question",
    "Third question",
    "Fourth question"
  ],
  "confidence_note": "This analysis is grounded in the context you provided. Nodes marked ◈ are inferred — not explicitly defined in your intake. In production, connect Backstage, PagerDuty, and your org chart to replace manual intake with live data."
}}"""


def _j(obj) -> str:
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return str(obj)
