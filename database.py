from typing import List

class TaskStorage:
    def __init__(self):
        self.tasks = []
        self.current_id = 1
task_store = TaskStorage()

def get_task_store():
    
    return task_store