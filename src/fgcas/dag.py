
class Task:
    def __init__(
        self,
        task_id,
        duration,
        release_time=1
    ):
        self.id = task_id
        self.duration = duration
        self.release_time = release_time

        self.predecessors = set()
        self.successors = set()


class DAG:
    def __init__(
        self,
        time_unit="hour",
        project_delay=0,
        slack_threshold=0
    ):
        self.tasks = {}
        self.time_unit = time_unit
        self.project_delay = project_delay
        self.slack_threshold = slack_threshold

        if project_delay < 0:
            raise ValueError("Project delay cannot be negative")

        if slack_threshold < 0:
            raise ValueError("Slack threshold cannot be negative")

    # Add task
    def add_task(self, task):
        if task.id in self.tasks:
            raise ValueError(f"Task {task.id} already exists")

        if task.duration < 0:
            raise ValueError("Task duration cannot be negative")

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
            raise ValueError(
                "Cannot perform topological sort: cycle detected"
            )

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

    # Calculate Earliest Start
    def calculate_es(self):
        if not self.validate_dag():
            raise ValueError("Cannot calculate ES: cycle detected")

        order = self.topological_sort()
        es = {}

        for task_id in order:
            task = self.tasks[task_id]

            if not task.predecessors:
                es[task_id] = task.release_time

            else:
                predecessor_finish = max(
                    es[pred] + self.tasks[pred].duration
                    for pred in task.predecessors
                )

                es[task_id] = max(
                    task.release_time,
                    predecessor_finish
                )

        return es

    # Calculate Latest Start
    def calculate_ls(self):
        if not self.validate_dag():
            raise ValueError("Cannot calculate LS: cycle detected")

        if not self.tasks:
            return {}

        es = self.calculate_es()
        order = self.topological_sort()

        # Calculate earliest project completion time
        project_finish = max(
            es[task_id] + self.tasks[task_id].duration
            for task_id in self.tasks
        )

        # Project deadline
        deadline = project_finish + self.project_delay

        ls = {}

        # Backward pass
        for task_id in reversed(order):
            task = self.tasks[task_id]

            if not task.successors:
                latest_finish = deadline

            else:
                latest_finish = min(
                    ls[successor]
                    for successor in task.successors
                )

            ls[task_id] = latest_finish - task.duration

        return ls

    # Calculate Slack
    def calculate_slack(self):
        es = self.calculate_es()
        ls = self.calculate_ls()

        slack = {}

        for task_id in self.tasks:
            slack[task_id] = ls[task_id] - es[task_id]

        return slack

    # Classify Slack
    def classify_slack(self):
        slack = self.calculate_slack()
        status = {}

        for task_id, value in slack.items():

            if value == 0:
                status[task_id] = "Critical"

            elif value <= self.slack_threshold:
                status[task_id] = "Near-Critical"

            else:
                status[task_id] = "Safe"

        return status

    # Calculate Tail Length
    def calculate_tail_length(self):
        pass


    # Calculate Critical Paths
    def calculate_critical_paths(self):
        slack = self.calculate_slack()

        critical_tasks = {
            task_id
            for task_id, value in slack.items()
            if abs(value) < 1e-9
        }

        paths = []

        def dfs(task_id, current_path):
            current_path.append(task_id)

            if not self.tasks[task_id].successors:
                paths.append(current_path.copy())

            else:
                for successor in self.tasks[task_id].successors:
                    if successor in critical_tasks:
                        dfs(successor, current_path)

            current_path.pop()

        # Start from critical tasks without critical predecessors
        for task_id in critical_tasks:
            critical_predecessors = (
                self.tasks[task_id].predecessors
                & critical_tasks
            )

            if not critical_predecessors:
                dfs(task_id, [])

        return paths

