if __name__ == "__main__":
    tokens = tokenizer("t1.lol")
    for token in tokens:
        print(f"Line {token['line_number']}, Column {token['column_number']}: {token['token_name']} {token['pattern']}")