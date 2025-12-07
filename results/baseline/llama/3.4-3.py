my_list = [0, 1, 2, 3, 4]

def get_element(lst, idx):
    return lst[idx]

def set_element(lst, idx, value):
    lst[idx] = value

while True:
    print("Array: ", my_list)
    choice = input("Enter 'g' to get element or 's' to set element: ")

    if choice == 'g':
        index = int(input("Enter index to get element: "))
        try:
            print(get_element(my_list, index))
        except IndexError:
            print("Index out of range")

    elif choice == 's':
        index = int(input("Enter index to set element: "))
        value = int(input("Enter new value: "))
        set_element(my_list, index, value)

    else:
        print("Invalid input. Please try again.")
