def setElement(arr, index, value):
    if not isinstance(index, int):
        raise ValueError("Index must be an integer.")
    if not isinstance(value, int):
        raise ValueError("Value must be an integer.")
    if index < 0 or index >= len(arr):
        raise IndexError("Index is out of bounds for the array. Please enter an index between 0 and " + str(len(arr) - 1) + ".")
    arr[index] = value

def getElement(arr, index):
    if not isinstance(index, int):
        raise ValueError("Index must be an integer.")
    if index < 0 or index >= len(arr):
        raise IndexError("Index is out of bounds for the array. Please enter an index between 0 and " + str(len(arr) - 1) + ".")
    return arr[index]

def main():
    array_length = 5
    myArray = [i * 10 for i in range(array_length)]

    try:
        print("Initial array:", [getElement(myArray, i) for i in range(array_length)])

        while True:
            try:
                index = int(input("Enter an index to set (between 0 and " + str(len(myArray)-1) + "): "))
                value = int(input("Enter a value to set at that index: "))
                setElement(myArray, index, value)
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter integers only.")
            except IndexError as e:
                print(str(e))  # Simplified error message access
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Updated array:", [getElement(myArray, i) for i in range(array_length)])

if __name__ == "__main__":
    main()
