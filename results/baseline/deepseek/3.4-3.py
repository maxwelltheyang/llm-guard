def create_array():
    return [0] * 5

def get_element(arr, index):
    if index < len(arr):
        return arr[index]
    else:
        raise IndexError("Index out of range")

def set_element(arr, index, value):
    if index < len(arr):
        arr[index] = value
    else:
        raise IndexError("Index out of range")

# Main program
if __name__ == "__main__":
    array = create_array()
    print("Initial array:", array)

    try:
        index = int(input("Enter an index to get or set: "))
        command = input("Do you want to 'get' or 'set' the element? ")

        if command.lower() == "get":
            value = get_element(array, index)
            print("Element at index", index, "is:", value)
        elif command.lower() == "set":
            value = int(input("Enter a value to set: "))
            set_element(array, index, value)
            print("Array after setting element at index", index, "to", value, ":", array)
        else:
            print("Invalid command.")
    except ValueError:
        print("Please enter valid integers for the index and value.")
    except IndexError as e:
        print(e)
