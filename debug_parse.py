from parse import parse_whole
import json

parse_tree, errors = parse_whole('t5.lol')
for entry in parse_tree:
    result = entry.get('parse_result') or entry.get('ast')
    if result:
        print(f"Line {entry.get('line_number')}: {result.get('node')}")
        print(json.dumps(result, indent=2, default=str))
        print('---')
