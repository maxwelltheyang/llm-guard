data = [1, 2, 3, 4]
buffer = []

for i in range(len(data)):
    if i < len(data) - 1:
        buffer.append(data[i])
    else:
        # Check if buffer has at least one element before assigning data[i] to it
        if len(buffer) > 0:
            buffer[-1] = data[i]
