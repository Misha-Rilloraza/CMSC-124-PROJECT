def extract_value(expression):
    if not expression:
        return "[empty]"
    
    node_type = expression.get('node', '')
    
    if node_type in ['identifier', 'string_literal', 'boolean_literal', 
                    'type_literal', 'float_literal', 'integer_literal']:
        return expression.get('value', expression.get('name', '[no value]'))
    
    elif node_type == 'arithmetic_expression':
        op1 = extract_value(expression.get('operand1', {}))
        op2 = extract_value(expression.get('operand2', {}))
        return f"{expression.get('operator', '')} {op1} AN {op2}"
    
    elif node_type == 'comparison_expression':
        op1 = extract_value(expression.get('operand1', {}))
        op2 = extract_value(expression.get('operand2', {}))
        return f"{expression.get('operator', '')} {op1} AN {op2}"
    
    return f"[complex: {node_type}]"

def error(state, message):
    state['errors'].append(message)
    print(f"Error on line {state['line_no']}: {message}")

def match(state, expected_token, expected_value=None):
    current_token = state['current_token']
    if current_token and current_token['token_name'] == expected_token:
        if expected_value is None or current_token['pattern'] == expected_value:
            print(f"Matched token: '{current_token['pattern']}' (type: {current_token['token_name']})")
            state['position'] += 1
            if state['position'] < len(state['tokens']):
                state['current_token'] = state['tokens'][state['position']]
            else:
                state['current_token'] = None
            return current_token
    return None

def peek_token(state, expected_value=None, expected_type=None):
    """
    Peek at next token without consuming.
    """
    if state["position"] >= len(state["tokens"]):
        return None
    
    token = state["tokens"][state["position"]]
    
    if expected_value:
        if token["value"] == expected_value:
            return token
        return None
    
    if expected_type:
        if token["type"] == expected_type:
            return token
        return None
    
    return token

def advance(state):
    state['position'] += 1
    if state['position'] < len(state['tokens']):
        state['current_token'] = state['tokens'][state['position']]
    else:
        state['current_token'] = None

def end_of_line(state):
    return state['current_token'] is None