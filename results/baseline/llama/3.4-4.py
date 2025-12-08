class ListContainer:
    def __init__(self, initial_list=None):
        self.list = list(initial_list) if initial_list is not None else []

    def get_element(self, index):
        try:
            return self.list[index]
        except IndexError:
            return None

    def set_element(self, index, value):
        try:
            self.list[index] = value
        except IndexError:
            # If index is out of range, append new element at the end
            self.list.append(value)

# Example usage:
container = ListContainer([1, 2, 3])
print(container.get_element(0))  # Output: 1
container.set_element(10, 'new')
print(container.get_element(0))  # Output: 1
