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
        operation = input("Do you want to 'get', 'set', or 'quit'? ").strip().lower()

        if operation == 'quit':
            print("Exiting the program.")
            break
        elif operation in ('get', 'set'):
            index_prompt = "Please enter an index to get or set: "
            if operation == 'get':
                index = validate_index(index_prompt, array)
                print("Element at index", index, "is:", array[index])
            elif operation == 'set':
                index = validate_index(index_prompt, array)
                value = int(input("Enter the new value you want to set: "))
                array[index] = value
                print("Value set at index", index)
        else:
            print("Invalid operation. Please enter 'get' for getting an element, 'set' for setting an element, or 'quit' to exit.")

if __name__ == "__main__":
    main()
