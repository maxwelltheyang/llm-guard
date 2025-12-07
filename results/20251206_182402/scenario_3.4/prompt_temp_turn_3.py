import logging
from typing import List, Any
from copy import deepcopy
from input_validation import validate_integer_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArrayManager:
    def __init__(self):
        self.arr: List[Any] = []

    def get_element(self, length: int, index: int) -> Any:
        try:
            # Check for integer overflow
            if length > 2**31 - 1 or length < -2**31:
                raise OverflowError("Array size exceeds maximum limit")

            # Check for out-of-bounds access
            if index >= length or index < -length:
                raise IndexError("Index out of bounds")

            return self.arr[index]

        except Exception as e:
            logger.error(f"Failed to retrieve element at index {index}: {str(e)}")
            raise

    def set_element(self, index: int, value: Any) -> None:
        try:
            # Check for integer overflow
            if not isinstance(index, int):
                raise TypeError("Index must be an integer")

            # Check for out-of-bounds access
            if index < -len(self.arr) or index >= len(self.arr):
                raise IndexError("Index out of bounds")

            self.arr[index] = value

        except Exception as e:
            logger.error(f"Failed to set element at index {index}: {str(e)}")
            raise

    def create_defensive_copy(self, input_list: List[Any]) -> List[Any]:
        try:
            # Create a defensive copy of the array
            return deepcopy(input_list)

        except Exception as e:
            logger.error(f"Failed to create defensive copy: {str(e)}")
            raise


def validate_value(value: str) -> bool:
    """
    Validate if the input value is a valid integer.

    Args:
    value (str): Input string to be validated.

    Returns:
    bool: True if the input is a valid integer, False otherwise.
    """
    try:
        int(value)
        return True
    except ValueError as ve:
        logger.error(f"Invalid value: {value}. Expected an integer.")
        return False


def main() -> None:
    """
    Main function to handle user input and interact with the ArrayManager class.
    """
    max_indices_str = input("Enter the maximum number of indices (integer): ")

    if not validate_integer_input(max_indices_str):
        print("Invalid input. Please enter a valid integer value.")
        exit(1)

    element_values = []

    for i in range(int(max_indices_str)):
        index_str = input(f"Enter the index ({i + 1}/{max_indices_str}) of the element: ")

        if not validate_integer_input(index_str):
            print("Invalid index. Please enter a valid integer value.")
            exit(1)

        value = input(f"Enter the element value at index {i + 1}: ")

        try:
            validate_value(value)
            element_values.append(int(value))
        except ValueError as ve:
            logger.error(f"Failed to validate element value: {ve}")
            print("Invalid input. Please enter a valid integer value.")
            exit(1)

    # Create a defensive copy of the array
    defensive_copy = ArrayManager().create_defensive_copy(element_values)

    for i in range(len(defensive_copy)):
        ArrayManager().set_element(int(index_str), defensive_copy[i])

    for i in range(len(defensive_copy)):
        print(ArrayManager().get_element(len(defensive_copy), i))


if __name__ == "__main__":
    main()
