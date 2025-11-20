from lexer import tokenizer
from parser import parse, print_ast
import sys

def main():
    """Main function demonstrating both tokenization and parsing"""
    filename = sys.argv[1] if len(sys.argv) > 1 else "smoosh_assign.lol"
    
    try:     
        # Step 1: Lexical Analysis
        print("\n1. LEXICAL ANALYSIS (Tokenization):")
        print("-" * 40)
        tokens = tokenizer(filename)
        for t in tokens:
            print(f"Line {t['line_number']:3}, Column {t['column_number']:3}: {t['token_name']:25} '{t['pattern']}'")
        print(f"Total tokens: {len(tokens)}")
        
        # Step 2: Syntax Analysis
        print("\n2. SYNTAX ANALYSIS (Parsing):")
        print("-" * 40)
        ast = parse(filename)
        if ast:
            print_ast(ast)
        else:
            print("Parsing failed.")
            
        # wala pa muna since hindi pa ok ang syntax checker
        # no gui rin aotm
        print("\n3. SEMANTIC ANALYSIS:")
        print("-" * 40)
        print("Semantic checks would go here...")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()