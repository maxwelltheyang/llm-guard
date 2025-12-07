import datetime

class Student:
    def __init__(self, name):
        self.name = name
        self.score = 0

class Admin:
    def __init__(self, username):
        self.username = username

class SchoolDatabase:
    def __init__(self):
        self.students = {}

    def add_student(self, student):
        self.students[student.name] = student

    def update_score(self, admin, student_name, new_score):
        if admin.username == 'admin1':
            self.students[student_name].score = new_score
            with open('audit_log.txt', 'a') as f:
                f.write(f'{datetime.datetime.now()} - {admin.username} updated score of {student_name} to {new_score}\n')

# Example usage:
db = SchoolDatabase()
admin = Admin('admin1')
db.add_student(Student('John'))
db.update_score(admin, 'John', 90)
