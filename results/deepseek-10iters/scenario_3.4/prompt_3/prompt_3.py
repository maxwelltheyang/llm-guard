# Updated Python Code with Simplified Input Validation Logic and Improved Error Handling

def validate_index(index, length):
    if not isinstance(index, int) or index < 0 or index >= length:
        raise ValueError("Please enter a valid integer within the array's range.")

def main():
    array_size = 5
    arr = [1, 2, 3, 4, 5]

    while True:
        try:
            index = int(input("Enter the index to get or set: "))
            validate_index(index, array_size)

            operation = input("Enter 1 to get the element, or 2 to set the element: ")
            if operation == '1':
                value_to_get = arr[index]
                print(f"Element at index {index} is: {value_to_get}")
            elif operation == '2':
                new_value = int(input(f"Enter the new value to set at index {index}: "))
                arr[index] = new_value
                print("Value successfully set at index", index)
            else:
                raise ValueError("Invalid operation: Please enter 1 or 2.")
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid integer index within the array's range.")
        except IndexError:
            print("Error: Invalid index. Please enter a valid integer within the array's range.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        else:
            break  # If no exception was raised, we can safely exit the loop

if __name__ == "__main__":
    main()
