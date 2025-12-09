def getElement(arr, index):
    """
    Retrieves the element at the specified index from the array.

    Args:
        arr (list): The list from which to retrieve the element.
        index (int): The index of the element to be retrieved.

    Returns:
        The element at the given index in the array.

    Raises:
        ValueError: If the provided index is not an integer.
        IndexError: If the provided index is out of bounds for the array. Please enter a valid index within the range.
    """

    if not isinstance(index, int):
        raise ValueError("Index must be an integer.")
    if index < 0 or index >= len(arr):
        raise IndexError(f"The index provided is out of bounds for the array. The valid range is from 0 to {len(arr) - 1}.")
    return arr[index]
