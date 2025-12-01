from lexer import tokenizer
from helper import extract_value, error, match, end_of_line
from statements import *
from conditions import *

def parse_whole(filename):
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
        # return parse_variable_assignment(state)
        if len(state['tokens']) > 1:
            next_token = state['tokens'][1]['pattern']
            if next_token == 'R' or next_token == 'ITZ':
                return parse_variable_assignment(state)
            elif next_token == 'IS NOW A':
                return parse_is_now_a_type_cast(state)
            else:
                # this is to handle cases where variable reference is not alone
                return parse_variable_reference(state)
        else:
            # we parse as variable reference if single token
            return parse_variable_reference(state)
    elif pattern_value == "VISIBLE":
        return parse_output_statement(state)
    elif pattern_value == "GIMMEH":
        return parse_input_statement(state)
    elif pattern_value == "SMOOSH":
        return parse_smoosh(state)
    elif pattern_value == "MAEK":
        return parse_type_casting(state)
    elif pattern_value == "O RLY?":
        return parse_if_statement_start(state)
    elif pattern_value == "YA RLY":
        return parse_then_statement(state)
    elif pattern_value == "MEBBE":
        return parse_elseif_statement(state)
    elif pattern_value == "NO WAI":
        return parse_else_statement(state)
    elif pattern_value == "OIC":
        return parse_if_end(state)
    elif pattern_value == "WTF?":
        return parse_switch_start(state)
    elif pattern_value == "OMG":
        return parse_switch_cases(state)
    elif pattern_value == "OMGWTF":
        return parse_switch_end(state)
    # for expressions as standalone statements
    # most likely that appears in the beginning as well
    elif pattern_value in ["BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF", 
                       "BOTH OF", "EITHER OF", "WON OF", "ALL OF", "ANY OF",
                       "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF",
                       "NOT", "SMOOSH", "MAEK"]:
        from expressions import parse_expression
        expr = parse_expression(state)
        if expr and end_of_line(state):
            return {
                'node': 'expression_statement',
                'expression': expr
            }
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

# def check_conditionals(token):
#     # Check if line starts with conditonal expression
#     # comparison
#     if token['pattern'] in ["BOTH SAEM", "DIFFRINT", "BIGGR OF", "SMALLR OF"]:
#         return True
#     # logical
#     if token['pattern'] in ["BOTH OF", "EITHER OF", "WON OF", "ALL OF", "ANY OF", "NOT"]:
#         return True
#     # arithmetic
#     if token['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
#         return True
#     # boolean
#     if token['token_name'] == "Boolean Literal":
#         return True
#     # type
#     if token['token_name'] == "Type Literal":
#         return True
#     # stirng
#     if token['token_name'] == "String Literal":
#         return True
#     # numbers
#     if token['token_name'] in ["Integer Literal", "Float Literal"]:
#         return True
#     # variable identifiers
#     if token['token_name'] == "Variable Identifier":
#         return True
    
#     return False

def print_results(parse_tree, errors):
    print("\n" + "="*60)
    print("PARSING RESULTS")
    print("="*60)

    if not parse_tree:
        print("❌ No parse tree to display!")
        return

    print(f"\n📊 Parsed ({len(parse_tree)} lines):")
    for line_data in parse_tree:
        line_no = line_data.get('line_number', 'unknown')
        result = line_data.get('parse_result', {})

        print(f"\nLine {line_no}: ", end="")

        # print tokens in a list format
        tokens = [t['pattern'] for t in line_data.get('tokens', [])]
        print(f"{tokens}")
        
        node_type = result.get('node', 'unknown')
        print(f"  └─ {node_type}")

        # starting from the top
        if node_type == 'start_of_program':
            print("-- HAI (start of program)")
        elif node_type == 'end_of_program':
            print("-- KTHXBYE (end of program)")
        elif node_type == 'variable_list_start':
            print("-- WAZZUP (start of vardecl block)")
        elif node_type == 'variable_list_end':
            print("-- BUHBYE (end of vardecl block)")

        # details of the variable declarations and assignments if yes
        elif node_type == 'variable_declaration':
            identifier = result.get('identifier', 'unknown')
            print(f" - {identifier}", end="")
            if result.get('assignment'):
                assign = result['assignment']
                assign_type = assign.get('node', 'unknown')
                value = assign.get('value', assign.get('name', ''))
                print(f" = {assign_type}: '{value}'")
            else:
                print(" (no assignment)")
        
        # for the output statement nodes
        # can be expressions
        # can be variable identifiers
        # can be literals
        elif node_type == 'output_statement':
            if 'expressions' in result:
                expressions = result.get('expressions', [])
                if len(expressions) == 1:
                    expr = expressions[0]
                    expr_string = extract_value(expr)
                    expr_type = expr.get('node', 'unknown')
                    print(f" - VISIBLE: {expr_type}: '{expr_string}'")
                else:
                    for expr in expressions:
                        expr_string = extract_value(expr)
                        expr_type = expr.get('node', 'unknown')
                        print(f"     - {expr_type}: '{expr_string}'")
            elif 'expression' in result:
                expr = result.get('expression', {})
                expr_string = extract_value(expr)
                expr_type = expr.get('node', 'unknown')
                print(f" - VISIBLE: {expr_type}: '{expr_string}'")
            else:
                print(f" - VISIBLE (no expression details)")
        
        elif node_type == 'input_statement':
            identifier = result.get('identifier', 'unknown')
            print(f" - GIMMEH: '{identifier}'")
        
        # variable assignment detauils
        # handle assignment and reassignment
        elif node_type == 'variable_assignment':
            identifier = result.get('identifier', 'unknown')
            operator = result.get('used_operator', result.get('operator', 'unknown'))
            expr_string = result.get('expression_string', extract_value(result.get('expression', {})))
            expr_type = result.get('expression_type', 'expression')
            print(f" - {identifier} {operator} {expr_type}: '{expr_string}'")
            

        elif node_type == 'variable_reference':
            identifier = result.get('identifier', 'unknown')
            print(f" - Variable Reference: '{identifier}'")

        # elif node_type == 'variable_assignment':
        #     identifier = result.get('identifier', 'unknown')
        #     operator = result.get('operator', 'unknown')
        #     expr_string = extract_value(result.get('expression', {}))
        #     expr_type = result.get('expression', {}).get('node', 'unknown')
        #     print(f" - {identifier} {operator} {expr_type}: '{expr_string}'")

        # for the expression details
        elif node_type == 'expression_statement':
            expr = result.get('expression', {})
            expr_string = extract_value(expr)
            expr_type = expr.get('node', 'unknown')
            print(f" - Expression: {expr_type}: '{expr_string}'")

        # smoosh details
        elif node_type == 'smoosh_expression':
            parts = result.get('parts', [])
            part_strings = [extract_value(part) for part in parts]
            print(f" - SMOOSH parts: {part_strings}")

        # type casting details
        elif node_type == 'type_casting':
            target_type = result.get('target_type', 'unknown')
            expr_string = extract_value(result.get('expression', {}))
            expr_type = result.get('expression', {}).get('node', 'unknown')
            print(f" - MAEK to {target_type}: {expr_type}: '{expr_string}'")

        # conditionals
        elif result['node'] == 'if_statement_start':
            print(f" - IF statement begins")
        
        elif result['node'] == 'then_statement':
            print(f" - THEN branch begins")
        
        elif result['node'] == 'else_if_statement':
            condition_string = extract_value(result['condition'])
            print(f" - ELSE IF branch begins")
            print(f"       Condition: {result['condition']['node']}: '{condition_string}'")
        
        elif result['node'] == 'else_statement':
            print(f" - ELSE branch begins")
        
        elif result['node'] == 'if_statement_end':
            print(f" - IF statement ends")
        
        # switch statements
        elif result['node'] == 'switch_start':
            expr_string = extract_value(result['expression'])
            print(f" - SWITCH statement begins")
            print(f"       Expression: {result['expression']['node']}: '{expr_string}'")
        
        elif result['node'] == 'switch_case':
            case_string = extract_value(result['case_value'])
            print(f" - CASE branch begins")
            print(f"       Case value: {result['case_value']['node']}: '{case_string}'")
        
        elif result['node'] == 'default_case':
            print(f" - DEFAULT branch begins")
        
        elif result['node'] == 'switch_end':
            print(f" - SWITCH statement ends")
        
        else:
            print(f" - [Unhandled node type: {node_type}]")

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ No parsing errors found!")    


# if __name__ == "__main__":
#     parse_tree, errors = parse("t1.lol")
#     print_results(parse_tree, errors)
