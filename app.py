import streamlit as st
import os
import glob
from lexer import tokenizer
from parser import parse
from interpreter import Interpreter
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

# Initialize code editor content in session state
if 'code_editor' not in st.session_state:
    st.session_state.code_editor = st.session_state.get('code_content', '')

# HELPER FUNCTIONS =========================================================

# Loads file content into the text editor and sync widget state
def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Update app state
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
    
# Execute the LOLCODE code and update session state
def execute_code(code_content, user_input=""):
    try:
        # Save code to temporary file for processing
        temp_file = save_temp_file(code_content)
        if not temp_file:
            return
        
        # Clear previous output
        st.session_state.console_output = ""
        
        # Tokenization
        # Break code to individual tokens 
        tokens = tokenizer(temp_file)
        st.session_state.tokens = tokens
        
        # Parsing
        # Build Abstract Syntax Tree from tokens
        ast = parse(temp_file)
        
        if not ast:
            st.session_state.console_output = "Parsing failed\n"
            st.session_state.symbol_table = []
            return
        
        # Interpretation
        # Execute the parsed AST and maintain symbol table
        interpreter = Interpreter()

        # Execute the program
        success = interpreter.interpret(ast)
        
        # Get output from the interpreter
        output = interpreter.get_output()
        if output:
            st.session_state.console_output = output
        
        # Update symbol table with all variables and their values
        st.session_state.symbol_table = interpreter.get_symbol_table_display()
        
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


# TEXT EDITOR, LEXEMES,SYMBOL TABLE ----------------------------------------
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
            symbol_display = symbol_df[['Variable', 'Value']].copy()
            symbol_display.columns = ['Identifier', 'Value']
            
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

# Check if there's output to display
if st.session_state.console_output:
    # Display output with custom styling
    st.markdown(
        f'<div class="console-output">{st.session_state.console_output}</div>',
        unsafe_allow_html=True
    )
else:
    # Info message when no output is available
    st.info("Output will appear after execution.")
