from lexer import tokenizer

# diretso na, para madali na i-adjust kapag coconnect na sa frontend
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.advance()

    def advance(self):
        # move on to next token
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None
        return self.current_token

    def peek(self):
        # look at the next token without consuming it
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        return None

    def error_handle(self, token_type, value=None):
        # eExpect a specific token type and optionally value
        if self.current_token and self.current_token['token_name'] == token_type:
            if value is None or self.current_token['pattern'] == value:
                token = self.current_token
                self.advance()
                return token
            else:
                self.error(f"Expected {token_type} '{value}', but got '{self.current_token['pattern']}'")
        else:
            expected = f"{token_type} '{value}'" if value else token_type
            got = self.current_token['token_name'] if self.current_token else 'EOF'
            self.error(f"Expected {expected}, but got {got}")

    def error(self, message):
        # for the errors, indicate line number and column number
        # and unexpected error
        if self.current_token:
            line = self.current_token['line_number']
            column = self.current_token['column_number']
            raise SyntaxError(f"Line {line}, Column {column}: {message}")
        else:
            raise SyntaxError(f"Unexpected end of file: {message}")

    def parse_program(self):
        """Program -> HAI statements KTHXBYE"""
        print("Parsing program...")
        
        # always HAI sa start
        self.error_handle("Code Delimeter", "HAI")
        
        # sa bawat statement
        # dito mapupunta ung breakdown ng keywords
        # tapos iaarrange into a tree for easier analysis
        statements = []
        while self.current_token and self.current_token['pattern'] != "KTHXBYE":
            if self.current_token['pattern'] == "WAZZUP":
                statements.append(self.parse_variable_block())
            else:
                statement = self.parse_statement()
                if statement:
                    statements.append(statement)
        
        # KTHXBYE eof
        self.error_handle("Code Delimeter", "KTHXBYE")
        
        return {
            'type': 'program',
            'statements': statements
        }

    def parse_statement(self):
        # for the statements (parsing)
        if not self.current_token:
            return None
            
        token_value = self.current_token['pattern']
        
        # variable declaration
        if token_value == "I HAS A":
            return self.parse_variable_declaration()
        
        # output statement
        elif token_value == "VISIBLE":
            return self.parse_output_statement()
        
        # for now, skip other tokens we don't handle yet
        else:
            self.advance()
            return self.parse_statement()

    def parse_variable_block(self):
        # take note of block structures
        # WAZZUP -- BUHBYE
        print("Parsing variable block...")
        self.error_handle("Variable List Delimeter", "WAZZUP")
        
        declarations = []
        while self.current_token and self.current_token['pattern'] != "BUHBYE":
            if self.current_token['pattern'] == "I HAS A":
                decl = self.parse_variable_declaration()
                if decl:
                    declarations.append(decl)
            else:
                self.advance()
        
        self.error_handle("Variable List Delimeter", "BUHBYE")
        return {
            'type': 'variable_block',
            'declarations': declarations
        }

    def parse_variable_declaration(self):
        # identifiers
        self.error_handle("Variable Declaration", "I HAS A")
        
        identifier = self.error_handle("Variable Identifier")
        
        # Optional assignment with ITZ
        initial_value = None
        if self.current_token and self.current_token['pattern'] == "ITZ":
            self.advance()  # consume ITZ
            initial_value = self.parse_expression()
        
        return {
            'type': 'variable_declaration',
            'identifier': identifier['pattern'],
            'initial_value': initial_value
        }

    def parse_output_statement(self):
        # visible
        self.error_handle("Output Keyword", "VISIBLE")
        
        expressions = []
        while (self.current_token and 
               self.current_token['pattern'] not in ["KTHXBYE", "VISIBLE"] and
               not (self.current_token['token_name'] == "Comment")):
            expr = self.parse_expression()
            if expr:
                expressions.append(expr)
        
        return {
            'type': 'output_statement',
            'expressions': expressions
        }

    def parse_expression(self):
        # parse expressions with operator precedence
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current_token and self.current_token['pattern'] in ["ANY OF", "EITHER OF"]:
            operator = self.current_token['pattern']
            self.advance()
            right = self.parse_logical_and()
            left = {
                'type': 'logical_operation',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def parse_logical_and(self):
        left = self.parse_comparison()
        while self.current_token and self.current_token['pattern'] in ["BOTH OF", "EITHER OF", "WON OF", "ANY OF", "ALL OF"]:
            operator = self.current_token['pattern']
            self.advance()
            right = self.parse_comparison()
            left = {
                'type': 'logical_operation',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def parse_comparison(self):
        left = self.parse_arithmetic()
        while self.current_token and self.current_token['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT", ]:
            operator = self.current_token['pattern']
            self.advance()
            right = self.parse_arithmetic()
            left = {
                'type': 'comparison_operation',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def parse_arithmetic(self):
        left = self.parse_term()
        while self.current_token and self.current_token['pattern'] in ["SUM OF", "DIFF OF"]:
            operator = self.current_token['pattern']
            self.advance()
            right = self.parse_term()
            left = {
                'type': 'arithmetic_operation',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token and self.current_token['pattern'] in ["PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
            operator = self.current_token['pattern']
            self.advance()
            right = self.parse_factor()
            left = {
                'type': 'arithmetic_operation',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def parse_factor(self):
        # basic expressions: literals, identifiers, and arithmetic operations
        if not self.current_token:
            return None
        
        # hiwalay arithmetic and comparison operators
        # wala pang logical atmm
        # arithmetic operations at the factor level
        if self.current_token['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"]:
            return self.parse_arithmetic_operation()
        
        if self.current_token['pattern'] in ["BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT"]:
            return self.parse_comparison_operation()
        
        # boolean literals (WIN and FAIL)
        if self.current_token['token_name'] == "Boolean Literal":
            value = self.current_token
            self.advance()
            return {
                'type': 'literal',
                'value_type': 'Boolean Literal',
                'value': value['pattern']
            }
        
        # other literals
        elif self.current_token['token_name'] in ["String Literal", "Integer Literal", "Float Literal"]:
            value = self.current_token
            self.advance()
            return {
                'type': 'literal',
                'value_type': value['token_name'],
                'value': value['pattern']
            }
        
        # type literals
        elif self.current_token['token_name'] == "Type Literal":
            value = self.current_token
            self.advance()
            return {
                'type': 'type_literal',
                'value': value['pattern']
            }
        
        # identifiers
        elif self.current_token['token_name'] == "Variable Identifier":
            identifier = self.current_token
            self.advance()
            return {
                'type': 'identifier',
                'name': identifier['pattern']
            }
        
        # parentheses
        elif self.current_token['pattern'] == "(":
            self.advance()  # consume (
            expr = self.parse_expression()
            self.error_handle(")", ")")
            return expr
        
        # unary NOT
        elif self.current_token['pattern'] == "NOT":
            self.advance()
            operand = self.parse_factor()
            return {
                'type': 'unary_operation',
                'operator': 'NOT',
                'operand': operand
            }
        
        else:
            self.error(f"Unexpected token in expression: {self.current_token['pattern'] if self.current_token else 'EOF'}")

    def parse_arithmetic_operation(self):
        operator = self.current_token['pattern']
        self.advance()  # consume operator
        
        # Parse first operand
        operand1 = self.parse_expression()
        
        # Expect AN
        if self.current_token and self.current_token['pattern'] == "AN":
            self.advance()  # consume AN
        
        # Parse second operand
        operand2 = self.parse_expression()
        
        return {
            'type': 'arithmetic_operation',
            'operator': operator,
            'operand1': operand1,
            'operand2': operand2
        }
    
    def parse_comparison_operation(self):
        operator = self.current_token['pattern']
        self.advance()  # consume operator
        
        # Parse first operand
        operand1 = self.parse_expression()
        
        # Expect AN
        if self.current_token and self.current_token['pattern'] == "AN":
            self.advance()  # consume AN
        
        # Parse second operand
        operand2 = self.parse_expression()
        
        return {
            'type': 'comparison_operation',
            'operator': operator,
            'operand1': operand1,
            'operand2': operand2
        }

def parse(filename):
    # main function for parsing
    try:
        tokens = tokenizer(filename)
        print(f"Tokenization complete. Found {len(tokens)} tokens.")
        
        # Debug: print all tokens
        print("\nTokens found:")
        for i, token in enumerate(tokens):
            print(f"{i+1:3}: {token['token_name']:25} '{token['pattern']}'")
        
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        return ast
        
    except Exception as e:
        print(f"Parsing error: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_ast(node, indent=0):
    # print AST
    if not node:
        return
    
    prefix = "  " * indent
    
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
        return
    
    node_type = node.get('type')
    
    if node_type == 'program':
        print(f"{prefix}Program:")
        for stmt in node['statements']:
            print_ast(stmt, indent + 1)
    
    elif node_type == 'variable_block':
        print(f"{prefix}Variable Block:")
        for decl in node['declarations']:
            print_ast(decl, indent + 1)
    
    elif node_type == 'variable_declaration':
        if node['initial_value']:
            print(f"{prefix}Variable Declaration: {node['identifier']} =")
            print_ast(node['initial_value'], indent + 1)
        else:
            print(f"{prefix}Variable Declaration: {node['identifier']}")
    
    elif node_type == 'output_statement':
        print(f"{prefix}Output Statement:")
        for expr in node['expressions']:
            print_ast(expr, indent + 1)
    
    elif node_type == 'literal':
        print(f"{prefix}Literal ({node['value_type']}): {node['value']}")
    
    elif node_type == 'identifier':
        print(f"{prefix}Identifier: {node['name']}")
    
    elif node_type == 'type_literal':
        print(f"{prefix}Type Literal: {node['value']}")
    
    elif node_type == 'arithmetic_operation':
        print(f"{prefix}Arithmetic Operation: {node['operator']}")
        print_ast(node['operand1'], indent + 1)
        print_ast(node['operand2'], indent + 1)
    
    elif node_type == 'comparison_operation':
        print(f"{prefix}Comparison Operation: {node['operator']}")
        print_ast(node['operand1'], indent + 1)
        print_ast(node['operand2'], indent + 1)
    
    elif node_type == 'logical_operation':
        print(f"{prefix}Logical Operation: {node['operator']}")
        print_ast(node['left'], indent + 1)
        print_ast(node['right'], indent + 1)
    
    else:
        print(f"{prefix}Unknown node: {node}")

if __name__ == "__main__":
    filename = "t5.lol"
    
    print("=" * 60)
    print(f"PARSING: {filename}")
    print("=" * 60)
    
    ast = parse(filename)
    if ast:
        print("\nABSTRACT SYNTAX TREE:")
        print_ast(ast)
    else:
        print("Failed to parse the program.")