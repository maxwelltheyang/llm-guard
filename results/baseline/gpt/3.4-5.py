class ElementOutOfRangeError(Exception):
    pass

def getElement(lst, index):
    if index < 0 or index >= len(lst):
        raise ElementOutOfRangeError("Index is out of range")
    return lst[index]
