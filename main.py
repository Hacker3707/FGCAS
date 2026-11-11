from src.fgcas.dag import DAG, Task

dag = DAG(
    time_unit="hour",
    project_delay=0,
    slack_threshold=2
)

dag.add_task(Task("A", 3))
dag.add_task(Task("B", 2))
dag.add_task(Task("C", 5))
dag.add_task(Task("D", 4))

dag.add_dependency("A", "B")
dag.add_dependency("A", "C")
dag.add_dependency("B", "D")
dag.add_dependency("C", "D")

print("ES:", dag.calculate_es())
print("LS:", dag.calculate_ls())
print("Slack:", dag.calculate_slack())
print("Classification:", dag.classify_slack())