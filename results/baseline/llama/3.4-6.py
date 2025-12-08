import numpy as np

def array_operation(arr):
    # 1. Sort the array in ascending order
    arr.sort()

    # 2. Find the indices of all occurrences of the first element
    idx = [i for i, x in enumerate(arr) if x == arr[0]]

    # 3. Select elements from the sorted array with a step equal to the number of repetitions
    result = arr[idx[0]:idx[0] + len(idx):len(idx)]

    return result

# Example usage:
arr = np.array([5, 2, 8, 1, 9, 3, 7])
print(array_operation(arr))
