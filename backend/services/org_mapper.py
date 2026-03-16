"""Pass 4 — Organizational Impact Mapping"""

import services.llm_client as llm_client
from utils.llm_json import parse_llm_json
from utils.prompts import PASS4_SYSTEM, pass4_user


def map_org_impact(
    request_dict: dict,
    pass1_output: dict,
    pass2_output: dict,
    pass3_output: dict,
) -> dict:
    """Run Pass 4: map technical impacts to organizational impacts."""
    text = llm_client.complete(
        PASS4_SYSTEM,
        pass4_user(request_dict, pass1_output, pass2_output, pass3_output),
        max_tokens=4096,
    )
    return parse_llm_json(text, "organizational impact analysis")
