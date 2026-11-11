
class Task:
    def __init__(self, task_id, duration, release_time=1):
        self.id = task_id
        self.duration = duration
        self.release_time = release_time

        self.predecessors = set()
        self.successors = set()


class DAG:
    def __init__(self):
        self.tasks = {}

    # Add task
    def add_task(self, task):
        if task.id in self.tasks:
            raise ValueError(f"Task {task.id} already exists")

        self.tasks[task.id] = task

    # Add dependency
    def add_dependency(self, predecessor, successor):
        if predecessor not in self.tasks:
            raise ValueError(f"Task {predecessor} does not exist")

        if successor not in self.tasks:
            raise ValueError(f"Task {successor} does not exist")

        if predecessor == successor:
            raise ValueError("A task cannot depend on itself")

        self.tasks[predecessor].successors.add(successor)
        self.tasks[successor].predecessors.add(predecessor)

    # Get successors
    def get_successors(self, task_id):
        return self.tasks[task_id].successors

    # Get predecessors
    def get_predecessors(self, task_id):
        return self.tasks[task_id].predecessors

    # Validate DAG
    def validate_dag(self):
        visited = set()
        rec_stack = set()

        def dfs(task_id):
            if task_id in rec_stack:
                return False

            if task_id in visited:
                return True

            visited.add(task_id)
            rec_stack.add(task_id)

            for successor in self.tasks[task_id].successors:
                if not dfs(successor):
                    return False

            rec_stack.remove(task_id)
            return True

        for task_id in self.tasks:
            if not dfs(task_id):
                return False

        return True

    # Topological sort
    def topological_sort(self):
        if not self.validate_dag():
            raise ValueError("Cannot perform topological sort: cycle detected")

        visited = set()
        stack = []

        def dfs(task_id):
            visited.add(task_id)

            for successor in self.tasks[task_id].successors:
                if successor not in visited:
                    dfs(successor)

            stack.append(task_id)

        for task_id in self.tasks:
            if task_id not in visited:
                dfs(task_id)

        return stack[::-1]
