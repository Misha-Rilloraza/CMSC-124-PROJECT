from helper import extract_value, error, match, advance, end_of_line
from expressions import parse_expression

in_variable_block = False

def parse_output_statement(state):
    # Parse VISIBLE
    # for displaying output
    token = match(state, "Output Keyword", "VISIBLE")
    if not token:
        error(state, "Expected 'VISBLE' for output statement")
        return None
    
    # statements following VISIBLE can be expressions or literals
    expressions = []
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression after 'VISIBLE'")
        return None
    expressions.append(expr)

    # for multiple expressions
    while state['current_token'] and state['current_token']['pattern'] == 'AN':
        advance(state)  # consume 'AN'
        expr = parse_expression(state)
        if not expr:
            error(state, "Expected expression after 'AN'")
            return None
        expressions.append(expr)
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after output statement")
        return None
    
    return {
        'node': 'output_statement',
        'expressions': expressions
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
    global in_variable_block, wazzup_encountered
    token = match(state, "Variable List Delimiter", "WAZZUP")
    if token and end_of_line(state):
        in_variable_block = True
        return {'node': 'variable_list_start'}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after WAZZUP")
    return None

def parse_variable_declaration_end(state):
    # Parse BUHBYE
    # end of variable declaration block
    global in_variable_block
    token = match(state, "Variable List Delimiter", "BUHBYE")
    if token and end_of_line(state):
        in_variable_block = False
        return {'node': 'variable_list_end'}
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
    # Consider ITZ for variable assignment
    # Consider R for variable reassignment
    # expressions/values could be any literals
    var_identifier = match(state, "Variable Identifier")
    if not var_identifier:
        return None
    
    if state['current_token'] and state['current_token']['pattern'] == 'R':
        assign_token = match(state, "Variable Reassignment", "R")
        operator = 'reassignment'
        used_operator = 'R'
        # expression = parse_expression(state)
        # if not expression:
        #     error(state, "Expected expression after 'R'")
        #     return None
    elif state['current_token'] and state['current_token']['pattern'] == 'ITZ':
        assign_token = match(state, "Variable Assignment", "ITZ")
        operator = 'assignment'
        used_operator = 'ITZ'
        # expression = parse_expression(state)
        # if not expression:
        #     error(state, "Expected expression after 'ITZ'")
        #     return None
    else:
        if end_of_line(state):
            result = {
                'node': 'variable_reference',
                'identifier': var_identifier['pattern']
            }
        else:
            error(state, "Expected 'R' or 'ITZ' for variable assignment")
            return None
    
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression after assignment operator")
        return None
    
    expr_string = extract_value(expr)
    expr_type = expr.get('node', 'unknown')
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after assignment")
        return None
    
    result = {
        'node': 'variable_assignment',
        'identifier': var_identifier['pattern'],
        'operator': operator,
        'used_operator': used_operator,
        'expression': expr,
        'expression_string': expr_string,
        'expression_type': expr_type
    }
    return result

def parse_variable_reference(state):
    # this function parses variable references
    # variable references are just variable identifiers used in expressions
    var_identifier = match(state, "Variable Identifier")
    if not var_identifier:
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after variable reference")
        return None
    
    result = {
        'node': 'variable_reference',
        'identifier': var_identifier['pattern']
    }
    return result