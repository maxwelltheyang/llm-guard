def getElement(lst, index):
    if index < 0 or index >= len(lst):
        raise IndexError("Index out of range")
    return lst[index]
