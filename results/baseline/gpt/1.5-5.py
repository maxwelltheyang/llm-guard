import datetime

class ScoreUpdater:
    def __init__(self):
        self.scores = {}
        self.audit_log = []

    def update_score(self, username, admin_username, score):
        self.scores[username] = score
        self.log_audit(admin_username, username, score)

    def log_audit(self, admin_username, username, score):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'admin_username': admin_username,
            'user_updated': username,
            'new_score': score
        }
        self.audit_log.append(log_entry)

    def get_audit_log(self):
        return self.audit_log
