def validate_input(input):
    try:
        input = int(input)
        return True
    except ValueError:
        return False

def get_square_root(n):
    if n < 0:
        raise ValueError("Input cannot be negative")
    try:
        return round(n ** 0.5, 2)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def fix_issues():
    user_input = input("Please enter a number: ")

    if validate_input(user_input):
        num = get_square_root(int(user_input))
        print(f"The square root of the given number is: {num}")
    else:
        print("Invalid input. Please enter a valid integer.")

fix_issues()
