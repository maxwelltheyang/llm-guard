def get_element(arr, index):
    try:
        return arr[index]
    except IndexError as e:
        raise IndexError(f"Index {index} out of range for array") from None

def set_element(arr, index, value):
    if arr is None: 
        raise ValueError("Null array pointer")
    arr[index] = value

arr = [1, 2, 3]

try:
    print("Element at index 2: ", get_element(arr, 2))

    set_element(arr, 5, 7)

    for i in range(10):
        if i < len(arr):
            print(arr[i])
except Exception as e:
    print("Exception caught: ", str(e))
