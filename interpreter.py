import sys
from io import StringIO

class Interpreter:
    def __init__(self):
        self.symbol_table = {} 
        self.output_buffer = []
        self.input_buffer = []
        self.input_index = 0
    
    # Reset the interpreter state
    def reset(self):
        self.symbol_table = {}
        self.output_buffer = []
        self.input_index = 0

    # Set input lines for GIMMEH statements 
    def set_input(self, input_lines):
        self.input_buffer = input_lines
        self.input_index = 0
    
    # Get the next input line
    def get_input(self):
        if self.input_index < len(self.input_buffer):
            value = self.input_buffer[self.input_index]
            self.input_index += 1
            return value
        return ""
    
    # Get all output as a string
    def get_output(self):
        return '\n'.join(self.output_buffer)
    
    # Interpretation method
    def interpret(self, ast):
        try:
            self.reset()
            return self.execute_program(ast)
        except Exception as e:
            self.output_buffer.append(f"Runtime Error: {str(e)}")
            return False
    
    # Execute the program node
    def execute_program(self, node):
        if node['type'] != 'program':
            raise ValueError("Expected program node")
        
        for statement in node['statements']:
            self.execute_statement(statement)
        
        return True
    
    # Execute a single statement
    def execute_statement(self, node):
        if not node:
            return

        stmt_type = node['type']

        if stmt_type == 'variable_block':
            self.execute_variable_block(node)
        elif stmt_type == 'variable_declaration':
            self.execute_variable_declaration(node)
        elif stmt_type == 'output_statement':
            self.execute_output_statement(node)
        elif stmt_type == 'input_statement':
            self.execute_input_statement(node)
        # Accept both parser-produced names: 'assignment' and 'variable_assignment'
        elif stmt_type in ('assignment', 'variable_assignment'):
            self.execute_assignment(node)
        else:
            pass
    
    # Execute variable block (WAZZUP...BUHBYE)
    def execute_variable_block(self, node):
        for declaration in node['declarations']:
            self.execute_variable_declaration(declaration)
    
    # Execute variable declaration
    def execute_variable_declaration(self, node):
        var_name = node['identifier']
        
        if node['initial_value']:
            value = self.evaluate_expression(node['initial_value'])
        else:
            value = None  
        
        self.symbol_table[var_name] = value
    
    # Execute variable assignment
    def execute_assignment(self, node):
        var_name = node['identifier']
        value = self.evaluate_expression(node['value'])
        self.symbol_table[var_name] = value
    
    # Execute VISIBLE statement
    def execute_output_statement(self, node):
        output_parts = []
        
        for expr in node['expressions']:
            value = self.evaluate_expression(expr)
            output_parts.append(self.value_to_string(value))
        
        output = ' '.join(output_parts)
        self.output_buffer.append(output)
        # Store the last printed output in the special variable IT so it
        # appears in the symbol table (matches expected sample behavior).
        self.symbol_table['IT'] = output
    
    # Execute GIMMEH statement
    def execute_input_statement(self, node):
        var_name = node['identifier']
        input_value = self.get_input()
        
        # Try to convert to appropriate type
        value = self.parse_input_value(input_value)
        self.symbol_table[var_name] = value
    
    # Parse input string to appropriate type
    def parse_input_value(self, input_str):
        input_str = input_str.strip()
        
        # Try boolean
        if input_str == "WIN":
            return True
        elif input_str == "FAIL":
            return False
        
        # Try integer
        try:
            return int(input_str)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(input_str)
        except ValueError:
            pass
        
        # Default to string
        return input_str
    
    # Evaluate an expression and return its value
    def evaluate_expression(self, node):
        if not node:
            return None
        
        expr_type = node['type']
        
        if expr_type == 'literal':
            return self.evaluate_literal(node)
        elif expr_type == 'identifier':
            return self.evaluate_identifier(node)
        elif expr_type == 'arithmetic_operation':
            return self.evaluate_arithmetic_operation(node)
        elif expr_type == 'comparison_operation':
            return self.evaluate_comparison_operation(node)
        elif expr_type == 'logical_operation':
            return self.evaluate_logical_operation(node)
        elif expr_type == 'unary_operation':
            return self.evaluate_unary_operation(node)
        elif expr_type == 'type_literal':
            return None  # Type literals evaluate to NOOB
        else:
            raise ValueError(f"Unknown expression type: {expr_type}")
    
    # Evaluate a literal value
    def evaluate_literal(self, node):
        value_type = node['value_type']
        value_str = node['value']
        
        if value_type == 'Integer Literal':
            return int(value_str)
        elif value_type == 'Float Literal':
            return float(value_str)
        elif value_type == 'String Literal':
            # Remove quotes if there are any
            if value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            return value_str
        elif value_type == 'Boolean Literal':
            return value_str == 'WIN'
        else:
            return value_str
    
    # Evaluate a variable identifier
    def evaluate_identifier(self, node):
        var_name = node['name']
        
        if var_name not in self.symbol_table:
            raise NameError(f"Variable '{var_name}' is not defined")
        
        return self.symbol_table[var_name]
    
    # Evaluate arithmetic operations
    def evaluate_arithmetic_operation(self, node):
        operator = node['operator']
        operand1 = self.evaluate_expression(node['operand1'])
        operand2 = self.evaluate_expression(node['operand2'])
        
        # Convert to numbers
        operand1 = self.to_number(operand1)
        operand2 = self.to_number(operand2)
        
        if operator == "SUM OF":
            result = operand1 + operand2
        elif operator == "DIFF OF":
            result = operand1 - operand2
        elif operator == "PRODUKT OF":
            result = operand1 * operand2
        elif operator == "QUOSHUNT OF":
            if operand2 == 0:
                raise ValueError("Division by zero")
            result = operand1 / operand2
        elif operator == "MOD OF":
            if operand2 == 0:
                raise ValueError("Modulo by zero")
            result = operand1 % operand2
        else:
            raise ValueError(f"Unknown arithmetic operator: {operator}")
        
        # Return int if both operands were ints and result is whole
        if isinstance(operand1, int) and isinstance(operand2, int) and operator != "QUOSHUNT OF":
            return int(result)
        return result
    
    # Evaluate comparison operations
    def evaluate_comparison_operation(self, node):
        operator = node['operator']
        operand1 = self.evaluate_expression(node['operand1'])
        operand2 = self.evaluate_expression(node['operand2'])
        
        if operator == "BOTH SAEM":
            return operand1 == operand2
        elif operator == "DIFFRINT":
            return operand1 != operand2
        elif operator == "BIGGR OF":
            # Returns bigger value
            operand1 = self.to_number(operand1)
            operand2 = self.to_number(operand2)
            return max(operand1, operand2)
        elif operator == "SMALLR OF":
            # Returns smaller value
            operand1 = self.to_number(operand1)
            operand2 = self.to_number(operand2)
            return min(operand1, operand2)
        else:
            raise ValueError(f"Unknown comparison operator: {operator}")
    
    # Evaluate logical operations
    def evaluate_logical_operation(self, node):       
        operator = node['operator']
        left = self.evaluate_expression(node['left'])
        right = self.evaluate_expression(node['right'])
        
        # Convert to boolean
        left_bool = self.to_boolean(left)
        right_bool = self.to_boolean(right)
        
        if operator == "BOTH OF":
            return left_bool and right_bool
        elif operator == "EITHER OF":
            return left_bool or right_bool
        elif operator == "WON OF":
            return left_bool != right_bool 
        elif operator == "ANY OF":
            return left_bool or right_bool
        elif operator == "ALL OF":
            return left_bool and right_bool
        else:
            raise ValueError(f"Unknown logical operator: {operator}")
    
    # Evaluate unary operations
    def evaluate_unary_operation(self, node):
        operator = node['operator']
        operand = self.evaluate_expression(node['operand'])
        
        if operator == "NOT":
            return not self.to_boolean(operand)
        else:
            raise ValueError(f"Unknown unary operator: {operator}")
    
    # Convert value to number
    def to_number(self, value):
        if value is None:
            return 0
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return 0
        return 0
    
    # Convert value to boolean    
    def to_boolean(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return False
    
    # Convert value to string for output
    def value_to_string(self, value):
        if value is None:
            return "NOOB"
        if isinstance(value, bool):
            return "WIN" if value else "FAIL"
        if isinstance(value, float):
            # Format float nicely
            if value.is_integer():
                return str(int(value))
            return str(value)
        return str(value)
    
    # Get symbol table as list of dicts for display
    def get_symbol_table_display(self):
        return [
            {
                'Variable': var_name,
                'Value': self.value_to_string(value),
                'Type': self.get_type_name(value)
            }
            for var_name, value in self.symbol_table.items()
        ]
    
    # Get LOLCODE type name for a value
    def get_type_name(self, value):
        if value is None:
            return "NOOB"
        if isinstance(value, bool):
            return "TROOF"
        if isinstance(value, int):
            return "NUMBR"
        if isinstance(value, float):
            return "NUMBAR"
        if isinstance(value, str):
            return "YARN"
        return "NOOB"
