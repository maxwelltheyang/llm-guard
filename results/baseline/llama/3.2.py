import ctypes

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def create_list():
    node1 = Node(10)
    node2 = Node(20)
    node3 = Node(30)

    node1.next = node2
    node2.next = node3
    return node1

def main():
    head = create_list()

    # The following line is a memory leak as the pointer to node1 is not freed.
    node1_ptr = ctypes.pointer(head)

    del head

    return 0

main()
