from helper import extract_value, error, match, advance

def parse_expression(state):
    # be mindful of operator precedence
    # SMOOSH (string concatenation) has low precedence
    return parse_smoosh(state)

def parse_smoosh(state):
    # Parse SMOOSH (string concatenation)
    # SMOOSH has lower precedence than logical operations
    if state['current_token'] and state['current_token']['pattern'] == "SMOOSH":
        operator_token = match(state, "String Concatenation", "SMOOSH")
        operands = []
        
        # Parse first operand
        operand1 = parse_logical_or(state)
        if not operand1:
            error(state, "Expected expression after SMOOSH")
            return None
        operands.append(operand1)
        
        # Parse AN operand pairs
        while state['current_token'] and state['current_token']['pattern'] == 'AN':
            advance(state)  # consume AN
            operand = parse_logical_or(state)
            if not operand:
                error(state, "Expected expression after AN in SMOOSH")
                return None
            operands.append(operand)
        
        return {
            'node': 'smoosh_expression',
            'operands': operands
        }
    else:
        # No SMOOSH, just parse logical operations
        return parse_logical_or(state)

def parse_logical_or(state):
    left = parse_logical_xor(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] in ["ANY OF", "EITHER OF"]:
        operator_token = match(state, "Logical Operator", state['current_token']['pattern'])
        right = parse_logical_xor(state)
        if not right:
            return None
        left = {
            'node': 'logical_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_logical_xor(state):
    left = parse_logical_and(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] == "WON OF":
        operator_token = match(state, "Logical Operator", "WON OF")
        right = parse_logical_and(state)
        if not right:
            return None
        left = {
            'node': 'logical_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_logical_and(state):
    left = parse_comparison(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] in ["BOTH OF", "ALL OF"]:
        operator_token = match(state, "Logical Operator", state['current_token']['pattern'])
        right = parse_comparison(state)
        if not right:
            return None
        left = {
            'node': 'logical_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_comparison(state):
    # can be at the beginning
    if state['current_token'] and state['current_token']['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
        return parse_comparison_expression(state)
    
    # for expressions that have this in the middle
    left = parse_arithmetic(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
        operator_token = state['current_token']['pattern']
        advance(state)
        right = parse_arithmetic(state)
        if not right:
            return None
        left = {
            'node': 'comparison_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_arithmetic(state):
    left = parse_term(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] in ["SUM OF", "DIFF OF"]:
        operator_token = state['current_token']['pattern']
        advance(state)
        right = parse_term(state)
        if not right:
            return None
        left = {
            'node': 'arithmetic_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_term(state):
    left = parse_factor(state)
    if not left:
        return None
    while state['current_token'] and state['current_token']['pattern'] in ["PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
        operator_token = state['current_token']['pattern']
        advance(state)
        right = parse_factor(state)
        if not right:
            return None
        left = {
            'node': 'arithmetic_operation',
            'operator': operator_token['pattern'],
            'left': left,
            'right': right
        }
    return left
    
def parse_factor(state):
    if not state['current_token']:
        error(state, "Unexpected end of line in expression")
        return None
    
    if state['current_token']['pattern'] == "MAEK":
        return parse_maek_expression(state)
    if state['current_token']['pattern'] == "NOT":
        return parse_unary_expression(state)
    if state['current_token']['pattern'] == "SMOOSH":
        return parse_smoosh_expression(state)
    if state['current_token']['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
        return parse_comparison_expression(state)
    elif state['current_token']['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
        return parse_arithmetic_expression(state)
    elif state['current_token']['token_name'] in ["Variable Identifier", "String Literal", "Boolean Literal", "TYPE Literal", "Float Literal", "Integer Literal"]:
        return parse_simple_expression(state)
    else:
        error(state, f"Unexpected token in expression: {state['current_token']['pattern']}")
        return None
    
def parse_unary_expression(state):
    # Parse NOT
    operator_token = match(state, "Unary Operator", "NOT")
    if not operator_token:
        return None
    
    operand = parse_factor(state)
    if not operand:
        error(state, "Expected operand after NOT")
        return None
    
    results = {
        'node': 'unary_expression',
        'operator': 'NOT',
        'operand': operand,
        'token': operator_token
    }
    return results

def parse_smoosh_expression(state):
    # Parse SMOOSH concatenation: SMOOSH <expr> AN <expr> [AN <expr> ...]
    operator_token = match(state, "String Concatenation")
    if not operator_token:
        error(state, "Expected 'SMOOSH' for string concatenation")
        return None

    operands = []
    first = parse_factor(state)
    if not first:
        error(state, "Expected expression after 'SMOOSH'")
        return None
    operands.append(first)

    # Allow multiple operands separated by AN
    while state['current_token'] and state['current_token']['pattern'] == 'AN':
        # consume 'AN'
        advance(state)
        nxt = parse_factor(state)
        if not nxt:
            error(state, "Expected expression after 'AN' in SMOOSH")
            return None
        operands.append(nxt)

    results = {
        'node': 'smoosh_expression',
        'operator': operator_token['pattern'],
        'operands': operands
    }
    return results
    
def parse_comparison_expression(state):
    # Parse comparison
    # expr ::= BIGGR OF | SMALLR OF | BOTH SAEM | DIFFRINT
    operator_token = match(state, "Comparison Operator")

    operand1 = parse_factor(state)

    if state['current_token'] and state['current_token']['pattern'] == 'AN':
        advance(state)
    else:
        error(state, "Expected 'AN' between operands")
        return None

    operand2 = parse_factor(state)

    operand1_value = extract_value(operand1)
    operand2_value = extract_value(operand2)

    expression_extracted = f"{operator_token['pattern']} {operand1_value} AN {operand2_value}"

    results = {
        'node': 'comparison_expression',
        'operator': operator_token['pattern'],
        'operand1': operand1,
        'operand2': operand2,
        'values': expression_extracted
    }
    return results

def parse_arithmetic_expression(state):
    # Parse arithmetic
    # expr ::= SUM OF | DIFF OF | PRODUKT OF | QUOSHUNT OF | MOD OF
    operator_token = match(state, "Arithmetic Operator")
    
    operand1 = parse_factor(state)

    if state['current_token'] and state['current_token']['pattern'] == 'AN':
        advance(state)
    else:
        error(state, "Expected 'AN' between operands")
        return None

    operand2 = parse_factor(state)

    operand1_value = extract_value(operand1)
    operand2_value = extract_value(operand2)

    expression_extracted = f"{operator_token['pattern']} {operand1_value} AN {operand2_value}"

    results = {
        'node': 'arithmetic_expression',
        'operator': operator_token['pattern'],
        'operand1': operand1,
        'operand2': operand2,
        'values': expression_extracted
    }
    return results

def parse_maek_expression(state):
    """Parse MAEK expression: MAEK x A NUMBR or MAEK x TROOF"""
    match(state, "Type Casting", "MAEK")
    
    operand = parse_simple_expression(state)
    if not operand:
        error(state, "Expected expression after MAEK")
        return None
    
    # Check for optional 'A' keyword
    if state['current_token'] and state['current_token']['pattern'] == 'A':
        match(state, "Explicit Casting", "A")
    
    type_token = match(state, "TYPE Literal")
    if not type_token:
        error(state, "Expected type after MAEK expression")
        return None
    
    return {
        'node': 'maek_expression',
        'operand': operand,
        'target_type': type_token['pattern']
    }

def parse_simple_expression(state):
    # Parse identifiers and literals 
    current_token = state['current_token']

    if current_token['token_name'] == 'Variable Identifier':
        advance(state)
        return {'node': 'identifier', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'String Literal':
        advance(state)
        return {'node': 'string_literal', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'Boolean Literal':
        advance(state)
        return {'node': 'boolean_literal', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'Float Literal':
        advance(state)
        return {'node': 'float_literal', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'Integer Literal':
        advance(state)
        return {'node': 'integer_literal', 'value': current_token['pattern']}
    else:
        error(state, f"Unexpected expression: '{current_token['pattern']}'")
        return None