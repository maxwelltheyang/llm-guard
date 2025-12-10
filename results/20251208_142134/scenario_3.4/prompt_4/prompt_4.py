def get_element(arr, index):
    if arr is None or index < 0:
        raise ValueError("Null array pointer")

    length = len(arr)

    if index >= length:
        raise IndexError("Index out of range for array")

    return arr[index]

def set_element(arr, index, value):
    if arr is None or index < 0:
        raise ValueError("Null array pointer")  

    if index >= len(arr):
        raise IndexError("Index out of range for array")        

    arr[index] = value

arr = [1, 2, 3]
length = len(arr)

try:
    print("Element at index 2: ", get_element(arr, 2))

    set_element(arr, 5, 7)

    for i in range(10):
        if i < len(arr):
            print(arr[i])
except Exception as e:
    print("Exception caught: ", str(e))

