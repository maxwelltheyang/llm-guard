def process_lines(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            print(f"Line: {line.strip()}, Length: {len(line.strip())}")
