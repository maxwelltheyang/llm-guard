def validate_index(prompt, arr):
    while True:
        try:
            index = int(input(prompt))
            if 0 <= index < len(arr):
                return index
            else:
                print("Error: Index is out of range. Please enter a valid integer index within the array's range.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer index.")

def main():
    array = [1, 2, 3, 4, 5]  # Example array for demonstration purposes

    while True:
        operation_prompt = "Do you want to 'get', 'set', or 'quit'? "
        operation = input(operation_prompt).strip().lower()

        if operation == 'quit':
            print("Exiting the program.")
            break
        elif operation in ('get', 'set'):
            index_prompt = f"Please enter an index to {'get' if operation == 'get' else 'set'}: "
            index = validate_index(index_prompt, array)
            if operation == 'get':
                print("Element at index", index, "is:", array[index])
            elif operation == 'set':
                value_prompt = "Enter the new value you want to set: "
                value = int(input(value_prompt))
                array[index] = value
                print("Value set at index", index)
        else:
            print("Invalid operation. Please enter 'get' for getting an element, 'set' for setting an element, or 'quit' to exit.")

if __name__ == "__main__":
    main()
