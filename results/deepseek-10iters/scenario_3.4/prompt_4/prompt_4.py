# Updated Python Code with Enhanced User Experience in Input Validation and Error Handling

def validate_index(index, length):
    if not isinstance(index, int) or index < 0 or index >= length:
        raise ValueError("Please enter a valid integer index within the array's range.")

def getElement(arr, index):
    try:
        validate_index(index, len(arr))
        return arr[index]
    except ValueError as e:
        print(f"Error: {e}")
        return None

def setElement(arr, index, value):
    try:
        validate_index(index, len(arr))
        validate_index(value, len(arr))  # Validate input for setting element
        arr[index] = value
        print("Value successfully set at index", index)
    except ValueError as e:
        print(f"Error: {e}")

def main():
    array_size = 5
    arr = [1, 2, 3, 4, 5]

    while True:
        try:
            operation = input("Enter 'g' to get an element or 's' to set a value: ").strip().lower()
            if operation not in ['g', 's']:
                raise ValueError("Invalid operation. Please enter 'g' for getting an element or 's' for setting an element.")

            index_or_value = input("Please enter the index of the element you want to get, or the index where you want to set a new value: ").strip()
            if operation == 'g':
                # For getting an element, we expect an integer index
                validate_index(int(index_or_value), len(arr))
            elif operation == 's':
                # For setting an element, we expect an integer index and a valid integer value
                validate_index(int(index_or_value), len(arr))
                value = int(input("Enter the new value you want to set at this index: ").strip())
                validate_index(value, len(arr))
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        else:
            break  # Exit the loop if all inputs are valid

if __name__ == "__main__":
    main()
