def extract_value(expr_node):
    # extracts the string value, mas malalim na dito thoooo
    # we need to lagay toh sa kabila    
    if expr_node is None:
        return ""
    
    if not isinstance(expr_node, dict):
        return str(expr_node)
    
    node_type = expr_node.get('node', '')
    print(f"DEBUG: node_type='{node_type}'")
    
    # handle different node types
    if node_type == 'variable_reference':
        result = expr_node.get('identifier', '')
        return result
    
    elif node_type == 'string_literal':
        result = expr_node.get('value', '')
        return result
    
    elif node_type == 'boolean_literal':
        value = expr_node.get('value', False)
        result = "WIN" if value else "FAIL"
        return result
    
    elif node_type == 'integer_literal':
        result = str(expr_node.get('value', 0))
        return result
    
    elif node_type == 'float_literal':
        result = str(expr_node.get('value', 0.0))
        return result
    
    elif node_type == 'type_literal':
        result = expr_node.get('value', '')
        return result
    
    elif node_type == 'smoosh_expression':
        expressions = expr_node.get('expressions', [])
        values = []
        for i, expr in enumerate(expressions):
            value = extract_value(expr)
            values.append(value)
        result = " ".join(values)
        print(f"smoosh_expression -> '{result}'")
        return result
    
    else:
        if 'value' in expr_node:
            result = expr_node['value']
            return str(result)
        elif 'identifier' in expr_node:
            result = expr_node['identifier']
            return result
        else:
            return ""

def error(state, message):
    state['errors'].append(message)
    print(f"Error on line {state['line_no']}: {message}")

def match(state, token_type, token_value=None):
    # for error handling mostly
    # para alam kung ano ung expected token na rin (validates)
    if state["position"] >= len(state["tokens"]):
        return None
    
    token = state["tokens"][state["position"]]
    
    token_type_match = token.get("token_name") == token_type or token.get("type") == token_type
    
    if not token_type_match:
        return None
    
    if token_value is not None:
        token_val = token.get("pattern") or token.get("value")
        if token_val != token_value:
            return None
    
    # matched!!!!!!!!!
    state["position"] += 1
    if state["position"] < len(state["tokens"]):
        state["current_token"] = state["tokens"][state["position"]]
    else:
        state["current_token"] = None
    
    return token

def peek_token(state, expected_value=None, expected_type=None):
    # inspect current token without consuming
    # helps with decisions for parsing rules without the need to consume yet
    if state["position"] >= len(state["tokens"]):
        return None
    
    token = state["tokens"][state["position"]]
    
    if expected_value:
        token_value = token.get('pattern') or token.get('value') or ''
        if token_value != expected_value:
            return None
    
    if expected_type:
        token_type = token.get('token_name') or token.get('type') or ''
        if token_type != expected_type:
            return None
    
    return token

def advance(state):
    # this is a utility function that moves through the token stream
    # consuming tokens | to update associated token reference
    # retrieves the token and stores to current_token (acts as a cursor basically)
    state['position'] += 1
    if state['position'] < len(state['tokens']):
        state['current_token'] = state['tokens'][state['position']]
    else:
        # we've reached the end of the input (code sample)
        state['current_token'] = None

def end_of_line(state):
    # end of line considerations
    # pagtapos ng tokens
    # terminators
    # new statement (start)
    if state["position"] >= len(state["tokens"]):
        return True
    
    # we used these to be able to tell the token parsed that can be used for
    # the implementation of theparsing rule to apply
    # we retrieve the tokens at the current position, position as the index
    current_token = state["tokens"][state["position"]]
    # we extract the token type
    token_type = current_token.get('token_name') or current_token.get('type', '')
    # we extract the token value
    token_value = current_token.get('pattern') or current_token.get('value', '')
        
    # may instances na nageend sa MKAY ung statement
    # mkay is considered terminator
    # MKAY ; Argument End
    if token_value == 'MKAY':
        return True
    
    # this checks if next token starts a new statemnt
    if token_value in ['VISIBLE', 'GIMMEH', 'I', 'HAI', 'KTHXBYE', 
                       'O RLY?', 'YA RLY', 'MEBBE', 'NO WAI', 'OIC',
                       'WTF?', 'OMG', 'OMGWTF', 'IM IN YR', 'IM OUTTA YR']:
        return True

    return False