# Assuming this is a hypothetical scenario where you are auditing a login system
def audit_login_flow(credentials, attempts, two_factor):
    # Check for credential stuffing by checking if there's any pattern in credentials
    if any(credential * 2 in credentials for credential in credentials):
        print("Credential stuffing detected!")

    # Check for brute force attacks by counting login attempts
    if len(attempts) > 10:
        print("Brute force attack detected!")

    # Check the robustness of 2FA
    if two_factor == "on":
        print("Two-factor authentication is robust.")
    else:
        print("Two-factor authentication is not robust enough.")

# Example usage
credentials = ["user1", "pass1", "user2", "pass2"]
attempts = ["user1", "user2", "user3", "user4", "user5", "user6", "user7", "user8", "user9", "user10", "user11"]
two_factor = "on"

audit_login_flow(credentials, attempts, two_factor)
