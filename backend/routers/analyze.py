"""
SSE streaming analysis router.
Runs the 5-pass analysis engine with progress events streamed between each pass.
"""
import json
import asyncio
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.intake import BlastRadiusRequest
from services.errors import AnalysisError
from services.graph_builder import (
    build_graph,
    get_first_order,
    get_second_order,
    get_graph_data,
    get_services_by_ids,
)
from services.decision_classifier import classify_decision
from services.impact_analyzer import analyze_first_order, analyze_second_order
from services.org_mapper import map_org_impact
from services.risk_scorer import score_and_synthesize

router = APIRouter(prefix="/analyze")
logger = logging.getLogger(__name__)


def sse(data: dict) -> str:
    return f"data: {json.dumps(data, default=str)}\n\n"


async def _run_in_executor(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *args)


async def run_analysis_stream(request: BlastRadiusRequest) -> AsyncGenerator[str, None]:
    req_dict = request.model_dump()

    try:
        # Build graph (fast, synchronous)
        G = build_graph(request.services, request.dependencies)
        graph_data = get_graph_data(G)
        affected_ids = request.decision.affected_services
        first_order_ids = get_first_order(G, affected_ids)
        second_order_ids = get_second_order(G, affected_ids, first_order_ids)

        # ── Pass 1 ──────────────────────────────────
        yield sse({"type": "progress", "pass": 1, "total": 5, "message": "Classifying decision type..."})
        await asyncio.sleep(0)

        pass1 = await _run_in_executor(classify_decision, req_dict)
        yield sse({
            "type": "pass_complete", "pass": 1, "name": "Decision Classification",
            "summary": pass1.get("playbook_notes", "")[:200],
        })

        # ── Pass 2 ──────────────────────────────────
        yield sse({"type": "progress", "pass": 2, "total": 5, "message": "Mapping first-order technical impacts..."})
        await asyncio.sleep(0)

        first_order_svcs = get_services_by_ids(request.services, first_order_ids)
        pass2 = await _run_in_executor(analyze_first_order, req_dict, pass1, first_order_svcs, graph_data)

        direct_n = len(pass2.get("directly_affected_impacts", []))
        first_n = len(pass2.get("first_order_impacts", []))
        yield sse({
            "type": "pass_complete", "pass": 2, "name": "First-Order Impact",
            "summary": pass2.get("pass2_summary", f"Found {direct_n} direct + {first_n} first-order impacts"),
        })

        # ── Pass 3 ──────────────────────────────────
        yield sse({"type": "progress", "pass": 3, "total": 5, "message": "Propagating second-order effects..."})
        await asyncio.sleep(0)

        second_order_svcs = get_services_by_ids(request.services, second_order_ids)
        pass3 = await _run_in_executor(analyze_second_order, req_dict, pass1, pass2, second_order_svcs)

        second_n = len(pass3.get("second_order_impacts", []))
        yield sse({
            "type": "pass_complete", "pass": 3, "name": "Second-Order Propagation",
            "summary": pass3.get("pass3_summary", f"Found {second_n} second-order impacts"),
        })

        # ── Pass 4 ──────────────────────────────────
        yield sse({"type": "progress", "pass": 4, "total": 5, "message": "Analyzing organizational impact..."})
        await asyncio.sleep(0)

        pass4 = await _run_in_executor(map_org_impact, req_dict, pass1, pass2, pass3)

        team_n = len(pass4.get("team_impacts", []))
        yield sse({
            "type": "pass_complete", "pass": 4, "name": "Organizational Impact",
            "summary": pass4.get("pass4_summary", f"Mapped {team_n} team impacts"),
        })

        # ── Pass 5 ──────────────────────────────────
        yield sse({"type": "progress", "pass": 5, "total": 5, "message": "Scoring risk dimensions and synthesizing..."})
        await asyncio.sleep(0)

        all_nodes = (
            pass2.get("directly_affected_impacts", [])
            + pass2.get("first_order_impacts", [])
            + pass3.get("second_order_impacts", [])
            + pass4.get("team_impacts", [])
        )

        result = await _run_in_executor(
            score_and_synthesize, req_dict, pass1, pass2, pass3, pass4, all_nodes, []
        )

        yield sse({
            "type": "pass_complete", "pass": 5, "name": "Risk Scoring & Synthesis",
            "summary": f"Overall verdict: {result.overall_verdict} ({result.overall_risk_score:.0%} risk score)",
        })

        yield sse({"type": "result", "data": result.model_dump()})
        yield sse({"type": "complete", "message": "Analysis complete"})

    except AnalysisError as exc:
        logger.warning("Streaming analysis failed: %s", exc)
        yield sse({"type": "error", "message": str(exc)})
    except Exception:
        logger.exception("Streaming analysis failed unexpectedly")
        yield sse({"type": "error", "message": "Analysis failed due to an internal server error."})


@router.post("/stream")
async def stream_analysis(request: BlastRadiusRequest):
    """Stream 5-pass analysis as Server-Sent Events."""
    return StreamingResponse(
        run_analysis_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("")
async def analyze_sync(request: BlastRadiusRequest):
    """Synchronous analysis — runs all 5 passes and returns complete BlastRadiusResult."""
    try:
        req_dict = request.model_dump()
        G = build_graph(request.services, request.dependencies)
        graph_data = get_graph_data(G)
        affected_ids = request.decision.affected_services
        first_order_ids = get_first_order(G, affected_ids)
        second_order_ids = get_second_order(G, affected_ids, first_order_ids)

        pass1 = classify_decision(req_dict)
        first_order_svcs = get_services_by_ids(request.services, first_order_ids)
        pass2 = analyze_first_order(req_dict, pass1, first_order_svcs, graph_data)
        second_order_svcs = get_services_by_ids(request.services, second_order_ids)
        pass3 = analyze_second_order(req_dict, pass1, pass2, second_order_svcs)
        pass4 = map_org_impact(req_dict, pass1, pass2, pass3)

        all_nodes = (
            pass2.get("directly_affected_impacts", [])
            + pass2.get("first_order_impacts", [])
            + pass3.get("second_order_impacts", [])
            + pass4.get("team_impacts", [])
        )

        return score_and_synthesize(req_dict, pass1, pass2, pass3, pass4, all_nodes, [])
    except AnalysisError as exc:
        logger.warning("Synchronous analysis failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Synchronous analysis failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed due to an internal server error.",
        ) from exc
