import re

def tokenizer(filename):
    keywords = []
    # pattern;name
    with open('keyword.txt', 'r') as f:
        for line in f:
            if ";" in line:
                pattern, label = line.strip().split(';', 1)
                keywords.append((pattern.strip(), label.strip()))

    # combine the patterns (lexeme)
    token_patterns = []
    token_patterns.extend(keywords)
    token_patterns.append((r"\b[a-zA-Z][a-zA-Z0-9_]*\b", "Variable Identifier"))

    token_patterns.append((r'"(?:[^"\\\r\n]|\\.)*"', "String Literal"))
    token_patterns.append((r"\"", "String Delimiter"))
    token_patterns.append((r"\b[+-]?[0-9]*\.[0-9]+\b", "Float Literal"))
    token_patterns.append((r"\b[+-]?[0-9]+\b", "Integer Literal"))
    token_patterns.append((r"\b(WIN|FAIL)\b", "Boolean Literal"))
    token_patterns.append((r"\b(NOOB|NUMBR|NUMBAR|YARN|TROOF)\b", "Type Literal"))

    # simpler regex combining
    combined_regex = "|".join(f"({pattern})" for pattern, _ in token_patterns)

    print(token_patterns)

    # open sample lolcode program
    with open(filename, 'r') as f:
        program = f.read()

    # ignore comments
    # substring consideration: ignore all preceding this keywords
    # replace the characters with nothing aka ignore na rin
    program = re.sub(r"OBTW.*?TLDR", "", program, flags=re.DOTALL)  # if group commenting
    program = re.sub(r"BTW[^\n]*", "", program)

    # line number lookup
    # we use finditer (https://www.geeksforgeeks.org/python/re-finditer-in-python/)
    line_num = [0]
    for match in re.finditer('\n', program):
        line_num.append(match.end())

    def get_line_num(position):
        low, high = 0, len(line_num) - 1
        while low <= high:
            mid = (low + high) // 2
            if line_num[mid] <= position:
                low = mid + 1
            else:
                high = mid - 1
        line_no = low
        col_no = position - line_num[line_no - 1] + 1
        return line_no, col_no

    tokens = []
    for match in re.finditer(combined_regex, program):
        # Find which pattern matched (by checking which capturing group has a value)
        for i, (_, label) in enumerate(token_patterns):
            if match.group(i + 1):  # corresponds to first pattern, etc.
                value = match.group(i + 1).strip()
                # add line number
                get_num, col_no = get_line_num(match.start())
                tokens.append({"line_number": get_num, "column_number": col_no, "token_name": label, "pattern": value})
                break

    # itsura ng pagkagroup
    # print(tokens)
    for token in tokens:
        print(f"Line {token['line_number']}:Column {token['column_number']} {token['token_name']} {token['pattern']}")
    return tokens

# test (print like dun sa sample results)
# for token in tokens:
#     print(f"Line {token['line_number']}:Column {token['column_number']} {token['token_name']} {token['pattern']}")

# if __name__ == "__main__":
#     tokens = tokenizer("t1.lol")
#     for token in tokens:
#         print(f"Line {token['line_number']}, Column {token['column_number']}: {token['token_name']} {token['pattern']}")