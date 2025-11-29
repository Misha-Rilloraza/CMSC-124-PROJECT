from helper import error, match, end_of_line
from expressions import parse_expression

# def parse_conditional_expression(state):
#     condition = parse_expression(state)
#     if not condition:
#         error(state, "Expected conditional expression")
#         return None
    
#     if not end_of_line(state):
#         error(state, "Unexpected tokens after conditional expression")
#         return None
    
#     return {
#         'node': 'conditional_expression',
#         'condition': condition
#     }

# == NORMAL CONDITIONALS

def parse_if_statement_start(state):
    # Parse O RLY?
    # start of if-else block
    cond_token = match(state, "If Keyword", "O RLY?")
    if not cond_token:
        return None
    elif not end_of_line(state):
        error(state, "Unexpected tokens after O RLY?")
        return None
    
    return {
        'node': 'if_statement_start',
        'token': cond_token
    }

def parse_then_statement(state):
    # Parse YA RLY
    cond_token = match(state, "Then Keyword", "YA RLY")
    if not cond_token:
        return None
    elif not end_of_line(state):
        error(state, "Unexpected tokens after YA RLY")
        return None
    
    return {
        'node': 'then_statement',
        'token': cond_token
    }

def parse_elseif_statement(state):
    # Parse MEBBE
    cond_token = match(state, "ElseIf Keyword", "MEBBE")
    if not cond_token:
        return None
    
    condition = parse_expression(state)
    if not condition:
        error(state, "Expected condition after MEBBE")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after MEBBE")
        return None
    
    return {
        'node': 'else_if_statement',
        'condition': condition,
        'token': cond_token
    }

def parse_else_statement(state):
    # Parse NO WAI
    cond_token = match(state, "Else Keyword", "NO WAI")
    if not cond_token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after NO WAI")
        return None
    
    return {
        'node': 'else_statement',
        'token': cond_token
    }

def parse_if_end(state):
    # Parse OIC
    cond_token = match(state, "If-Then-Else-End", "OIC")
    if not cond_token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after OIC")
        return None
    
    return {
        'node': 'if_statement_end',
        'token': cond_token
    }

# == SWITCH CASE

def parse_switch_start(state):
    # Parse WTF
    cond_token = match(state, "Switch", "WTF?")
    if not cond_token:
        return None
    
    if not end_of_line:
        error(state, "Expected expression for WTF?")
        return None
    
    return {
        'node': 'switch_start',
        'token': cond_token
    }