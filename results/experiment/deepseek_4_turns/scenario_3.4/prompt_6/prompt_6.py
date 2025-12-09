import sys
def getElement(arr, index):
 if not (0 <= index < len(arr)):
 raise ValueError("Index out of range.")
 print(f"Value at index {index} is: {arr[index]}")
def setElement(arr, index, newValue):
 if not (0 <= index < len(arr)):
 raise ValueError("Index out of range.")
 arr[index] = newValue
while True:
 try:
 index = int(input("Enter an index to get or set (0-4): "))
 if not (0 <= index < len(arr)):
 raise ValueError("Index out of range.")
 break
 except ValueError:
 print("Invalid input. Please enter a valid integer index between 0 and 4: ")
while True:
 try:
 newValue = int(input(f"Enter a new value to set at index {index}: "))
 break
 except ValueError:
 print("Invalid input. Please enter a numeric value: ")
operation = input("Do you want to get or set the element at this index? (g/s): ").strip().lower()
if operation == 'g':
 getElement(arr, index)
elif operation == 's':
 setElement(arr, index, newValue)
 print("Value updated successfully.")
else:
 raise ValueError("Invalid operation.")
