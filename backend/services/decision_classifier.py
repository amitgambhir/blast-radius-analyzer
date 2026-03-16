"""Pass 1 — Decision Classification"""

import services.llm_client as llm_client
from utils.llm_json import parse_llm_json
from utils.prompts import PASS1_SYSTEM, pass1_user


def classify_decision(request_dict: dict) -> dict:
    """Run Pass 1: classify the decision and identify primary risk category."""
    text = llm_client.complete(PASS1_SYSTEM, pass1_user(request_dict), max_tokens=2048)
    return parse_llm_json(text, "decision classification")
