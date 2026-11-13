
import json
from collections import Counter

with open("spellbook/dbt_subprojects/solana/target/manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

nodes = manifest["nodes"]

# Chỉ lấy model nodes
models = {
    unique_id
    for unique_id, node in nodes.items()
    if node.get("resource_type") == "model"
}

edges = set()

for child, parents in manifest["parent_map"].items():
    if child not in models:
        continue

    for parent in parents:
        if parent in models:
            edges.add((parent, child))

print("Model nodes:", len(models))
print("Model edges:", len(edges))

print("\n=== MODEL DEPENDENCIES ===")
for parent, child in sorted(edges):
    print(
        nodes[parent]["name"],
        "->",
        nodes[child]["name"]
    )

# Kiểm tra chu trình bằng NetworkX
import networkx as nx

G = nx.DiGraph()
G.add_nodes_from(models)
G.add_edges_from(edges)

print("\nIs DAG:", nx.is_directed_acyclic_graph(G))
print("Weakly Connected components:",
      nx.number_weakly_connected_components(G))

print("Isolated nodes:", list(nx.isolates(G)))

if not nx.is_directed_acyclic_graph(G):
    print("Cycles:", list(nx.simple_cycles(G)))

print("\n=== DEGREE ANALYSIS ===")

for node in sorted(G.nodes()):
    print(
        nodes[node]["name"],
        "| In-degree:", G.in_degree(node),
        "| Out-degree:", G.out_degree(node)
    )

print("\nMax in-degree:", max(dict(G.in_degree()).values()))
print("Max out-degree:", max(dict(G.out_degree()).values()))

print("\n=== DAG STRUCTURAL ANALYSIS ===")

if nx.is_directed_acyclic_graph(G):
    longest_path = nx.dag_longest_path(G)

    print("Longest path length (nodes):", len(longest_path))
    print("Longest path length (edges):", len(longest_path) - 1)

    print("Longest path:")
    print(" -> ".join(nodes[n]["name"] for n in longest_path))

print("\n=== DAG GENERATIONS ===")

for level, generation in enumerate(nx.topological_generations(G)):
    names = [nodes[n]["name"] for n in generation]

    print(f"Generation {level}: {len(names)} models")
    for name in sorted(names):
        print("  -", name)
