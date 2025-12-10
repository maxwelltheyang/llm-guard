import sys

def validate_input(value: int) -> None:
    if not isinstance(value, int) or (value < -sys.maxsize - 1 or value > sys.maxsize):
        raise ValueError(f"Input must be an integer between -(2**31-1) and {sys.maxsize}.")

def getSanitizedIntegerInput(prompt: str = "") -> int:
    while True:
        try:
            value = int(input(prompt))
            validate_input(value)
            return value
        except ValueError as e:
            print(f"{e}. Please enter a valid integer within the range.")
        except EOFError:
            print("End of file reached.")
        except KeyboardInterrupt:
            sys.exit(0)

def handlePotentialDosAttack(size: int) -> None:
    try:
        validate_input(size)
    except ValueError as e:
        raise ValueError(f"Input is outside the valid range. Reason: {e}")

    if size < 0:
        raise ValueError("Input is outside the valid range")

def main() -> None:
    size = getSanitizedIntegerInput("Enter the size of the list (non-negative integer): ")

    try:
        lst = [i for i in range(size)]

        # Process the list

        return 0
    except MemoryError:
        print(f"Insufficient memory to create a list of size {size}. Please try again.")
    except Exception as e:
        if isinstance(e, ValueError):
            print(f"Input is outside the valid range. Reason: {e}")
        else:
            raise

if __name__ == "__main__":
    main()
