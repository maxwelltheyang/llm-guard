def create_array():
    return [0] * 5

def get_element(arr, index):
    return arr[index]

def set_element(arr, index, value):
    arr[index] = value
    return arr

def main():
    array = create_array()

    while True:
        index = int(input("Enter the index (0-4) you want to get: "))
        if 0 <= index < 5:
            print(f"Element at index {index}: {get_element(array, index)}")
            break

    while True:
        index = int(input("Enter the index (0-4) you want to set: "))
        if 0 <= index < 5:
            value = int(input("Enter the value you want to set: "))
            array = set_element(array, index, value)
            print(f"Updated array: {array}")
            break

if __name__ == "__main__":
    main()
