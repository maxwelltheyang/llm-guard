import logging
from typing import List, Any
from copy import deepcopy
from input_validation import validate_integer_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArrayManager:
    def __init__(self):
        self.arr: List[Any] = []

    @staticmethod
    def get_element(array: List[Any], index: int) -> Any:
        try:
            # Check for integer overflow
            if len(array) > 2**31 - 1 or len(array) < -2**31:
                raise OverflowError("Array size exceeds maximum limit")

            # Check for out-of-bounds access
            if index >= len(array) or index < -len(array):
                raise IndexError("Index out of bounds")

            return array[index]

        except Exception as e:
            logger.error(f"Failed to retrieve element at index {index}: {str(e)}")
            raise

    @staticmethod
    def set_element(array: List[Any], index: int, value: Any) -> None:
        try:
            # Check for integer overflow
            if not isinstance(index, int):
                raise TypeError("Index must be an integer")

            # Check for out-of-bounds access
            if index >= len(array) or index < -len(array):
                raise IndexError("Index out of bounds")

            array[index] = value

        except Exception as e:
            logger.error(f"Failed to set element at index {index}: {str(e)}")
            raise


    @staticmethod
    def create_defensive_copy(elements: List[Any]) -> List[Any]:
        """
        Create a defensive copy of the input list.

        Args:
        elements (List[Any]): Input list to be copied.

        Returns:
        List[Any]: Defensive copy of the input list.
        """
        try:
            return deepcopy(elements)
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

    # Input validation for max_indices_str
    try:
        max_indices = int(max_indices_str)
        if max_indices < 0 or max_indices > (2**31 - 1) * 10:  # Check against very large numbers
            raise ValueError("Input exceeds maximum limit")
    except ValueError as ve:
        logger.error(f"Invalid value for max_indices: {max_indices_str}. Expected a positive integer.")
        print("Invalid input. Please enter a valid integer value.")
        exit(1)

    element_values = []

    for i in range(max_indices):
        index_str = input(f"Enter the index ({i + 1}/{max_indices}) of the element: ")

        if not validate_integer_input(index_str):
            print("Invalid index. Please enter a valid integer value.")
            exit(1)

        # Handle potential exception elegantly
        try:
            value = int(input(f"Enter the element value at index {i + 1}: "))
        except ValueError as ve:
            logger.error(f"Failed to validate element value: {ve}")
            print("Invalid input. Please enter a valid integer value.")
            exit(1)

        if not validate_value(str(value)):
            continue

        element_values.append(value)

    # Create a defensive copy of the array
    array_manager = ArrayManager()
    array_manager.arr = ArrayManager.create_defensive_copy(element_values)

    for i in range(len(array_manager.arr)):
        ArrayManager.set_element(array_manager.arr, int(index_str), element_values[i])

    for i in range(len(array_manager.arr)):
        print(ArrayManager.get_element(array_manager.arr, i))


if __name__ == "__main__":
    main()
