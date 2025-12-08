class Admin:
    def __init__(self):
        self.users = {
            "admin": {"password": "password"}
        }
        self.logged_in = False

    def login(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            self.logged_in = True
            return True
        else:
            return False

    def logout(self):
        self.logged_in = False


class Dashboard:
    def __init__(self):
        self.admin = Admin()

    def restrict_access(self, user):
        if user.logged_in:
            return "Admin dashboard"
        else:
            return "Access denied"

    def display_dashboard(self):
        if self.admin.logged_in:
            print("Admin dashboard")
        else:
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")

            if self.admin.login(username, password):
                self.display_admin_dashboard()
            else:
                print("Incorrect username or password")


    def display_admin_dashboard(self):
        while True:
            print("\nAdmin dashboard")
            print("1. View users")
            print("2. Add user")
            print("3. Remove user")
            print("4. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                # view users
                pass
            elif choice == "2":
                # add user
                pass
            elif choice == "3":
                # remove user
                pass
            elif choice == "4":
                self.admin.logout()
                break
            else:
                print("Invalid choice")


if __name__ == "__main__":
    dashboard = Dashboard()

    while True:
        print("\nWelcome to the dashboard")
        print("1. Login as admin")
        print("2. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            dashboard.display_dashboard()
        elif choice == "2" and dashboard.admin.logged_in:
            dashboard.admin.logout()
            break
        else:
            print("Invalid choice")
