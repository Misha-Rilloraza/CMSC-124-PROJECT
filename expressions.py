from helper import extract_value, error, match, advance, end_of_line

def parse_expression(state):
    # be mindful of operator precedence
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
    
    if state['current_token']['pattern'] == "NOT":
        return parse_unary_expression(state)
    if state['current_token']['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
        return parse_comparison_expression(state)
    elif state['current_token']['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
        return parse_arithmetic_expression(state)
    elif state['current_token']['token_name'] in ["Variable Identifier", "String Literal", "Boolean Literal", "Type Literal", "Float Literal", "Integer Literal"]:
        return parse_simple_expression(state)
    elif state['current_token']['pattern'] == "SMOOSH":
        return parse_smoosh(state)
    # elif state['current_token']['pattern'] == "MAEK" or (state['current_token']['token_name'] != "Variable Identifier" and state['current_token']['pattern'] == "IS NOW A"):
    #     return parse_type_casting(state)
    elif state['current_token']['pattern'] == "MAEK":
        return parse_explicit_type_cast(state)
    elif state['current_token']['pattern'] == "Variable Identifier":
        if state['current_token'] and state['current_token']['pattern'] == "IS NOW A":
            return parse_is_now_a_type_cast(state)
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
    
def parse_comparison_expression(state):
    # Parse comparison
    # expr ::= BIGGR OF | SMALLR OF | BOTH SAEM | DIFFRINT
    operator_token = match(state, "Comparison Operator")

    operand1 = parse_arithmetic(state)

    if state['current_token'] and state['current_token']['pattern'] == 'AN':
        advance(state)
    else:
        error(state, "Expected 'AN' between operands")
        return None

    operand2 = parse_arithmetic(state)

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
    elif current_token['token_name'] == 'Type Literal':
        advance(state)
        return {'node': 'type_literal', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'Float Literal':
        advance(state)
        return {'node': 'float_literal', 'value': current_token['pattern']}
    elif current_token['token_name'] == 'Integer Literal':
        advance(state)
        return {'node': 'integer_literal', 'value': current_token['pattern']}
    else:
        error(state, f"Unexpected expression: '{current_token['pattern']}'")
        return None
    
def parse_smoosh(state):
    # Parse SMOOSH
    operator_token = match(state, "String Concatenation", "SMOOSH")
    if not operator_token:
        return None
    
    strings = []
    while True:
        string_expr = parse_simple_expression(state)
        if not string_expr:
            error(state, "Expected string in SMOOSH")
            return None
        strings.append(string_expr)

        if state['current_token'] and state['current_token']['pattern'] == "AN":
            advance(state)
        else:
            break

        if not state['current_token']:
            error(state, "Unexpected end of line in SMOOSH")
            return None
    
    if len(strings) < 2:
        error(state, "SMOOSH requires at least two strings")
        return None
    
    results = {
        'node': 'smoosh_expression',
        'strings': strings,
        'token': operator_token
    }
    return results

def parse_type_casting(state):
    # tokens used: MAEK <expr> A <literal>
    # another way of type casting: IS NOW A
    # be mindful of both
    token = state.get('current_token')
    if not token:
        return None
    
    if state['current_token'] and state['current_token']['pattern'] == "MAEK":
        return parse_explicit_type_cast(state)
    elif pattern_for_isnowa(token):
        return parse_is_now_a_type_cast(state)
    return None
    

def parse_explicit_type_cast(state):
    # Parse MAEK ... A ...
    operator_token = match(state, "Type Casting", "MAEK")
    if not operator_token:
        return None
    
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression after MAEK")
        return None
    
    a_token = match(state, "Type Casting Keyword", "A")
    if not a_token:
        error(state, "Expected 'A' after expression for type casting")
        return None
    
    type_literal = match(state, "Type Literal")
    if not type_literal or type_literal['type'] not in ['identifier', 'integer_literal', 'float_literal', 'string_literal', 'boolean_literal', 'type_literal']:
        error(state, "Expected type literal after 'A' for type casting")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after type casting")
        return None
    
    results = {
        'node': 'type_casting',
        'expression': expr,
        'target_type': type_literal['pattern'],
        'token': operator_token
    }
    return results

def parse_is_now_a_type_cast(state):
    # Parse ... IS NOW A ...
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression before 'IS NOW A'")
        return None
        
    is_NOW_A_token = match(state, "Recast Variable", "IS NOW A")
    if not is_NOW_A_token:
        error(state, "Expected 'IS NOW A' for type casting")
        return None
    
    type_literal = match(state, "Type Literal")
    if not type_literal or type_literal['type'] not in ['identifier', 'integer_literal', 'float_literal', 'string_literal', 'boolean_literal', 'type_literal']:
        error(state, "Expected type literal after 'A' for type casting")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after type casting")
        return None
    
    results = {
        'node': 'recast_typing',
        'expression': expr,
        'target_type': type_literal['pattern'],
        'token': is_NOW_A_token
    }
    return results

def pattern_for_isnowa(token):
    expression_start_tokens = [
        "identifier",         # variable names
        "integer_literal",
        "float_literal",
        "string_literal",
        "boolean_literal",
        "type_literal"
    ]
    return token and token['token_name'] in expression_start_tokens