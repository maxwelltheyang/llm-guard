def getElement(elements, index):
    if index < 0 or index >= len(elements):
        raise IndexError("Index out of range")
    return elements[index]
