from lexer import tokenizer

# this is a parser
# this parser is a recursive descent parser
# it will take the tokens from the lexer
# top-down parsing
# LL(1) parser
# it will build a parse tree
# then we will build an abstract syntax tree
# then we will do semantic analysis
# parse it line by line (parsed independently)
# checks for proper pairing

def parse(filename):
    try:
        tokens = tokenizer(filename)
        print(f"Tokenization complete. Found {len(tokens)} tokens.")

        # line by line parsing
        lines = {}
        for token in tokens:
            line_no = token['line_number']
            if line_no not in lines:
                lines[line_no] = []
            lines[line_no].append(token)

        # show found tokens per line with the number and column
        # for line_no in sorted(lines.keys()):
        #     print(f"Line {line_no}:")
        #     for token in lines[line_no]:
        #         print(f"  Column {token['column_number']}: {token['token_name']} ({token['pattern']})")

        parse_tree = []
        errors = []
        hai_start = False
        bye_end = False
        in_var_declaration = False
        variable_declarations = []

        # parse each line independently
        for line_no in lines:
            line_tokens = lines[line_no]

            if not line_tokens:
                continue

            print(f"\n=== Parsing Line {line_no} ===")
            print(f"Tokens: {[t['pattern'] for t in line_tokens]}")

            # state for line parsing
            state = {
                "position": 0,
                "tokens": line_tokens,
                "current_token": line_tokens[0],
                "line_no": line_no,
                "errors": []
            }

            result = parse_line(state)

            if state["errors"]:
                for error in state["errors"]:
                    errors.append({
                        "line_number": line_no,
                        "error": error
                    })

            # track hai-kthxbye pairing
            if result:
                if result['node'] == 'start_of_program':
                    if hai_start:
                        errors.append(f"Line {line_no}: Multiple HAI statements")
                        if result['node'] == 'variable_list_start':
                            in_var_declaration = True
                            variable_declarations = []
                        elif result['node'] == 'variable-list_end':
                            in_var_declaration = False
                            if variable_declarations:
                                parse_tree.append({
                                    'line_number': line_no,
                                    'ast': {
                                        'node': 'variable_declaration_block',
                                        'declarations': variable_declarations
                                    },
                                    'tokens': ['WAZZUP...BUHBYE block']
                                })
                        elif in_var_declaration and result['node'] == 'variable_declaration':
                            variable_declarations.append(result)
                        else:
                            if not in_var_declaration or result['node'] not in ['variable_declaration']:
                                parse_tree.append({
                                    'line_number': line_no,
                                    'ast': result,
                                    'tokens': line_tokens
                                })
                    hai_start = True
                elif result['node'] == 'end_of_program':
                    if bye_end:
                        errors.append(f"Line {line_no}: Multiple KTHXBYE statements")
                    bye_end = True

                if not state["errors"]:
                    parse_tree.append({
                        "line_number": line_no,
                        "parse_result": result,
                        "tokens": line_tokens
                    })

        if not hai_start:
            errors.append("Error: Missing HAI statement at the beginning of the program.")
        if not bye_end:
            errors.append("Error: Missing KTHXBYE statement at the end of the program.")
        if hai_start and bye_end:
            hai_line = None
            bye_line = None
            for entry in parse_tree:
                if entry['parse_result']['node'] == 'start_of_program':
                    hai_line = entry['line_number']
                elif entry['parse_result']['node'] == 'end_of_program':
                    bye_line = entry['line_number']
            if hai_line and bye_line and hai_line < bye_line:
                print("\nProgram structure is valid with HAI and KTHXBYE.")
            else:
                errors.append("Error: KTHXBYE appears before HAI.")
    except Exception as e:
        print(f"Parsing error: {e}")
        return None
    
    return parse_tree, errors

def parse_line(state):
    # parse lines, complete statement per line
    current_token = state['current_token']
    pattern_value = current_token['pattern']

    print(f"First token: '{pattern_value}' (type: {current_token['token_name']})")

    if pattern_value == "HAI":
        return parse_hai(state)
    elif pattern_value == "KTHXBYE":
        return parse_kthxbye(state)
    elif pattern_value == "WAZZUP":
        return parse_variable_declaration_start(state)
    elif pattern_value == "BUHBYE":
        return parse_variable_declaration_end(state)
    elif pattern_value == "I HAS A":
        return parse_variable_declaration(state, in_var_declaration=True)
    elif current_token['token_name'] == "Variable Identifier":
        return parse_variable_assignment(state)
    else:
        error(state, f"Unexpected statement: '{pattern_value}'")
        return None
    
def parse_hai(state):
    # Parse HAI
    # begin of program
    token = match(state, "Code Delimiter", "HAI")
    if token and end_of_line(state):
        return {"node": "start_of_program"}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after HAI.")
    return None

def parse_kthxbye(state):
    # Parse KTHXBYE
    # end of program
    token = match(state, "Code Delimiter", "KTHXBYE")
    if token and end_of_line(state):
        return {"node": "end_of_program"}
    elif not end_of_line(state):
        error(state, "Unexpected tokens after KTHXBYE.")
    return None

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
    
    if state['current_token']['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
        return parse_comparison_expression(state)
    elif state['current_token']['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
        return parse_arithmetic_expression(state)
    elif state['current_token']['token_name'] in ["Variable Identifier", "String Literal", "Boolean Literal", "Type Literal", "Float Literal", "Integer Literal"]:
        return parse_simple_expression(state)
    else:
        error(state, f"Unexpected token in expression: {state['current_token']['pattern']}")
        return None
    
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

def extract_value(node):
    if node['node'] in ['identifier', 'string_literal', 'boolean_literal', 'type_literal', 'float_literal', 'integer_literal']:
        return node['value']
    return None

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

def advance(state):
    state['position'] += 1
    if state['position'] < len(state['tokens']):
        state['current_token'] = state['tokens'][state['position']]
    else:
        state['current_token'] = None

def end_of_line(state):
    return state['current_token'] is None

# def print_results(parse_tree, errors):
#     print("\n" + "="*50)
#     print("PARSING RESULTS")
#     print("="*50)

#     if errors:
#         print("\n❌ ERRORS:")
#         for error in errors:
#             print(f"  {error}")
#     else:
#         print("\n✅ No parsing errors found!")

#     print(f"\n📋 Parsed {len(parse_tree)} lines:")
#     for line_data in parse_tree:
#         line_no = line_data['line_number']
#         result = line_data['parse_result']
#         tokens = [t['pattern'] for t in line_data['tokens']]

#         print(f"\nLine {line_no}: {tokens}")
#         print(f"  Node: {result['node']}")

def print_results(parse_tree, errors):
    print("\n" + "="*60)
    print("PARSING RESULTS")
    print("="*60)

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ No parsing errors found!")

    print(f"\n📊 Parsed ({len(parse_tree)} lines):")
    for line_data in parse_tree:
        line_no = line_data['line_number']
        result = line_data['parse_result']

        print(f"\nLine {line_no}: ", end="")

        # print tokens in a list format
        # indicate structure
        tokens = [t['pattern'] for t in line_data['tokens']]
        print(f"{tokens}")
        print(f"  └─ {result['node']}")

        # details of the variable declarations and assignments if yes
        if result['node'] == 'variable_declaration':
            print(f" - {result['identifier']}", end="")
            if result.get('assignment'):
                assign = result['assignment']
                value = assign.get('value', assign.get('name', ''))
                print(f" = {assign['node']}: '{value}'")
                if assign['node'] == 'arithmetic_expression' and 'values' in assign:
                    print(f"\t^--Extracted Expression: {assign['values']}")
            else:
                print(" (no assignment)")

if __name__ == "__main__":
    parse_tree, errors = parse("t1.lol")
    print_results(parse_tree, errors)
