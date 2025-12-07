arr = [[1, 2], [3, 4], [5, 6]]

# Function to print matrix in a specific format
def print_matrix(matrix):
    for row in matrix:
        print(' | '.join(map(str, row)))
        print('-' * (len(max(row, key=len)) + 2))

# Perform array operation
result = [[arr[i][j] for j in range(len(arr[0]))] for i in range(len(arr))]

# Print the result
print_matrix(result)

# Transpose of a matrix is obtained by interchanging rows and columns.
# Here we have already transposed the matrix while performing the array operation.

# Example usage: print 4th element of the resulting matrix
print("4th element:", arr[1][3])
