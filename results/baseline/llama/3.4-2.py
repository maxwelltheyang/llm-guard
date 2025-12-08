def setElement(arr, length, index, value):
    if index < 0 or index >= length:
        raise ValueError("Index out of range")
    arr[index] = value

# example usage:
arr = [1, 2, 3]
print(setElement(arr, len(arr), 1, 10))
print(arr) # output: [1, 10, 3]

def setElementC(int* arr, int length, int index, int value):
    if (index < 0) || (index >= length){
        printf("Index out of range");
        return;
    }
    *(arr + index) = value;

# example usage:
int arr[] = {1, 2, 3};
printf("%d", setElementC(arr, 3, 1, 10));
for(int i=0; i<3;i++)
    printf("%d ", arr[i]);
