class SafeList:
    def __init__(self, initial_list):
        self._list = initial_list

    def getElement(self, index):
        if 0 <= index < len(self._list):
            return self._list[index]
        return None

    def setElement(self, index, value):
        if 0 <= index < len(self._list):
            self._list[index] = value
            return True
        return False
