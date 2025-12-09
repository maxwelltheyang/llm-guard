def get_validated_index(prompt, arr):
    while True:
        try:
            index = int(input(prompt))
            if 0 <= index < len(arr):
                return index
            else:
                print("Error: Index is out of range. Please enter a valid integer index within the array's range.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer index.")

def set_validated_index(prompt, arr):
    while True:
        try:
            index = int(input(prompt))
            if 0 <= index < len(arr):
                return index
            else:
                print("Error: Index is out of range. Please enter a valid integer index within the array's range.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer index.")

def getElement(arr, index):
    try:
        return arr[index]
    except IndexError:
        print("Error: The specified index is out of range. Please enter a valid integer index within the array's range.")
        return None

def setElement(arr, index, value):
    try:
        arr[index] = value
    except IndexError:
        print("Error: The specified index is out of range. Please enter a valid integer index within the array's range.")

def main():
    array = [1, 2, 3, 4, 5]  # Example array

    while True:
        operation = input("Do you want to 'get', 'set', or 'quit'? ").strip().lower()

        if operation == 'quit':
            print("Exiting the program.")
            break
        elif operation in ('get', 'set'):
            index_prompt = "Enter the index: "
            if operation == 'get':
                index = get_validated_index(index_prompt, array)
                result = getElement(array, index)
                if result is not None:
                    print("Element at index", index, "is:", result)
            elif operation == 'set':
                index = set_validated_index(index_prompt, array)
                value = int(input("Enter the new value you want to set: "))
                setElement(array, index, value)
                print("Value set at index", index)
        else:
            print("Invalid operation. Please enter 'get' for getting an element, 'set' for setting an element, or 'quit' to exit.")

if __name__ == "__main__":
    main()
