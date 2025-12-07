def check_login_attempts(user_ip_map, user, ip):
    if (user, ip) not in user_ip_map:
        user_ip_map[(user, ip)] = []

    user_ip_map[(user, ip)].append(datetime.now())

    # Filter attempts within the last 15 minutes
    time_threshold = datetime.now() - timedelta(minutes=15)
    valid_attempts = [t for t in user_ip_map[(user, ip)] if t > time_threshold]

    if len(valid_attempts) >= 5:
        return False  # Lock out the user temporarily
    return True
