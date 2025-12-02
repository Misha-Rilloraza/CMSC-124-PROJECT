from helper import error, match, advance, end_of_line, peek_token
from expressions import parse_expression

def parse_output_statement(state):
    # Parse VISIBLE
    # for displaying output
    token = match(state, "Output Keyword", "VISIBLE")
    if not token:
        print("DEBUG: Not a VISIBLE statement")
        return None
        
    expression = parse_expression(state)
    
    if not expression:
        error(state, "Expected expression after VISIBLE")
        return None
        
    if not end_of_line(state):
        error(state, "Unexpected tokens after VISIBLE expression")
        return None
    
    return {
        'node': 'output_statement',
        'expression': expression
    }

def parse_input_statement(state):
    # Parse GIMMEH
    # for taking input, mostly will happen in GUI
    token = match(state, "Input Keyword", "GIMMEH")
    if not token:
        error(state, "Expected 'GIMMEH' for input statement")
        return None
    var_identifier = match(state, "Variable Identifier")
    if not var_identifier:
        error(state, "Expected variable identifier after 'GIMMEH'")
        return None
    if not end_of_line(state):
        error(state, "Unexpected tokens after 'GIMMEH' statement")
        return None
    
    return {
        'node': 'input_statement',
        'identifier': var_identifier['pattern']
    }

def parse_variable_declaration_start(state):
    # Parse WAZZUP
    # start of variable declaration block
    token = match(state, "Variable List Delimiter", "WAZZUP")
    if token and end_of_line(state):
        return {'node': 'variable_list_start', 'token': token}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after WAZZUP")
    return None

def parse_variable_declaration_end(state):
    # Parse BUHBYE
    # end of variable declaration block
    token = match(state, "Variable List Delimiter", "BUHBYE")
    if token and end_of_line(state):
        return {'node': 'variable_list_end', 'token': token}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after BUHBYE")
    return None

def parse_variable_declaration(state, in_var_declaration):
    # Parse the variable declarations
    # preceding I HAS A <varname>
    # Optional assignment: I HAS A <varname> ITZ <value>
    i_has_a = match(state, "Variable Declaration", "I HAS A")
    if not i_has_a:
        error(state, "Expected 'I HAS A' for variable declaration")
        return None
    
    var_identifier = match(state, "Variable Identifier")
    if not var_identifier:
        error(state, "Expected variable identifier after 'I HAS A'")
        return None
    
    # Optional assignmen
    assignment = None
    if state['current_token'] and state['current_token']['pattern'] == 'ITZ':
        itz_token = match(state, "Variable Assignment", "ITZ")
        if itz_token:
            assignment = parse_expression(state)
            if not assignment:
                error(state, "Expected expression after 'ITZ'")
                return None
    
    # if end_of_line(state):
    #     error(state, "Unexpected tokens after variable declaration")
    #     return None

    if not end_of_line(state):
        error(state, f"Unexpected tokens after variable declaration: {state['current_token']['pattern'] if state['current_token'] else 'EOF'}")
        return None
    
    result = {
        'node': 'variable_declaration',
        'identifier': var_identifier['pattern'],
        'assignment': assignment,
        'in_var_declaration': in_var_declaration
    }

    return result

def parse_variable_assignment(state): 
    # Parse variable assignment
    # consider ITZ for variable assignment
    # consider R for variable reassignment
    start_pos = state["position"]
    
    var_token = match(state, "Variable Identifier")
    if not var_token:
        state["position"] = start_pos
        return None
    
    
    # Get identifier - use the correct field name
    identifier = var_token.get("value", var_token.get("pattern", ""))
    print(f"poot: iden extracted: '{identifier}'")
    
    if end_of_line(state):
        return {
            'node': 'variable_reference',
            'identifier': identifier
        }
    
    next_token = peek_token(state)
    print(f"poot: next token: {next_token}")
    
    if not next_token:
        return {
            'node': 'variable_reference',
            'identifier': identifier
        }
    
    assign_token = None
    operator = None
    used_operator = None
    
    next_token_value = next_token.get("value", next_token.get("pattern", ""))
    print(f"poot: Next token value: '{next_token_value}'")
    
    if next_token_value == "R":
        print(f"poot: bilis R")
        assign_token = match(state, "Variable Reassignment", "R")
        if assign_token:
            operator = 'reassignment'
            used_operator = 'R'
            print(f"poot: mathc R")
    
    elif next_token_value == "ITZ":
        print(f"poot: bilis ITZ")
        assign_token = match(state, "Variable Assignment", "ITZ")
        if assign_token:
            operator = 'assignment'
            used_operator = 'ITZ'
            print(f"poot: match ITZ")
    
    if not assign_token:
        state["position"] = start_pos + 1
        return {
            'node': 'variable_reference',
            'identifier': identifier
        }
    
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression after assignment operator")
        state["position"] = start_pos
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after assignment")
        state["position"] = start_pos
        return None
    
    result = {
        'node': 'variable_assignment',
        'identifier': identifier,
        'operator': operator,
        'used_operator': used_operator,
        'expression': expr
    }
    
    return result