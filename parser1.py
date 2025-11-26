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
        self.error_handle("Code Delimiter", "HAI")
        
        # sa bawat statement
        # dito mapupunta ung breakdown ng keywords
        # tapos iaarrange into a tree for easier analysis
        statements = []
        while self.current_token and self.peek() and self.peek()['pattern'] != "KTHXBYE":
            if self.current_token['pattern'] == "WAZZUP":
                statements.append(self.parse_variable_block())
            else:
                statement = self.parse_statement()
                if statement:
                    statements.append(statement)
                else:
                    if self.current_token and self.current_token['pattern'] != "KTHXBYE":
                        self.error(f"Unexpected token: {self.current_token['pattern']}")
                    break
        
        # KTHXBYE eof
        self.error_handle("Code Delimiter", "KTHXBYE")
        
        return {
            'type': 'program',
            'statements': statements
        }

    def parse_statement(self):
        """<statement> ::= <print> | <input> | <declare_var> | <assign_var> | <typecast> 
        | <conditional> | <loop> | <function> | <function_call> | <return> | <break> 
        | <single_comment> | <multi_comment>"""
        if not self.current_token:
            return None
            
        token_value = self.current_token['pattern']
        
        # variable declaration
        if token_value == "I HAS A":
            return self.parse_variable_declaration()
        
        # output statement
        elif token_value == "VISIBLE":
            return self.parse_output_statement()
         
        # Input statement -added
        elif token_value == "GIMMEH":
            return self.parse_input_statement()

        # Loop statement - added
        elif token_value == "IM IN YR":
            return self.parse_loop_statement()
        
        # Variable assignment: <identifier> R <expression>
        elif (self.current_token['token_name'] == "Variable Identifier" and
            self.peek() and self.peek()['pattern'] == "R"):
            return self.parse_variable_assignment()

        # Variable typecasting: varident IS NOW A literal
        elif (self.current_token['token_name'] == "Variable Identifier"
            and self.peek()
            and self.peek()['pattern'] == "IS NOW A"):
            return self.parse_typecast_isnow()
        
         # conditional statements O RLY?
        elif (self.current_token['token_name'] in ["Variable Identifier", "String Literal", "Integer Literal", "Float Literal", "Boolean Literal"] or
            self.current_token['pattern'] in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT",
            "SMOOSH", "MAEK", "NOT"]):
            
            # check if conditional when theres O RLY?
            if self.peek() and self.peek()['pattern'] == "O RLY?":
                return self.parse_conditional_statement()
            else:
                self.advance()
                return self.parse_statement()

        # For now, skip other tokens we don't handle yet
        else:
            self.advance()
            return self.parse_statement()

    def parse_variable_block(self):
        # take note of block structures
        # WAZZUP -- BUHBYE
        print("Parsing variable block...")
        self.error_handle("Variable List Delimiter", "WAZZUP")
        
        declarations = []
        while self.current_token and self.current_token['pattern'] != "BUHBYE":
            if self.current_token['pattern'] == "I HAS A":
                decl = self.parse_variable_declaration()
                if decl:
                    declarations.append(decl)
            else:
                self.advance()
        
        self.error_handle("Variable List Delimiter", "BUHBYE")
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
               self.current_token['pattern'] not in ["KTHXBYE", "VISIBLE", "GIMMEH", "I HAS A", "O RLY?", 
               "MEBBE", "NO WAI", "OIC", "IM OUTTA YR", "IM IN YR", "AN"] and
               not (self.current_token['token_name'] == "Comment")):
            expr = self.parse_expression()
            if expr:
                expressions.append(expr)
            else:
                break
        
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
        
        # Handle Concatenation (added)
        elif self.current_token['pattern'] == "SMOOSH":
            return self.parse_smoosh()

        # Handle type literals
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
        
        # Handle type casting (added)
        elif self.current_token['pattern'] == "MAEK":
            return self.parse_typecast_maek()

        elif self.current_token['pattern'] in ["R", "IS NOW A", "VISIBLE", "GIMMEH", "I HAS A", 
                                          "O RLY?", "MEBBE", "NO WAI", "OIC", "IM IN YR", 
                                          "IM OUTTA YR", "KTHXBYE", "BUHBYE", "AN"]:
            return None

        else:
            self.error(f"Unexpected token: {self.current_token['pattern']}")

    def parse_arithmetic_operation(self):
        operator = self.current_token['pattern']
        self.advance()  # consume operator
        
        # Parse first operand
        operand1 = self.parse_expression()
        if operand1 is None:
            self.error(f"Expected expression after {operator}")
        
        # Expect AN
        if self.current_token and self.current_token['pattern'] == "AN":
            self.advance()  # consume AN
        
        # Parse second operand
        operand2 = self.parse_expression()
        if operand2 is None:  
            self.error(f"Expected expression after AN in {operator}")
        
        return {
            'type': 'arithmetic_operation',
            'operator': operator,
            'left': operand1,
            'right': operand2
        }
    
    def parse_comparison_operation(self):
        operator = self.current_token['pattern']
        self.advance()  # consume operator
        
        # Parse first operand
        operand1 = self.parse_expression()
        if operand1 is None:  
            self.error(f"Expected expression after {operator}")
        
        # Expect AN
        if self.current_token and self.current_token['pattern'] == "AN":
            self.advance()  # consume AN
        
        # Parse second operand
        operand2 = self.parse_expression()
        if operand2 is None: 
            self.error(f"Expected expression after AN in {operator}")

        
        return {
            'type': 'comparison_operation',
            'operator': operator,
            'left': operand1,
            'right': operand2
        }
    
    def parse_conditional_statement(self):
        """<conditional> ::= <expr> <linebreak> O RLY? <linebreak> <if> <linebreak> OIC"""        
        # Parse expressio
        condition = self.parse_expression()
        
        # Expect O RLY?
        self.error_handle("If Keyword", "O RLY?")
        
        # Parse if block
        if_block = self.parse_if_block()
        
        # Expect OIC
        self.error_handle("If-Then-Else End", "OIC")
        
        return {
            'type': 'conditional_statement',
            'condition': condition,
            'if_block': if_block
        }

    def parse_if_block(self):
        """
        <if> ::=
            YA RLY <linebreak> <statement_block>
        | YA RLY <linebreak> <statement_block> <linebreak> <else_if>
        | YA RLY <linebreak> <statement_block> <linebreak> <else>
        """
        self.error_handle("Then Keyword", "YA RLY")
        
        # Parse YA RLY
        then_block = self.parse_statement_block()
        
        # Check for other statements
        elseif_block = []
        else_block = None
        
        if self.current_token and self.current_token['pattern'] == "MEBBE":
            elseif_block = self.parse_elseif_block()
        elif self.current_token and self.current_token['pattern'] == "NO WAI":
            else_block = self.parse_else()
        
        return {
            'type': 'if_block',
            'then_block': then_block,
            'elseif_block': elseif_block,
            'else_block': else_block
        }

    def parse_elseif_block(self):
        """
        <else_if> ::=
            MEBBE <expr> <linebreak> <statement_block>
        | MEBBE <expr> <linebreak> <statement_block> <linebreak> <else_if>
        | <else>
        """
        elseif_block = []
        
        while self.current_token and self.current_token['pattern'] == "MEBBE":
            self.advance()  # consume MEBBE
            
            # Parse condition
            condition = self.parse_expression()
            
            # Parse statement block
            statements = self.parse_statement_block()
            
            elseif_block.append({
                'type': 'elseif_block',
                'condition': condition,
                'statements': statements
            })
        
        # Check for other chains of statments
        else_block = None
        if self.current_token and self.current_token['pattern'] == "NO WAI":
            else_block = self.parse_else()
        
        return elseif_block

    def parse_else(self):
        """<else> ::= NO WAI <linebreak> <statement_block>"""
        self.error_handle("Else Keyword", "NO WAI")
        
        statements = self.parse_statement_block()
        
        return {
            'type': 'else_block',
            'statements': statements
        }

    def parse_statement_block(self):
        """
        <statement_block> ::=
            <statement> 
        | <statement> <linebreak> <statement_block>
        """
        statements = []
        start_index = self.token_index
        
        while self.current_token and self.current_token['pattern'] != "KTHXBYE":
            # Check end keywords
            if self.current_token['pattern'] in ["MEBBE", "NO WAI", "OIC", "IM OUTTA YR"]:
                break
                
            # Parse statement
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            else:
                self.advance()
        
        return statements
    
    def parse_input_statement(self):
        """GIMMEH identifier"""
        self.error_handle("Input Keyword", "GIMMEH")
        
        identifier = self.error_handle("Variable Identifier")
        
        return {
            'type': 'input_statement',
            'identifier': identifier['pattern']
        }
    
    def parse_loop_statement(self):
        """<loop> ::= IM IN YR loopident <loop_condition> <linebreak> <statement_block> IM OUTTA YR loopident
                    | IM IN YR loopident <linebreak> <statement_block> IM OUTTA YR loopident"""        
        # Expect IM IN YR
        self.error_handle("Start Loop Label", "IM IN YR")
        
        # Parse loop identifier
        start_loop_ident = self.error_handle("Variable Identifier")
        
        # Check for loop condition
        loop_condition = None
        if self.current_token and self.current_token['pattern'] in ["UPPIN YR", "NERFIN YR"]:
            loop_condition = self.parse_loop_condition()
        
        # Parse statement block
        statements = self.parse_statement_block()
        
        # Expect IM OUTTA YR
        self.error_handle("End Loop Label", "IM OUTTA YR")
        
        # Parse loop identifier (IM IN YR loop and IM OUTTA YR loop)
        end_loop_ident = self.error_handle("Variable Identifier")
        
        return {
            'type': 'loop_statement',
            'loop_identifier': start_loop_ident['pattern'],
            'loop_condition': loop_condition,
            'statements': statements
        }

    def parse_loop_condition(self):
        """<loop_condition> ::= UPPIN YR varident TIL <expr>
                            | UPPIN YR varident WILE <expr>
                            | NERFIN YR varident TIL <expr>
                            | NERFIN YR varident WILE <expr>"""
        # Parse loop operation
        loop_operation = self.current_token
        self.advance()  # consume UPPIN/NERFIN
        
        # Parse variable identifier
        var_ident = self.error_handle("Variable Identifier")
        
        # Parse loop condition (TIL/WILE)
        if self.current_token and (self.current_token['pattern'] == "TIL" or 
        self.current_token['pattern'] == "WILE"):
            loop_condition = self.current_token['pattern']
            self.advance()  # consume TI/WILE
        
        # Parse condition
        condition = self.parse_expression()
        
        return {
            'type': 'loop_condition',
            'loop_operation': loop_operation['pattern'],  # UPPIN/NERFIN YR
            'variable': var_ident['pattern'],
            'loop_condition': loop_condition,  # TIL/WILE
            'condition': condition
        }
    

    def parse_variable_assignment(self):
        """identifier R expression"""

        identifier = self.current_token['pattern']
        self.advance()  # consume identifier

        self.error_handle("Variable Assignment")  # consume R

        value = self.parse_expression()

        return {
            'type': 'variable_assignment',
            'identifier': identifier,
            'value': value
        }
    
    def parse_smoosh(self):
        """SMOOSH expression (AN expression)*"""
        self.advance()  # consume SMOOSH
        parts = []

        # Parse first expression
        parts.append(self.parse_expression())

        # if theres more than one AN then parse those
        while self.current_token and self.current_token['pattern'] == "AN":
            self.advance()  # consume AN
            parts.append(self.parse_expression())

        return {
            'type': 'smoosh',
            'parts': parts
        }

    def parse_typecast_isnow(self):
        """varident IS NOW A <literal>"""
        varident = self.current_token['pattern']
        self.advance()  # consume identifier

        self.error_handle("Recast Variable", "IS NOW A")  # consumes IS NOW A

        # Handle Type Literal
        if self.current_token['pattern'] in ["NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF"]:
            type_literal = self.current_token
            self.advance() 
        else:
            self.error("Expected type literal after IS NOW A")

        return {
            'type': 'typecast_isnow',
            'identifier': varident,
            'convert_to_type': type_literal['pattern']
        }

    def parse_typecast_maek(self):
        """MAEK <expr> A <literal>"""
        self.advance()  # consume MAEK

        expr = self.parse_expression()

        # Expect A
        self.error_handle("Explicit Casting", "A")

        # Handle Type Literal
        if self.current_token['pattern'] in ["NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF"]:
            type_literal = self.current_token
            self.advance()
        else:
            self.error("Expected type literal after A")

        return {
            'type': 'typecast_maek',
            'expression': expr,
            'convert_to_type': type_literal['pattern']
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
        print_ast(node['left'], indent + 1)
        print_ast(node['right'], indent + 1)
    
    elif node_type == 'comparison_operation':
        print(f"{prefix}Comparison Operation: {node['operator']}")
        print_ast(node['left'], indent + 1)
        print_ast(node['right'], indent + 1)
    
    elif node_type == 'logical_operation':
        print(f"{prefix}Logical Operation: {node['operator']}")
        print_ast(node['left'], indent + 1)
        print_ast(node['right'], indent + 1)

    elif node_type == 'conditional_statement':
        print(f"{prefix}Conditional Statement:")
        print(f"{prefix}  Expression/Condition:")
        print_ast(node['condition'], indent + 2)
        print_ast(node['if_block'], indent + 1)
    
    elif node_type == 'if_block':
        print(f"{prefix}If Structure:")
        print(f"{prefix}  Then Block (YA RLY):")
        for stmt in node['then_block']:
            print_ast(stmt, indent + 3)
        
        for else_if in node['elseif_block']:
            print(f"{prefix}  Else-If Block (MEBBE):")
            print(f"{prefix}    Condition:")
            print_ast(else_if['condition'], indent + 4)
            for stmt in else_if['statements']:
                print_ast(stmt, indent + 4)
        
        if node['else_block']:
            print(f"{prefix}  Else Block (NO WAI):")
            for stmt in node['else_block']['statements']:
                print_ast(stmt, indent + 3)
    
    elif node_type == 'input_statement':
        print(f"{prefix}Input Statement: {node['identifier']}")

    elif node_type == 'loop_statement':
        print(f"{prefix}Loop Statement:")
        print(f"{prefix}  Identifier: {node['loop_identifier']}")
        if node['loop_condition']:
            print_ast(node['loop_condition'], indent + 1)
        print(f"{prefix}  Statements:")
        for stmt in node['statements']:
            print_ast(stmt, indent + 2)

    elif node_type == 'loop_condition':
        print(f"{prefix}Loop Condition:")
        print(f"{prefix}  Loop Operation: {node['loop_operation']}")
        print(f"{prefix}  Variable: {node['variable']}")
        print(f"{prefix}  Loop Condition: {node['loop_condition']}")
        print(f"{prefix}  Condition:")
        print_ast(node['condition'], indent + 2)

    #added
    elif node_type == 'variable_assignment':
        print(f"{prefix}Assignment (=):")
        print(f"{prefix}  Variable: {node['identifier']}")
        print(f"{prefix}  Value:")
        print_ast(node['value'], indent + 2)
    
    elif node_type == 'smoosh':
        print(f"{prefix}String Concatenation (SMOOSH):")
        for part in node['parts']:
            print_ast(part, indent + 1)

    elif node_type == 'typecast_isnow':
        print(f"{prefix}Typecast (IS NOW A):")
        print(f"{prefix}  Variable: {node['identifier']}")
        print(f"{prefix}  Convert To: {node['convert_to_type']}")  

    elif node_type == 'typecast_maek':
        print(f"{prefix}Type Cast (MAEK):")
        print(f"{prefix}  Expression:")
        print_ast(node['expression'], indent + 2)
        print(f"{prefix}  Convert To: {node['convert_to_type']}")

    else:
        print(f"{prefix}Unknown node: {node}")

if __name__ == "__main__":
    filename = "smoosh_assign.lol"
    
    print("=" * 60)
    print(f"PARSING: {filename}")
    print("=" * 60)
    
    ast = parse(filename)
    if ast:
        print("\nABSTRACT SYNTAX TREE:")
        print_ast(ast)
    else:
        print("Failed to parse the program.")