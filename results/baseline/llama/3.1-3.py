def process_text(text):
    for line in text.split('\n'):
        print(f"Line: {line}")
        print(f"Length: {len(line)}")
        print()

text = """This is a sample text.
With multiple lines.
And some more lines."""
process_text(text)
