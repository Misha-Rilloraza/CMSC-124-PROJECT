from helper import error, match, end_of_line
from expressions import *

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
    cond_token = match(state, "If-Then-Else End", "OIC")
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
    cond_token = match(state, "Switch", "WTF?") or match(state, "Switch", "WTF")
    if not cond_token:
        return None
    
    expression = parse_expression(state)
    if not expression:
        error(state, "Expected expression after WTF?")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after switch")
        return None
    
    return {
        'node': 'switch_start',
        'expression': expression,
        'token': cond_token
    }

def parse_switch_cases(state):
    # Parse OMG
    cond_token = match(state, "Comparison Statement", "OMG")
    if not cond_token:
        return None
    
    case_value = parse_simple_expression(state)
    if not case_value:
        error(state, "Expected literal value after OMG")
        return None
    
    if case_value['node'] not in ['string_literal', 'integer_literal', 'float_literal', 'boolean_literal', 'type_literal']:
        error(state, "Case value must be a literal")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after case value")
        return None
    
    return {
        'node': 'switch_case',
        'case_value': case_value,
        'token': cond_token
    }

def parse_default_case(state):
    # Parse OMGWTF
    cond_token = match(state, "Default Comparison Statement", "OMGWTF")
    if not cond_token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after OMGWTF")
        return None
    
    return {
        'node': 'default_case',
        'token': cond_token
    }

def parse_switch_end(state):
    # Parse OIC
    cond_token = match(state, "If-Then-Else End", "OIC")
    if not cond_token:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after OIC")
        return None
    
    return {
        'node': 'switch_end',
        'token': cond_token
    }

# == LOOPS

def parse_loop_start(state):
    # Parse IM IN YR <label> (UPPIN YR|NERFIN YR) <var> (WILE|TIL) <condition>
    token = match(state, "Start Loop Label", "IM IN YR")
    if not token:
        return None

    label = None
    next_tok = state['current_token']
    if next_tok and next_tok['token_name'] == 'Variable Identifier':
        label = next_tok['pattern']
        advance(state)

    # increment/decrement
    incdec = None
    varname = None
    if match(state, "Increment", "UPPIN YR"):
        incdec = 'UPPIN'
    elif match(state, "Decrement", "NERFIN YR"):
        incdec = 'NERFIN'
    if incdec:
        ident = state['current_token']
        if ident and ident['token_name'] == 'Variable Identifier':
            varname = ident['pattern']
            advance(state)

    # loop condition
    mode = None
    if match(state, "While Loop", "WILE"):
        mode = 'WILE'
    elif match(state, "Until Loop", "TIL"):
        mode = 'TIL'
    condition = parse_expression(state) if mode else None

    if not end_of_line(state):
        error(state, "Unexpected tokens after loop header")
        return None

    return {
        'node': 'loop_start',
        'label': label,
        'incdec': incdec,
        'varname': varname,
        'mode': mode,
        'condition': condition,
        'token': token
    }

def parse_loop_end(state):
    # Parse IM OUTTA YR <label>
    token = match(state, "End Loop Label", "IM OUTTA YR")
    if not token:
        return None
    label = None
    next_tok = state['current_token']
    if next_tok and next_tok['token_name'] == 'Variable Identifier':
        label = next_tok['pattern']
        advance(state)
    if not end_of_line(state):
        error(state, "Unexpected tokens after loop end")
        return None
    return {
        'node': 'loop_end',
        'label': label,
        'token': token
    }