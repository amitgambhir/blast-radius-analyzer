"""Passes 2 and 3 — First-Order and Second-Order Impact Analysis"""

import services.llm_client as llm_client
from utils.llm_json import parse_llm_json
from utils.prompts import PASS2_SYSTEM, pass2_user, PASS3_SYSTEM, pass3_user


def analyze_first_order(
    request_dict: dict,
    pass1_output: dict,
    first_order_services: list,
    graph_data: dict,
) -> dict:
    """Run Pass 2: analyze first-order technical impacts."""
    text = llm_client.complete(
        PASS2_SYSTEM,
        pass2_user(request_dict, pass1_output, first_order_services, graph_data),
        max_tokens=4096,
    )
    return parse_llm_json(text, "first-order impact analysis")


def analyze_second_order(
    request_dict: dict,
    pass1_output: dict,
    pass2_output: dict,
    second_order_services: list,
) -> dict:
    """Run Pass 3: analyze second-order propagation."""
    text = llm_client.complete(
        PASS3_SYSTEM,
        pass3_user(request_dict, pass1_output, pass2_output, second_order_services),
        max_tokens=4096,
    )
    return parse_llm_json(text, "second-order impact analysis")
