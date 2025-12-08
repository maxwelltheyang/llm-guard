def find_missing_numbers(nums):
    num_set = set()
    for num in nums:
        num_set.add(num)

    missing_nums = []
    for i in range(1, max(num_set) + 1):
        if i not in num_set:
            missing_nums.append(i)

    return sorted(missing_nums)

# Test the function
nums = [4,0,3,1]
print(find_missing_numbers(nums))
