from src.fgcas.dag import DAG, Task

def test_calculate_es():
    dag = DAG()

    dag.add_task(Task("A", 3))
    dag.add_task(Task("B", 2))

    dag.add_dependency("A", "B")

    es = dag.calculate_es()

    assert es["A"] == 1
    assert es["B"] == 4