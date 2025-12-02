from helper import error, match, end_of_line
from expressions import *

control_flow_stack = []
current_structure = None

# def reset_control_flow(state):
#     global control_flow_stack, current_structure
#     control_flow_stack = []
#     current_structure = None

# def validate_control_flow(state):
#     for structure in control_flow_stack:
#         if structure["type"] == "if":
#             error(state, "Unclosed IF structure detected")
#         elif structure["type"] == "switch":
#             error(state, "Unclosed SWITCH structure detected")

def get_control_stack():
    return control_flow_stack

# ========================
# IF STRUCTURE
# ========================

def parse_if_structure(state):
    # this is the start of the whole chunk for the condition
    # handle the expression first before pushing to stack  
    condition = parse_expression(state)
    if not condition:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after expression")
        return None

    global control_flow_stack, current_structure
    control_flow_stack.append({
        "type": "if",
        "state": "condition_parsed",
        "has_then": False,
        "has_else": False,
        "has_o_rly": False
    })
    current_structure = "if"

    return {"node": "if_condition", "condition": condition}


def parse_if_statement_start(state):
    if not control_flow_stack or control_flow_stack[-1]["type"] != "if":
        error(state, "O RLY? without preceding IF condition")
        return None

    token = match(state, "If Keyword", "O RLY?")
    if not token:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after O RLY?")
        return None

    control_flow_stack[-1]["has_o_rly"] = True
    control_flow_stack[-1]["state"] = "if_started"
    return {"node": "if_statement_start", "token": token}


def parse_then_statement(state):
    frame = control_flow_stack[-1] if control_flow_stack else None
    if not frame or frame["type"] != "if" or frame["state"] not in ["if_started"]:
        error(state, "YA RLY without preceding O RLY?")
        return None

    token = match(state, "Then Keyword", "YA RLY")
    if not token:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after YA RLY")
        return None

    frame["state"] = "then_parsed"
    frame["has_then"] = True

    return {"node": "then_statement", "token": token}


def parse_elseif_statement(state):
    frame = control_flow_stack[-1] if control_flow_stack else None

    if not frame or frame["type"] != "if":
        error(state, "MEBBE without active IF")
        return None

    if not frame["has_then"]:
        error(state, "MEBBE requires a YA RLY branch first")
        return None

    token = match(state, "ElseIf Keyword", "MEBBE")
    if not token:
        return None

    condition = parse_expression(state)
    if not condition:
        error(state, "Expected condition after MEBBE")
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after MEBBE")
        return None

    frame["state"] = "elseif_parsed"
    return {"node": "else_if_statement", "condition": condition, "token": token}


def parse_else_statement(state):
    frame = control_flow_stack[-1] if control_flow_stack else None

    if not frame or frame["type"] != "if" or frame["state"] not in ["then_parsed", "elseif_parsed"]:
        error(state, "NO WAI without preceding YA RLY or MEBBE")
        return None

    token = match(state, "Else Keyword", "NO WAI")
    if not token:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after NO WAI")
        return None

    frame["state"] = "else_parsed"
    frame["has_else"] = True

    return {"node": "else_statement", "token": token}


# ========================
# SWITCH STRUCTURE
# ========================

def parse_switch_structure(state):
    token = match(state, "Switch", "WTF?")
    if not token:
        return None

    expression = parse_expression(state)
    if not expression:
        error(state, "Expected expression after WTF?")
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after WTF?")
        return None

    global control_flow_stack, current_structure
    control_flow_stack.append({
        "type": "switch",
        "state": "switch_parsed",
        "has_cases": False,
        "has_default": False
    })
    current_structure = "switch"

    return {"node": "switch_start", "expression": expression, "token": token}


def parse_switch_cases(state):
    frame = control_flow_stack[-1] if control_flow_stack else None
    if not frame or frame["type"] != "switch":
        error(state, "OMG without preceding WTF?")
        return None

    token = match(state, "Case", "OMG")
    if not token:
        return None

    case_value = parse_simple_expression(state)
    if not case_value:
        error(state, "Expected literal value after OMG")
        return None

    if case_value["node"] not in [
        "string_literal", "integer_literal", "float_literal",
        "boolean_literal", "type_literal"
    ]:
        error(state, "Case value must be a literal")
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after case value")
        return None

    frame["has_cases"] = True
    return {"node": "switch_case", "case_value": case_value, "token": token}


def parse_default_case(state):
    frame = control_flow_stack[-1] if control_flow_stack else None
    if not frame or frame["type"] != "switch":
        error(state, "OMGWTF without preceding WTF?")
        return None

    token = match(state, "Default Case", "OMGWTF")
    if not token:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after OMGWTF")
        return None

    frame["has_default"] = True
    return {"node": "default_case", "token": token}


# ========================
# UNIFIED OIC HANDLING
# ========================

def parse_oic(state):
    stack = get_control_stack()
    if not stack:
        error(state, "OIC without preceding control structure")
        return None

    token = match(state, "End Block", "OIC")
    if not token:
        return None

    if not end_of_line(state):
        error(state, "Unexpected tokens after OIC")
        return None

    frame = stack[-1]

    if frame["type"] == "if":
        return _parse_if_end(frame, token)
    elif frame["type"] == "switch":
        return _parse_switch_end(frame, token)

    error(state, "OIC encountered in unknown structure")
    return None


def _parse_if_end(frame, token):
    if not frame.get("has_then"):
        error("IF must have at least a YA RLY branch before OIC")
        return None

    control_flow_stack.pop()

    return {"node": "if_statement_end", "token": token}


def _parse_switch_end(frame, token):
    if not frame.get("has_cases"):
        error("Switch must have at least one OMG case before OIC")
        return None

    control_flow_stack.pop()

    return {"node": "switch_end", "token": token}
