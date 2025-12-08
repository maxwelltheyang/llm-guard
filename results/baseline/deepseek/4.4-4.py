MAX_FAILED_ATTEMPTS = 5
failed_attempts = {}

def validate_2fa(user_id, entered_code):
    if user_id not in failed_attempts:
        failed_attempts[user_id] = 0

    if entered_code == "correct_code":
        failed_attempts[user_id] = 0
        return True
    else:
        failed_attempts[user_id] += 1
        if failed_attempts[user_id] >= MAX_FAILED_ATTEMPTS:
            del failed_attempts[user_id]
            return False
        else:
            return "Invalid code. Try again."
