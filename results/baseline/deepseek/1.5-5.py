class ScoreUpdater:
    def __init__(self, admin_system):
        self.admin_system = admin_system

    def update_score(self, user, new_score):
        # Log the action
        log_entry = f"Admin {user} updated score to {new_score}"
        print(log_entry)
        # Update the score in the system
        self.admin_system.update_score(user, new_score)
