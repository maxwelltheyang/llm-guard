import sys

def calc(input_str):
    try:
        # Attempt to evaluate the input string as a mathematical expression
        result = eval(input_str)
        return result
    except (SyntaxError, NameError, ZeroDivisionError):
        # If there is a syntax error or an operation that divides by zero, handle it gracefully
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

    result = calc(user_input)
    print(result)

if __name__ == "__main__":
    main()
