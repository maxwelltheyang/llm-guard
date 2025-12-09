def validate_index(index, length):
    if not isinstance(index, int) or index < 0 or index >= length:
        raise ValueError("Please enter a valid integer index within the array's range.")

def getElement(arr, index):
    try:
        validate_index(index, len(arr))
        return arr[index]
    except IndexError:
        print("Error: The specified index is out of range. Please enter a valid index within the array's range.")
    except ValueError as e:
        print(f"Error: {e}")

def setElement(arr, index, value):
    try:
        validate_index(index, len(arr))
        arr[index] = value
    except IndexError:
        print("Error: The specified index is out of range. Please enter a valid index within the array's range.")
    except ValueError as e:
        print(f"Error: {e}")

def main():
    arr = [1, 2, 3, 4, 5]  # Example array

    while True:
        operation = input("Do you want to get an element by index, set an element at a specific index, or quit? Please enter 'g', 's', or 'q': ").strip().lower()

        if operation == 'q':
            print("Exiting the program.")
            break
        elif operation in ['g', 's']:
            try:
                if operation == 'g':
                    index = int(input("Please enter the index to get: ").strip())
                    result = getElement(arr, index)
                    if result is not None:
                        print("Element at index", index, "is:", result)
                elif operation == 's':
                    index = int(input("Please enter the index to set: ").strip())
                    value = int(input("Enter the new value you want to set: ").strip())
                    setElement(arr, index, value)
                    print("Value set at index", index)
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        else:
            print("Invalid operation. Please enter 'g' for getting an element, 's' for setting an element, or 'q' to quit.")

if __name__ == "__main__":
    main()
