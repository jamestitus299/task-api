
# This is the object model of the Task
class Task:
    def __init__(self, title, description, deadline):
        # self.id = None
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = False