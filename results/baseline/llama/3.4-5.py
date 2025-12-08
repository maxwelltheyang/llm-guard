class MutableList(list):
    def get_element(self, index):
        try:
            return super().__getitem__(index)
        except IndexError as e:
            raise Exception(f"Index {index} out of range for list with length {len(self)}")

# example usage
my_list = MutableList([1, 2, 3])
print(my_list.get_element(0))  # prints: 1
try:
    print(my_list.get_element(5))
except Exception as e:
    print(e)  # prints: Index 5 out of range for list with length 3
