import sys
import logging

logging.basicConfig(level=logging.ERROR)

def validate_input(value: int) -> None:
    if not isinstance(value, int):
        raise ValueError(f"Input must be an integer.")
    elif value < 0:
        raise ValueError("Input must be a non-negative integer.")

def getSanitizedIntegerInput(prompt: str = "") -> int:
    while True:
        try:
            value = int(input(prompt))
            if value > sys.maxsize or value == -1: 
                print(f"Error: Input too large. Please enter a number less than {sys.maxsize}.")
                continue
            validate_input(value)
            return value
        except EOFError:
            logging.error("End of file reached.")
        except KeyboardInterrupt:
            sys.exit(0)

def handlePotentialDosAttack(size: int) -> None:
    try:
        validate_input(size)
    except ValueError as e:
        raise ValueError(f"Input is invalid. Reason: {e}")

def main() -> None:
    size = getSanitizedIntegerInput("Enter the size of the list (non-negative integer): ")

    if size > sys.maxsize:
        raise ValueError("Size exceeds maximum limit.")

    try:
        lst = [i for i in range(size)]

        # Process the list
        print(get_element(lst, 0))

        if size > 0:
            print(get_element(lst, -1))  # Test out-of-range index

        return 0
    except MemoryError as e:
        logging.error(f"Insufficient memory to create a list of size {size}.")
        print("Memory Error: Insufficient memory to create the list. Please consider reducing the list size or running with more memory.")
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

def get_element(lst, index):
    if index > len(lst) - 1:
        print("Index out of range. List size is", len(lst))
        return None
    try:
        return lst[index]
    except IndexError as e:
        print(f"Index out of range: {str(e)}")
        return None

if __name__ == "__main__":
    main()
