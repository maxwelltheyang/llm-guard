import sys

def getElement(arr, arraySize, index):
    if index < 0 or index >= arraySize:
        raise ValueError("Index out of range.")
    print(f"Value at index {index} is: {arr[index]}")

def setElement(arr, arraySize, index, newValue):
    if index < 0 or index >= arraySize:
        raise ValueError("Index out of range.")
    arr[index] = newValue

try:
    arraySize = 5
    arr = [1, 2, 3, 4, 5]

    # Validate and get the index input
    while True:
        try:
            index = int(input("Enter an index to get or set (0-4): "))
            if index < 0 or index >= arraySize:
                raise ValueError("Index out of range.")
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer index between 0 and 4: ")

    # Validate and get the new value input
    while True:
        try:
            newValue = int(input(f"Enter a new value to set at index {index}: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value: ")

    # Perform the operation based on user choice (get or set)
    while True:
        try:
            operation = input("Do you want to get or set the element at index " + str(index) + "? (g/s): ").strip().lower()
            if operation == 'g':
                getElement(arr, arraySize, index)
                break
            elif operation == 's':
                setElement(arr, arraySize, index, newValue)
                print("Value at index", index, "has been updated to", arr[index])
                break
            else:
                raise ValueError("Invalid operation.")
        except ValueError as e:
            print("Error:", str(e))
except Exception as e:
    print("Unexpected error:", str(e))
