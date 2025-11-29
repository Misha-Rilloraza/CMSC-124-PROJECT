from helper import error, match, end_of_line
from expressions import parse_expression

def parse_output_statement(state):
    # Parse VISIBLE
    # for displaying output
    token = match(state, "Output Keyword", "VISIBLE")
    if not token:
        error(state, "Expected 'VISBLE' for output statement")
        return None
    
    expressions = []
    while state['current_token'] and not end_of_line(state):
        expr = parse_expression(state)
        if expr:
            expressions.append(expr)
        else:
            error(state, "Expected expression after 'VISIBLE'")

    if not expressions:
        error(state, "'VISIBLE' requires an expression to output")
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
        'identifier': var_identifier['patterm']
    }

def parse_variable_declaration_start(state):
    # Parse WAZZUP
    # start of variable declaration block
    token = match(state, "Variable List Delimiter", "WAZZUP")
    if token and end_of_line(state):
        return {'node': 'variable_list_start'}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after WAZZUP")
    return None

def parse_variable_declaration_end(state):
    # Parse BUHBYE
    # end of variable declaration block
    token = match(state, "Variable List Delimiter", "BUHBYE")
    if token and end_of_line(state):
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
        expression = parse_expression(state)
        if not expression:
            error(state, "Expected expression after 'R'")
            return None
    elif state['current_token'] and state['current_token']['pattern'] == 'ITZ':
        assign_token = match(state, "Variable Assignment", "ITZ")
        operator = 'assignment'
        expression = parse_expression(state)
        if not expression:
            error(state, "Expected expression after 'ITZ'")
            return None
    else:
        return None
    
    expr = parse_expression(state)
    if not expr:
        error(state, "Expected expression after assignment operator")
        return None
    
    if not end_of_line(state):
        error(state, "Unexpected tokens after assignment")
        return None
    
    result = {
        'node': 'variable_assignment',
        'identifier': var_identifier['pattern'],
        'operator': operator,
        'expression': expr
    }
    return result