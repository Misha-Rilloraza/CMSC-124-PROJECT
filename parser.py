from parse import parse_whole, print_results

def parse(filename):
    parse_tree, errors = parse_whole(filename)
    print_results(parse_tree, errors)
    return {
        'parse_tree': parse_tree,
        'errors': errors,
        'success': len(errors) == 0
    }

if __name__ == "__main__":
    result = parse("ifelse.lol")