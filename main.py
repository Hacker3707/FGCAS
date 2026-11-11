from dag_module.dag_framework import DAG, Task

dag = DAG()

tasks = [
    Task("T1", 2),
    Task("T2", 3),
    Task("T3", 1),
    Task("T4", 2),
    Task("T5", 2),
    Task("T6", 1)
]

for task in tasks:
    dag.add_task(task)

dependencies = [
    ("T1", "T2"),
    ("T1", "T3"),
    ("T2", "T4"),
    ("T3", "T5"),
    ("T4", "T6"),
    ("T5", "T6")
]

for u, v in dependencies:
    dag.add_dependency(u, v)

print("Valid DAG:", dag.validate_dag())
print("Topological order:", dag.topological_sort())