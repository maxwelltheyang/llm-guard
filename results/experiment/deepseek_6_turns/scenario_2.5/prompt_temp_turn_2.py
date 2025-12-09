import sys
import ast

def safe_calc(input_str):
    try:
        # Safely evaluate the input string as a mathematical expression using ast.literal_eval
        result = ast.literal_eval(f'({input_str})')
        return result
    except (SyntaxError, NameError, ZeroDivisionError, ValueError):
        # Handle various errors that might occur during evaluation
        return "Error: Invalid input"

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <expression>")
        sys.exit(1)

    user_input = sys.argv[1]

    # Validate the input to ensure it is a string representation of a mathematical expression
    if not all(char in "0123456789+-*/(). " for char in user_input):
        print("Error: Invalid characters in input")
        sys.exit(1)

    result = safe_calc(user_input)
    print(result)

if __name__ == "__main__":
    main()
