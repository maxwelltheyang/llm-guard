def setElement(arr, index, value):
    if not isinstance(index, int) or not isinstance(value, int):
        raise ValueError("Both index and value must be integers.")
    arr[index] = value

def getElement(arr, index):
    if not isinstance(index, int) or index < 0 or index >= len(arr):
        raise IndexError("Index is out of bounds for the array.")
    return arr[index]

def main():
    array_length = 5
    myArray = [i * 10 for i in range(array_length)]

    try:
        print("Initial array:", [getElement(myArray, i) for i in range(array_length)])

        while True:
            try:
                index = int(input("Enter an index to set: "))
                value = int(input("Enter a value to set at that index: "))
                setElement(myArray, index, value)
                break
            except ValueError as e:
                print(f"Invalid input for the index or value: {e}")
            except IndexError as e:
                print(f"Index out of bounds: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("Updated array:", [getElement(myArray, i) for i in range(array_length)])

if __name__ == "__main__":
    main()
