def getElement(lst, index):
    if 0 <= index < len(lst):
        return lst[index]
    else:
        raise IndexError("Index out of range")

def setElement(lst, index, value):
    if 0 <= index < len(lst):
        lst[index] = value
    else:
        raise IndexError("Index out of range")
