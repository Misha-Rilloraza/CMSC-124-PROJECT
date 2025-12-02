from helper import error, match, end_of_line, peek_token
from expressions import *

control_flow_stack = []
current_structure = None

def get_control_stack():
    return control_flow_stack

def reset_control_flow():
    global control_flow_stack, current_structure
    control_flow_stack = []
    current_structure = None

# starting with the whole block
# conditional structures works as multi-line

def parse_if_structure(state):
    # Parse parse ikaw ay nakakasilaw
    # be mindful of the first expression
    start_pos = state["position"]
    
    condition = parse_expression(state)
    if not condition:
        state["position"] = start_pos
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after expression")
        state["position"] = start_pos
        return None
    
    # store the condition
    global control_flow_stack, current_structure
    control_flow_stack.append({
        "type": "if",
        "condition": condition,
        "state": "condition_parsed",
        "has_then": False,
        "has_else": False,
        "has_o_rly": False,
        "elseif_count": 0
    })
    current_structure = "if"
    
    return {"node": "if_condition", "condition": condition}

def parse_o_rly(state):
    # Parse O RLY?
    # if statement start usually
    if not control_flow_stack or control_flow_stack[-1]["type"] != "if":
        error(state, "O RLY? without preceding IF condition")
        return None
    
    token = match(state, "If Keyword", "O RLY?")
    if not token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after O RLY?")
        return None
    
    frame = control_flow_stack[-1]
    frame["has_o_rly"] = True
    frame["state"] = "o_rly_parsed"
    
    return {"node": "o_rly", "token": token}

def parse_ya_rly(state):
    # Parse YA RLY
    # the then branch thingy
    # be mindful of the order ng conditions
    if not control_flow_stack or control_flow_stack[-1]["type"] != "if":
        error(state, "YA RLY without preceding IF structure")
        return None
    
    frame = control_flow_stack[-1]
    if not frame.get("has_o_rly"):
        error(state, "YA RLY must follow O RLY?")
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

def parse_mebbe(state):
    # Parse MEBBE
    # the else-if
    if not control_flow_stack or control_flow_stack[-1]["type"] != "if":
        error(state, "MEBBE without active IF")
        return None
    
    frame = control_flow_stack[-1]
    
    # before MEBBE, dapat may YA RLY
    # (a must)
    if not frame.get("has_then") and frame["elseif_count"] == 0:
        error(state, "MEBBE requires a YA RLY branch first")
        return None
    
    token = match(state, "ElseIf Keyword", "MEBBE")
    if not token:
        return None
    
    # Parse the MEBBE condition
    condition = parse_expression(state)
    if not condition:
        error(state, "Expected condition after MEBBE")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after MEBBE")
        return None
    
    frame["state"] = "elseif_parsed"
    frame["elseif_count"] += 1
    
    return {"node": "else_if_statement", "condition": condition, "token": token}

def parse_no_wai(state):
    # Parse NO WAI
    # since else siya, siya nasa hulihan
    if not control_flow_stack or control_flow_stack[-1]["type"] != "if":
        error(state, "NO WAI without active IF")
        return None
    
    frame = control_flow_stack[-1]
    
    # can't use NO WAI without an active if structure
    if not frame.get("has_then") and frame["elseif_count"] == 0:
        error(state, "NO WAI requires a YA RLY or MEBBE branch first")
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
    # Parse WTF?????
    # switch toh ah
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
        "expression": expression,
        "state": "switch_parsed",
        "has_cases": False,
        "has_default": False,
        "case_count": 0
    })
    current_structure = "switch"
    
    return {"node": "switch_start", "expression": expression, "token": token}

def parse_omg(state):
    # Parse OMG
    # switch cases
    if not control_flow_stack or control_flow_stack[-1]["type"] != "switch":
        error(state, "OMG without preceding WTF?")
        return None
    
    token = match(state, "Comparison Statement", "OMG")
    if not token:
        return None
    
    # expect value (ltieral)
    case_value = parse_simple_expression(state)
    if not case_value:
        error(state, "Expected literal value after OMG")
        return None
    
    if case_value.get("node") not in [
        "string_literal", "integer_literal", "float_literal",
        "boolean_literal", "type_literal"
    ]:
        error(state, "Case value must be a literal")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after case value")
        return None
    
    frame = control_flow_stack[-1]
    frame["has_cases"] = True
    frame["state"] = "case_parsed"
    frame["case_count"] += 1
    
    return {"node": "switch_case", "case_value": case_value, "token": token}

def parse_omgwtf(state):
    # Parse OMGWTF
    # default case | nasa hulihan
    if not control_flow_stack or control_flow_stack[-1]["type"] != "switch":
        error(state, "OMGWTF without preceding WTF?")
        return None
    
    token = match(state, "Default Comparison Statement", "OMGWTF")
    if not token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after OMGWTF")
        return None
    
    frame = control_flow_stack[-1]
    frame["has_default"] = True
    frame["state"] = "default_parsed"
    
    return {"node": "default_case", "token": token}

# isahang OIC na lang
# very tricky
def parse_oic(state):
    if not control_flow_stack:
        error(state, "OIC without preceding control structure")
        return None
    
    token = match(state, "End Block", "OIC")
    if not token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after OIC")
        return None
    
    frame = control_flow_stack[-1]
    
    if frame["type"] == "if":
        return _parse_if_end(state, frame, token)
    elif frame["type"] == "switch":
        return _parse_switch_end(state, frame, token)
    
    error(state, "OIC encountered in unknown structure")
    return None

def _parse_if_end(state, frame, token):
    if not frame.get("has_then"):
        error(state, "IF must have at least a YA RLY branch before OIC")
        return None
    
    if not frame.get("has_o_rly"):
        error(state, "Missing O RLY? in IF structure")
        return None
    
    # POP the if from stack
    control_flow_stack.pop()
    
    # update current structure
    global current_structure
    if not control_flow_stack:
        current_structure = None
    else:
        current_structure = control_flow_stack[-1]["type"]
    
    return {"node": "if_statement_end", "token": token}

def _parse_switch_end(state, frame, token):
    # ganon lang din, for switch naman
    if not frame.get("has_cases"):
        error(state, "Switch must have at least one OMG case before OIC")
        return None
    
    # Pop the SWITCH frame from stack
    control_flow_stack.pop()
    
    # Update current structure
    global current_structure
    if not control_flow_stack:
        current_structure = None
    else:
        current_structure = control_flow_stack[-1]["type"]
    
    return {"node": "switch_end", "token": token}

def in_control_flow():
    # we need to check if nasa loob pa rin ng structure
    return len(control_flow_stack) > 0

def get_current_structure():
    return current_structure

def get_current_frame():
    if control_flow_stack:
        return control_flow_stack[-1]
    return None

def validate_control_flow_completion(state):
    # make sure na closed ung mga blocks
    errors = []
    
    for i, frame in enumerate(control_flow_stack):
        if frame["type"] == "if":
            errors.append(f"Unclosed IF structure at nesting level {i}")
        elif frame["type"] == "switch":
            errors.append(f"Unclosed SWITCH structure at nesting level {i}")
    
    # Add errors to state
    for error_msg in errors:
        error(state, error_msg)
    
    return len(errors) == 0

# def parse_control_flow_block(state, parse_statement_func):
#     # parse the statements na nasa loob ng mga conditional blocks
#     # until OIC
#     # param: state and function for parsing
#     # return: list of parsed statements
#     statements = []
    
#     # Parse until we hit OIC or end of input
#     while state["position"] < len(state["tokens"]):
#         # Check if next token is OIC (end of block)
#         if peek_token(state, expected_value="OIC"):
#             break
        
#         # Parse a statement
#         statement = parse_statement_func(state)
#         if statement:
#             statements.append(statement)
#         else:
#             # Skip token if we can't parse it
#             if state["position"] < len(state["tokens"]):
#                 state["position"] += 1
    
#     return statements

# def parse_if_block_content(state, parse_statement_func):
#     return parse_control_flow_block(state, parse_statement_func)

# def parse_switch_block_content(state, parse_statement_func):
#     return parse_control_flow_block(state, parse_statement_func)

def is_control_flow_keyword(token_value):
    """Check if a token is a control flow keyword"""
    control_flow_keywords = [
        "O RLY?", "YA RLY", "MEBBE", "NO WAI", "OIC",
        "WTF?", "OMG", "OMGWTF",
        "BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF"  # comparison ops that start IF
    ]
    return token_value in control_flow_keywords

def get_control_flow_parser(token_value):
    """
    Get the appropriate control flow parser for a token.
    Returns the parser function or None.
    """
    parser_map = {
        "O RLY?": parse_o_rly,
        "YA RLY": parse_ya_rly,
        "MEBBE": parse_mebbe,
        "NO WAI": parse_no_wai,
        "OIC": parse_oic,
        "WTF?": parse_switch_structure,
        "OMG": parse_omg,
        "OMGWTF": parse_omgwtf,
    }
    
    # comparison operators, they start an IF structure
    if token_value in ["BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF"]:
        return parse_if_structure
    
    return parser_map.get(token_value)