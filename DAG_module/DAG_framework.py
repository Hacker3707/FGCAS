class Task:
    def __init__(self, task_id, duration, release_time = 1):
        self.id = task_id
        self.duration = duration
        self.release_time = release_time

        self.predecessors = set()
        self.successors = set()

class DAG:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        self.tasks[task.id] = task

    def add_dependency(self, predecessor, successor):
        # predecessor must finish before successor starts
        self.tasks[predecessor].successors.add(successor)
        self.tasks[successor].predecessors.add(predecessor)

    def get_successors(self):
        pass

    def get_predecessors(self):
        pass