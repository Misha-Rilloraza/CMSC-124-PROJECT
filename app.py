import streamlit as st
import os
import glob
from lexer import tokenizer
from parser import parse
import pandas as pd

# PAGE CONFIGURATION ======================================================

# Set up Streamlit page with wide layout
st.set_page_config(
    page_title="LOLCODE Interpreter",
    layout="wide",  # Use full width of browser
    initial_sidebar_state="expanded"
)

# CSS ===========================================================================

st.markdown("""
    <style>
    .stApp {
        background-color: #F5F9FF;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: #66C7BD;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    /* Section headers (Text Editor, Lexemes, etc.) */
    .section-header {
        font-size: 1.2rem;
        color: #2C5F8D;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #66C7BD;
        padding-bottom: 0.3rem;
    }
    
    /* Text editor - monospace font  */
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 14px;
        border-color: #66C7BD !important;
        background-color: white !important;
        color: #2C5F8D !important;
    }
    
    .console-output {
        background-color: #E8F4F8;
        color: #2C5F8D;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        min-height: 150px;
        white-space: pre-wrap;
        border: 2px solid #A5CCFA;
    }
    
    .stButton>button {
        background-color: #E9C4E3;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #5089D0;
        color: white;
    }
    
    .stDataFrame {
        background-color: #FAFCFE;
        border-radius: 10px;
    }
    div[data-testid="stDataFrame"] {
        background-color: #FAFCFE;
    }
    
    /* Dark blue for all text */
    .stMarkdown, .stSelectbox label, .stInfo, .stWarning, .stSuccess, p {
        color: #2C5F8D !important;
    }
    
    .compact-selector label {
        font-size: 0.85rem;
        color: #2C5F8D;
    }
    </style>
""", unsafe_allow_html=True)


# SESSION STATE INITIALIZATION ==================================================

# Stores current code in text editor
if 'code_content' not in st.session_state:
    st.session_state.code_content = ""

# Stores list of tokens from lexical analysis
if 'tokens' not in st.session_state:
    st.session_state.tokens = []

# Stores the symbol table
if 'symbol_table' not in st.session_state:
    st.session_state.symbol_table = []

# Stores output from program execution
if 'console_output' not in st.session_state:
    st.session_state.console_output = ""

# Stores currently selected .lol file path
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False

# Stores program input (for GIMMEH) as raw text (one input per line)
if 'program_input' not in st.session_state:
    st.session_state.program_input = ""

# Interactive GIMMEH session state
if 'awaiting_input' not in st.session_state:
    st.session_state.awaiting_input = False
if 'awaiting_var' not in st.session_state:
    st.session_state.awaiting_var = None
if 'awaiting_parse_index' not in st.session_state:
    st.session_state.awaiting_parse_index = None
if 'awaiting_parse_tree' not in st.session_state:
    st.session_state.awaiting_parse_tree = None
if 'awaiting_symbol_table' not in st.session_state:
    st.session_state.awaiting_symbol_table = None
if '_gimmeh_buffer' not in st.session_state:
    st.session_state._gimmeh_buffer = []
if 'awaiting_output_lines' not in st.session_state:
    st.session_state.awaiting_output_lines = []
if 'awaiting_semantic_errors' not in st.session_state:
    st.session_state.awaiting_semantic_errors = []

# Initialize code editor content in session state
if 'code_editor' not in st.session_state:
    st.session_state.code_editor = st.session_state.get('code_content', '')

# HELPER FUNCTIONS =========================================================

# Loads file content into the text editor and sync widget state
def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        st.session_state.selected_file = filepath
        st.session_state.code_content = content
        st.session_state["code_editor"] = content
        st.session_state.file_loaded = True 
        return True
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return False
    
# Save code content to a temporary file for processing
def save_temp_file(content):
    temp_file = "temp_code.lol"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return temp_file
    except Exception as e:
        st.error(f"Error saving temporary file: {str(e)}")
        return None

def extract_expression_value(expr, symbol_table, errors=None, line_no=None):
    """Extract the value from an expression, evaluating if needed."""
    if errors is None:
        errors = []
    
    if not expr:
        return None
    
    if isinstance(expr, dict):
        node_type = expr.get('node')
        
        # String literal
        if node_type == 'string_literal':
            value = expr.get('value', '')
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value
        
        # Integer or float literal
        elif node_type in ('integer_literal', 'float_literal'):
            val = expr.get('value')
            # Convert to proper type
            if node_type == 'integer_literal':
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return 0
            else:  # float_literal
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0
        
        # Variable identifier - look up in symbol table
        elif node_type == 'identifier':
            var_name = expr.get('value')
            if var_name not in symbol_table:
                error_msg = f"Line {line_no}: Semantic error: variable '{var_name}' used before declaration"
                errors.append(error_msg)
                return None
            return symbol_table.get(var_name)
        
        # Variable identifier (alternative format)
        elif node_type == 'variable_identifier':
            var_name = expr.get('name')
            if var_name not in symbol_table:
                error_msg = f"Line {line_no}: Semantic error: variable '{var_name}' used before declaration"
                errors.append(error_msg)
                return None
            return symbol_table.get(var_name)
        
        # SMOOSH expression (string concatenation)
        elif node_type == 'smoosh_expression':
            operands = expr.get('operands', [])
            result_parts = []
            for operand in operands:
                value = extract_expression_value(operand, symbol_table, errors, line_no)
                if value is not None:
                    result_parts.append(str(value))
            return ''.join(result_parts)
        
        # Arithmetic expression
        elif node_type == 'arithmetic_expression':
            return evaluate_arithmetic_expr(expr, symbol_table, errors, line_no)
        
        # Comparison expression
        elif node_type == 'comparison_expression':
            return evaluate_comparison_expr(expr, symbol_table, errors, line_no)
        
        # Logical expression
        elif node_type == 'logical_expression':
            return evaluate_logical_expr(expr, symbol_table, errors, line_no)
        
        # Literal (generic)
        elif node_type == 'literal':
            value = expr.get('value', '')
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value
        
        # Boolean literal
        elif node_type == 'boolean_literal':
            return expr.get('value') == 'WIN'
    
    return str(expr)

def to_number(value):
    """Convert value to number for arithmetic operations."""
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

def evaluate_arithmetic_expr(expr, symbol_table, errors=None, line_no=None):
    """Evaluate arithmetic expressions like SUM OF, DIFF OF, etc."""
    if errors is None:
        errors = []
    
    operator = expr.get('operator')
    operand1 = extract_expression_value(expr.get('operand1'), symbol_table, errors, line_no)
    operand2 = extract_expression_value(expr.get('operand2'), symbol_table, errors, line_no)
    
    num1 = to_number(operand1)
    num2 = to_number(operand2)
    
    if operator == 'SUM OF':
        return num1 + num2
    elif operator == 'DIFF OF':
        return num1 - num2
    elif operator == 'PRODUKT OF':
        return num1 * num2
    elif operator == 'QUOSHUNT OF':
        if num2 == 0:
            errors.append(f"Line {line_no}: Semantic error: division by zero")
            return 0
        return int(num1 // num2)
    elif operator == 'MOD OF':
        if num2 == 0:
            errors.append(f"Line {line_no}: Semantic error: modulo by zero")
            return 0
        return num1 % num2
    
    return 0

def evaluate_comparison_expr(expr, symbol_table, errors=None, line_no=None):
    """Evaluate comparison expressions like BIGGR OF, SMALLR OF, etc."""
    if errors is None:
        errors = []
    
    operator = expr.get('operator')
    operand1 = extract_expression_value(expr.get('operand1'), symbol_table, errors, line_no)
    operand2 = extract_expression_value(expr.get('operand2'), symbol_table, errors, line_no)
    
    if operator == 'BOTH SAEM':
        # Try numeric comparison if both can be converted to numbers
        try:
            num1 = to_number(operand1)
            num2 = to_number(operand2)
            # If both are numeric strings or numbers, compare as numbers
            if (isinstance(operand1, (int, float)) or (isinstance(operand1, str) and operand1.replace('.', '', 1).replace('-', '', 1).isdigit())) and \
               (isinstance(operand2, (int, float)) or (isinstance(operand2, str) and operand2.replace('.', '', 1).replace('-', '', 1).isdigit())):
                return num1 == num2
        except:
            pass
        # Otherwise compare as-is
        return operand1 == operand2
    elif operator == 'DIFFRINT':
        # Try numeric comparison if both can be converted to numbers
        try:
            num1 = to_number(operand1)
            num2 = to_number(operand2)
            # If both are numeric strings or numbers, compare as numbers
            if (isinstance(operand1, (int, float)) or (isinstance(operand1, str) and operand1.replace('.', '', 1).replace('-', '', 1).isdigit())) and \
               (isinstance(operand2, (int, float)) or (isinstance(operand2, str) and operand2.replace('.', '', 1).replace('-', '', 1).isdigit())):
                return num1 != num2
        except:
            pass
        # Otherwise compare as-is
        return operand1 != operand2
    elif operator == 'BIGGR OF':
        num1 = to_number(operand1)
        num2 = to_number(operand2)
        return max(num1, num2)
    elif operator == 'SMALLR OF':
        num1 = to_number(operand1)
        num2 = to_number(operand2)
        return min(num1, num2)
    
    return False

def evaluate_logical_expr(expr, symbol_table, errors=None, line_no=None):
    """Evaluate logical expressions like BOTH OF, EITHER OF, etc."""
    if errors is None:
        errors = []
    
    operator = expr.get('operator')
    left = extract_expression_value(expr.get('left'), symbol_table, errors, line_no)
    right = extract_expression_value(expr.get('right'), symbol_table, errors, line_no)
    
    left_bool = to_boolean(left)
    right_bool = to_boolean(right)
    
    if operator == 'BOTH OF':
        return left_bool and right_bool
    elif operator == 'EITHER OF':
        return left_bool or right_bool
    elif operator == 'WON OF':
        return left_bool != right_bool
    
    return False

def to_boolean(value):
    """Convert value to boolean."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    return False

def format_value_for_display(value):
    """Format a value for display in the symbol table."""
    if value is None:
        return 'NOOB'
    if isinstance(value, bool):
        return 'WIN' if value else 'FAIL'
    if isinstance(value, float):
        # Format float nicely
        if value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        return value
    return str(value)

def get_lolcode_type(value):
    """Get the LOLCODE type name for a value."""
    if value is None:
        return 'NOOB'
    if isinstance(value, bool):
        return 'TROOF'
    if isinstance(value, int):
        return 'NUMBR'
    if isinstance(value, float):
        return 'NUMBAR'
    if isinstance(value, str):
        return 'YARN'
    return 'NOOB'

def execute_code(code_content, user_input=""):
    try:
        # Save code to temporary file for processing
        temp_file = save_temp_file(code_content)
        if not temp_file:
            return

        # Clear previous output
        st.session_state.console_output = ""
        semantic_errors = []

        # Tokenization
        tokens = tokenizer(temp_file)
        st.session_state.tokens = tokens

        # Parsing (line-by-line)
        from parse import parse_whole
        parse_tree, errors = parse_whole(temp_file)

        # Build symbol table and collect output from parse tree
        symbol_table = {}
        output_lines = []

        # Helper to process remaining parse tree from a start index
        def process_remaining_parse_tree(parse_tree_obj, sym_table, out_lines, sem_errors, start_index=0):
            for idx in range(start_index, len(parse_tree_obj)):
                entry = parse_tree_obj[idx]
                result = entry.get('parse_result') or entry.get('ast')
                line_no = entry.get('line_number', '?')
                if not result:
                    continue

                # Handle GIMMEH (input statement)
                if result.get('node') == 'input_statement':
                    var_name = result.get('identifier')
                    # If buffer has pre-supplied inputs, consume first
                    if st.session_state._gimmeh_buffer:
                        value = st.session_state._gimmeh_buffer.pop(0)
                        sym_table[var_name] = value
                        continue
                    # Pause execution and save state to wait for user input
                    st.session_state.awaiting_input = True
                    st.session_state.awaiting_var = var_name
                    st.session_state.awaiting_parse_index = idx + 1
                    st.session_state.awaiting_parse_tree = parse_tree_obj
                    st.session_state.awaiting_symbol_table = sym_table
                    st.session_state.awaiting_output_lines = out_lines
                    st.session_state.awaiting_semantic_errors = sem_errors
                    st.session_state.console_output = f"Input required for variable '{var_name}'. Enter value below and press Submit."
                    return sym_table, out_lines, sem_errors

                # Variable declaration
                if result.get('node') == 'variable_declaration':
                    name = result.get('identifier')
                    assign = result.get('assignment')
                    value = None
                    if assign:
                        value = extract_expression_value(assign, sym_table, sem_errors, line_no)
                    sym_table[name] = value
                # Variable assignment
                elif result.get('node') == 'variable_assignment':
                    name = result.get('identifier')
                    expr = result.get('expression')
                    value = extract_expression_value(expr, sym_table, sem_errors, line_no)
                    sym_table[name] = value
                # Output statement
                elif result.get('node') == 'output_statement':
                    exprs = result.get('expressions', [])
                    visible_output_parts = []
                    for expr in exprs:
                        val = extract_expression_value(expr, sym_table, sem_errors, line_no)
                        out_lines.append(format_value_for_display(val))
                        visible_output_parts.append(format_value_for_display(val))
                    # The IT variable is implicitly set to the concatenated output of VISIBLE
                    if visible_output_parts:
                        sym_table['IT'] = ' '.join(visible_output_parts)
            return sym_table, out_lines, sem_errors

        # Start processing from the top (this may pause on first GIMMEH)
        symbol_table, output_lines, semantic_errors = process_remaining_parse_tree(parse_tree, symbol_table, output_lines, semantic_errors, 0)

        # If execution paused waiting for interactive input, don't overwrite the console prompt
        if st.session_state.awaiting_input:
            st.session_state.awaiting_symbol_table = symbol_table
            st.session_state.awaiting_output_lines = output_lines
            st.session_state.awaiting_semantic_errors = semantic_errors
            # Update symbol table display from the snapshot
            st.session_state.symbol_table = [
                {
                    'Variable': k,
                    'Value': format_value_for_display(v),
                    'Type': get_lolcode_type(v)
                }
                for k, v in (st.session_state.awaiting_symbol_table or {}).items()
            ]
            return

        # Update session state
        st.session_state.symbol_table = [
            {
                'Variable': k, 
                'Value': format_value_for_display(v),
                'Type': get_lolcode_type(v)
            } 
            for k, v in symbol_table.items()
        ]
        
        # Build console output: errors first, then program output
        console_parts = []
        if semantic_errors:
            console_parts.append("=== SEMANTIC ERRORS ===")
            console_parts.extend(semantic_errors)
            console_parts.append("")
        
        if output_lines:
            console_parts.extend(output_lines)
        
        st.session_state.console_output = '\n'.join(console_parts) if console_parts else 'No output.'

        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

    except Exception as e:
        st.session_state.console_output = f"Error: {str(e)}\n"
        import traceback
        st.session_state.console_output += traceback.format_exc()


# MAIN UI LAYOUT ============================================================

# Display main header 
st.markdown('<h1 class="main-header">LOLCODE Interpreter</h1>', unsafe_allow_html=True)


# FILE SELECTOR AND LOAD BUTTON ----------------------------------------------
file_col1, file_col2, file_col3 = st.columns([2, 0.3, 2.7])

with file_col1:
    # Get list of all .lol files in current directory
    lol_files = glob.glob("*.lol")
    
    if lol_files:
        selected_file = st.selectbox(
            "Select a LOLCODE file:",  # Label above the dropdown
            lol_files,  # List of options to show
            index=lol_files.index(st.session_state.selected_file) if st.session_state.selected_file in lol_files else 0,
            key="file_selector",  # Unique identifier
            label_visibility="visible"  # Show label
        )
    else:
        st.warning("No .lol files found")
        selected_file = None

with file_col2:
    st.write("")
    st.write("")
    if st.button("📂", use_container_width=True, help="Load File"):
        if selected_file and load_file(selected_file):
            st.success("Loaded!")
            st.rerun()  # Refresh page to show loaded content

with file_col3:
    pass


# TEXT EDITOR, LEXEMES, SYMBOL TABLE ----------------------------------------
editor_col, tables_col = st.columns([2, 3])

with editor_col:
    # TEXT EDITOR SECTION
    st.markdown('<div class="section-header">Text Editor</div>', unsafe_allow_html=True)
    
    # Create text area for code editing
    code_content = st.text_area(
        "Edit your LOLCODE here:",
        height=450,
        key="code_editor",
        placeholder="Load a file or paste your LOLCODE here...",
        label_visibility="collapsed"
    )

    # Update session state with current code content
    st.session_state.code_content = code_content

with tables_col:
    right_col1, right_col2 = st.columns(2)
    
    with right_col1:
        # LEXEMES TABLE SECTION
        st.markdown('<div class="section-header">Lexemes</div>', unsafe_allow_html=True)
        
        # Check if tokens exist in session state
        if st.session_state.tokens:
            # Convert tokens to DataFrame for display
            tokens_df = pd.DataFrame(st.session_state.tokens)
            tokens_display = tokens_df[['pattern', 'token_name']].copy()
            tokens_display.columns = ['Lexeme', 'Classification']
            
            # Display the dataframe as an interactive table
            st.dataframe(
                tokens_display,
                use_container_width=True,  
                height=450,  
                hide_index=True 
            )
        else:
            # Show info message when no tokens are available
            st.info("No tokens yet")
    
    with right_col2:
        # SYMBOL TABLE SECTION
        st.markdown('<div class="section-header">Symbol Table</div>', unsafe_allow_html=True)
        
        # Check if symbol table exists in session state
        if st.session_state.symbol_table:
            # Convert symbol table to DataFrame
            symbol_df = pd.DataFrame(st.session_state.symbol_table)
            symbol_display = symbol_df[['Variable', 'Value', 'Type']].copy()
            symbol_display.columns = ['Identifier', 'Value', 'Type']
            
            # Display the symbol table
            st.dataframe(
                symbol_display,
                use_container_width=True,
                height=450,  
                hide_index=True
            )
        else:
            # Show info message when no variables exist
            st.info("No variables yet")


# EXECUTE BUTTON -------------------------------------------------------------
if st.button("Execute Code", type="primary", use_container_width=True):
    # Check if there is code to execute
    if st.session_state.code_content.strip():
        # Show spinner animation while executing
        with st.spinner("Executing..."):
            execute_code(st.session_state.code_content, "")
        # Rerun to update the display output
        st.rerun()
    else:
        # Show warning if no code is present
        st.warning("Please load or enter code first!!!")

# OUTPUT CONSOLE ---------------------------------------------------------------
st.markdown('<div class="section-header">Output</div>', unsafe_allow_html=True)

# Display output
if st.session_state.awaiting_input:
    # Show current output and prompt for input inline
    out_lines = st.session_state.awaiting_output_lines or []
    sem_errs = st.session_state.awaiting_semantic_errors or []
    
    console_parts = []
    if sem_errs:
        console_parts.append('=== SEMANTIC ERRORS ===')
        console_parts.extend(sem_errs)
        console_parts.append('')
    if out_lines:
        console_parts.extend(out_lines)
    
    # Add the input prompt inline
    console_parts.append(f"> Waiting for input for '{st.session_state.awaiting_var}'")
    
    # Display console with prompt
    st.markdown(
        f'<div class="console-output">{chr(10).join(console_parts)}</div>',
        unsafe_allow_html=True
    )
    
    # Input field for GIMMEH
    # Use awaiting_var as part of key to force new input field for each GIMMEH
    input_key = f'gimmeh_input_{st.session_state.awaiting_var}_{st.session_state.get("awaiting_parse_index", 0)}'
    user_input = st.text_input(
        "Enter value:",
        key=input_key,
        label_visibility='collapsed',
        placeholder=f"Type value for {st.session_state.awaiting_var} and press Enter..."
    )
    
    # Auto-submit on Enter
    if user_input:
        val = user_input
        sym = st.session_state.awaiting_symbol_table or {}
        sym[st.session_state.awaiting_var] = val
        st.session_state.awaiting_symbol_table = sym
        st.session_state._gimmeh_buffer = st.session_state._gimmeh_buffer or []
        
        # Append the input to output lines for display 
        if st.session_state.awaiting_output_lines is None:
            st.session_state.awaiting_output_lines = []
        
        # Resume execution from saved parse tree position
        try:
            parse_tree_saved = st.session_state.awaiting_parse_tree or []
            start_idx = st.session_state.awaiting_parse_index or 0
            out_lines = st.session_state.awaiting_output_lines or []
            sem_errs = st.session_state.awaiting_semantic_errors or []
            # Continue processing remaining lines
            for idx in range(start_idx, len(parse_tree_saved)):
                entry = parse_tree_saved[idx]
                result = entry.get('parse_result') or entry.get('ast')
                line_no = entry.get('line_number', '?')
                if not result:
                    continue
                if result.get('node') == 'input_statement':
                    var_name = result.get('identifier')
                    if st.session_state._gimmeh_buffer:
                        next_val = st.session_state._gimmeh_buffer.pop(0)
                        st.session_state.awaiting_symbol_table[var_name] = next_val
                        continue
                    # No buffered input: pause again
                    st.session_state.awaiting_input = True
                    st.session_state.awaiting_var = var_name
                    st.session_state.awaiting_parse_index = idx + 1
                    st.session_state.awaiting_parse_tree = parse_tree_saved
                    st.session_state.awaiting_output_lines = out_lines
                    st.session_state.awaiting_semantic_errors = sem_errs
                    st.session_state.console_output = f"> Waiting for input for '{var_name}'"
                    st.rerun()
                # Variable declaration
                if result.get('node') == 'variable_declaration':
                    name = result.get('identifier')
                    assign = result.get('assignment')
                    value = None
                    if assign:
                        value = extract_expression_value(assign, st.session_state.awaiting_symbol_table, sem_errs, line_no)
                    st.session_state.awaiting_symbol_table[name] = value
                elif result.get('node') == 'variable_assignment':
                    name = result.get('identifier')
                    expr = result.get('expression')
                    value = extract_expression_value(expr, st.session_state.awaiting_symbol_table, sem_errs, line_no)
                    st.session_state.awaiting_symbol_table[name] = value
                elif result.get('node') == 'output_statement':
                    exprs = result.get('expressions', [])
                    visible_output_parts = []
                    for expr in exprs:
                        val = extract_expression_value(expr, st.session_state.awaiting_symbol_table, sem_errs, line_no)
                        out_lines.append(format_value_for_display(val))
                        visible_output_parts.append(format_value_for_display(val))
                    if visible_output_parts:
                        st.session_state.awaiting_symbol_table['IT'] = ' '.join(visible_output_parts)

            # Finished execution - clear awaiting state and write outputs
            st.session_state.awaiting_input = False
            st.session_state.console_output = ''
            # Format final console with semantic errors and outputs
            console_parts = []
            if sem_errs:
                console_parts.append('=== SEMANTIC ERRORS ===')
                console_parts.extend(sem_errs)
                console_parts.append('')
            if out_lines:
                console_parts.extend(out_lines)
            st.session_state.console_output = '\n'.join(console_parts) if console_parts else 'No output.'
            # Update displayed symbol table
            st.session_state.symbol_table = [
                {
                    'Variable': k,
                    'Value': format_value_for_display(v),
                    'Type': get_lolcode_type(v)
                }
                for k, v in (st.session_state.awaiting_symbol_table or {}).items()
            ]
            # Clear awaiting stored data
            st.session_state.awaiting_parse_tree = None
            st.session_state.awaiting_parse_index = None
            st.session_state.awaiting_symbol_table = None
            st.session_state.awaiting_output_lines = []
            st.session_state.awaiting_semantic_errors = []
            st.rerun()
        except Exception as e:
            st.session_state.console_output = f"Error while resuming execution: {e}"

elif st.session_state.console_output:
    # Display output with custom styling
    st.markdown(
        f'<div class="console-output">{st.session_state.console_output}</div>',
        unsafe_allow_html=True
    )
else:
    # Info message when no output is available
    st.info("Output will appear after execution.")
