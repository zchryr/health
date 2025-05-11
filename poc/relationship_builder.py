# Had Claude 3.7 one shot this. I'm not sure if it's the best way to do it, but it works, ish.

import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Tuple, Optional

def load_json_from_file(file_path: str) -> dict:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Find JSON object starting with "artifactRelationships"
            if '"artifactRelationships":' in content:
                start_idx = content.find('"artifactRelationships":')
                # Find the opening bracket after the key
                start_obj = content.find('[', start_idx)
                # Find the matching closing bracket
                bracket_count = 1
                end_obj = start_obj + 1
                while bracket_count > 0 and end_obj < len(content):
                    if content[end_obj] == '[':
                        bracket_count += 1
                    elif content[end_obj] == ']':
                        bracket_count -= 1
                    end_obj += 1

                relationships_json = content[start_obj:end_obj]
                return {"artifactRelationships": json.loads(relationships_json)}
            else:
                return json.loads(content)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        # Return empty structure as fallback
        return {"artifactRelationships": []}

def build_dependency_graph(relationships: List[dict]) -> Tuple[nx.DiGraph, Set[str]]:
    """Build a directed graph from relationship data."""
    G = nx.DiGraph()

    # Collect all unique artifact IDs
    all_artifacts = set()

    for rel in relationships:
        parent = rel.get("parent")
        child = rel.get("child")
        rel_type = rel.get("type")

        if parent and child:
            G.add_edge(parent, child, type=rel_type)
            all_artifacts.add(parent)
            all_artifacts.add(child)

    return G, all_artifacts

def find_root_nodes(G: nx.DiGraph) -> List[str]:
    """Find nodes with no incoming edges (root nodes)."""
    return [node for node in G.nodes() if G.in_degree(node) == 0]

def find_leaf_nodes(G: nx.DiGraph) -> List[str]:
    """Find nodes with no outgoing edges (leaf nodes)."""
    return [node for node in G.nodes() if G.out_degree(node) == 0]

def get_transitive_dependencies(G: nx.DiGraph, node: str) -> Set[str]:
    """Get all downstream dependencies (transitive closure)."""
    if node not in G:
        return set()

    # Get all reachable nodes from the current node
    return set(nx.descendants(G, node))

def calculate_dependency_stats(G: nx.DiGraph) -> Dict[str, dict]:
    """Calculate dependency statistics for each node."""
    stats = {}

    for node in G.nodes():
        direct_deps = list(G.successors(node))
        transitive_deps = get_transitive_dependencies(G, node)

        # Include relationship types for direct dependencies
        direct_deps_with_types = {
            dep: G.edges[node, dep].get('type', 'unknown')
            for dep in direct_deps if (node, dep) in G.edges
        }

        stats[node] = {
            "direct_dependencies": len(direct_deps),
            "direct_dependencies_list": direct_deps_with_types,
            "transitive_dependencies": len(transitive_deps),
            "total_dependencies": len(transitive_deps) + len(direct_deps)
        }

    return stats

def print_tree(G: nx.DiGraph, node: str, seen: Optional[Set[str]] = None, depth: int = 0, max_depth: int = None):
    """Print the dependency tree in a hierarchical format."""
    if seen is None:
        seen = set()

    if node in seen:
        print("  " * depth + f"└── {node} (cyclic reference)")
        return

    if max_depth is not None and depth > max_depth:
        print("  " * depth + "└── ...")
        return

    seen.add(node)

    # Get successors (children)
    successors = list(G.successors(node))

    if depth == 0:
        print(f"{node}")

    for i, child in enumerate(successors):
        is_last = i == len(successors) - 1
        edge_type = G.edges[node, child].get('type', '')

        prefix = "└── " if is_last else "├── "
        print("  " * depth + prefix + f"{child} ({edge_type})")

        # Recursively print the children with increased depth
        if child not in seen:
            next_prefix = "    " if is_last else "│   "
            print_tree(G, child, seen.copy(), depth + 1, max_depth)

def analyze_relationships(relationships: List[dict], print_stats: bool = True, visualize: bool = False):
    """Analyze artifact relationships."""
    # Build the graph
    G, all_artifacts = build_dependency_graph(relationships)

    # Find root and leaf nodes
    roots = find_root_nodes(G)
    leaves = find_leaf_nodes(G)

    # Calculate dependency statistics
    stats = calculate_dependency_stats(G)

    # Print basic information
    print(f"Total artifacts: {len(all_artifacts)}")
    print(f"Total relationships: {len(relationships)}")
    print(f"Root nodes: {len(roots)}")
    print(f"Leaf nodes: {len(leaves)}")

    # Get the most common node that is a child
    if G.nodes():
        most_common_child = max(G.nodes(), key=lambda n: G.in_degree(n))
        print(f"Most referenced artifact (highest in-degree): {most_common_child} ({G.in_degree(most_common_child)} references)")

    # Find the node with most dependencies
    if stats:
        node_with_most_deps = max(stats.keys(), key=lambda n: stats[n]["total_dependencies"])
        print(f"Artifact with most dependencies: {node_with_most_deps} ({stats[node_with_most_deps]['total_dependencies']} total deps)")

    # Print dependency trees for root nodes
    print("\nDependency Trees (max depth 3):")
    for root in sorted(roots)[:5]:  # Limit to first 5 roots to avoid excessive output
        print("\n" + "=" * 50)
        print(f"Tree for {root}:")
        print("=" * 50)
        print_tree(G, root, max_depth=3)

    if len(roots) > 5:
        print(f"\n... and {len(roots) - 5} more root nodes")

    # Calculate and print additional statistics
    if print_stats:
        print("\nDetailed Statistics:")
        print("-" * 50)

        # Sort nodes by total dependencies
        top_nodes = sorted(stats.keys(), key=lambda n: stats[n]["total_dependencies"], reverse=True)
        for node in top_nodes[:10]:  # Show top 10
            deps = stats[node]
            print(f"Node: {node}")
            print(f"  Direct dependencies: {deps['direct_dependencies']}")
            print(f"  Transitive dependencies: {deps['transitive_dependencies']}")
            print(f"  Total dependencies: {deps['total_dependencies']}")
            print("-" * 30)

    # Visualize the graph if requested
    if visualize and len(G) <= 100:  # Only visualize if not too large
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.3)
        nx.draw(G, pos, node_size=50, node_color="lightblue",
                with_labels=False, arrows=True, edge_color="gray", alpha=0.7)

        # Add labels for important nodes
        important_nodes = set(roots) | set([most_common_child, node_with_most_deps])
        label_dict = {node: node for node in important_nodes if node in pos}
        nx.draw_networkx_labels(G, pos, labels=label_dict, font_size=8)

        plt.title("Artifact Dependency Graph")
        plt.savefig("dependency_graph.png")
        print("\nGraph visualization saved as 'dependency_graph.png'")

    return G, stats

def find_dependency_path(G: nx.DiGraph, source: str, target: str):
    """Find the shortest dependency path between two artifacts."""
    if source not in G or target not in G:
        print(f"Error: One or both nodes not in graph ({source}, {target})")
        return None

    try:
        path = nx.shortest_path(G, source=source, target=target)
        print(f"\nPath from {source} to {target}:")
        for i in range(len(path) - 1):
            edge_type = G.edges[path[i], path[i+1]].get('type', 'unknown')
            print(f"  {path[i]} --({edge_type})--> {path[i+1]}")
        return path
    except nx.NetworkXNoPath:
        print(f"No path exists from {source} to {target}")
        return None

def main():
    # Either load from file or use the data provided in the question
    # Uncomment below if loading from file
    # file_path = "artifact_relationships.json"
    # data = load_json_from_file(file_path)

    # For demonstration, using a sample of the data
    data = {"artifactRelationships": [
    {
      "parent": "0145c1e6b0f02c2d",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "01d641da856fe3f9",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "0347c7be911f3520",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "043ddd85ae3164c0",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "0e3b3c440a9e0545",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "10cd28efc9f3885d",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "112d602ab58140ea",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "26d2284bf40226ae",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "2a7cfd5e62869a92",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "2b197e85ad8f17f9",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "2eab38f29227869d",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "30a4d4e733bfa714",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "317fb941ea652a28",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "33aa78f240636d66",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "3778a520401413a1",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "3935a3be2f4df533",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "3c88b1bf4599e259",
      "child": "28c718f924e0e3af",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "405ac3d6d0774f19",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "48c270f398b09868",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "496c1458d40975bb",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "4a50e530279cb6cd",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "4efdcd40b4e43970",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "52689b032fbd4294",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "53cee23074ad4b56",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "5ff94df7bb0badc4",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "660597430844770a",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "66b8f9c98051139b",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "6f7347c7ea019fdd",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "735ab323bad274ce",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "7ab7ca7d06e29f15",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "7c3099e157ddd1f5",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "7c6def6506b258b9",
      "child": "70e7071acbb8d0c2",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "81b5f6af25fd1089",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "821626b44fb40938",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "8c7766766985c8fd",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "8fbbbbea5a9cd136",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "94c6b30301562d90",
      "child": "a59c06faa8b1f418",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "95cf3195a4d8b148",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "9d146fa07a750edc",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "9dd6a1a34218a260",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a0be324a1c0e15c3",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a10e454919a4c09f",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a16e82d5cb597ae7",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a1d8ab19684169f0",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a51b2638f84ec18b",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "a7a14ee0a9500f76",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "aafcbcaf56e03b8a",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "ab824a8a391dfd16",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "acc156f9bb5a1f1d",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "ae8ec1a521d00b87",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b2075aff0360673d",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b3f638216c2f61e1",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b42871a73b9c207a",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b4cd8266cd71aff7",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b54bfb1da26ce9cd",
      "child": "a59c06faa8b1f418",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b617d6fecb41ed82",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b642793aeb569fa4",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "b7d5eae5bf613d57",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "ba0db63f1ea1d49c",
      "child": "28c718f924e0e3af",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "bb257c6bf89503bf",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "bb87ae5a83c7a94a",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "bd900f9f6bb9f6dd",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "c3a9c5c16c619f8f",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "c3e5bf5c3a82ef73",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "c45383f7269d67c6",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "ca02cb5b63f659a9",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "cb19a97cb588c57f",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "cbcd08d5323cf7ab",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "cbf693155383c51f",
      "child": "a59c06faa8b1f418",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "0145c1e6b0f02c2d",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "01d641da856fe3f9",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "0347c7be911f3520",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "043ddd85ae3164c0",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "0e3b3c440a9e0545",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "10cd28efc9f3885d",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "112d602ab58140ea",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "26d2284bf40226ae",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "2a7cfd5e62869a92",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "2b197e85ad8f17f9",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "2eab38f29227869d",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "30a4d4e733bfa714",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "317fb941ea652a28",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "33aa78f240636d66",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "3778a520401413a1",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "3935a3be2f4df533",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "3c88b1bf4599e259",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "405ac3d6d0774f19",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "48c270f398b09868",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "496c1458d40975bb",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "4a50e530279cb6cd",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "4efdcd40b4e43970",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "52689b032fbd4294",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "53cee23074ad4b56",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "5ff94df7bb0badc4",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "660597430844770a",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "66b8f9c98051139b",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "6f7347c7ea019fdd",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "735ab323bad274ce",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "7ab7ca7d06e29f15",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "7c3099e157ddd1f5",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "7c6def6506b258b9",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "81b5f6af25fd1089",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "821626b44fb40938",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "8c7766766985c8fd",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "8fbbbbea5a9cd136",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "94c6b30301562d90",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "95cf3195a4d8b148",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "9d146fa07a750edc",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "9dd6a1a34218a260",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a0be324a1c0e15c3",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a10e454919a4c09f",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a16e82d5cb597ae7",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a1d8ab19684169f0",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a51b2638f84ec18b",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "a7a14ee0a9500f76",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "aafcbcaf56e03b8a",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "ab824a8a391dfd16",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "acc156f9bb5a1f1d",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "ae8ec1a521d00b87",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b2075aff0360673d",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b3f638216c2f61e1",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b42871a73b9c207a",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b4cd8266cd71aff7",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b54bfb1da26ce9cd",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b617d6fecb41ed82",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b642793aeb569fa4",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "b7d5eae5bf613d57",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "ba0db63f1ea1d49c",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "bb257c6bf89503bf",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "bb87ae5a83c7a94a",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "bd900f9f6bb9f6dd",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "c3a9c5c16c619f8f",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "c3e5bf5c3a82ef73",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "c45383f7269d67c6",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "ca02cb5b63f659a9",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "cb19a97cb588c57f",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "cbcd08d5323cf7ab",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "cbf693155383c51f",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "cf5d35c026fc9352",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "cfb05003ba72ba14",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "d015daceb06d0f5e",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "d1f542d648442f35",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "d6c8f66bff72bd07",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "da1dfd004a1f39a5",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "da3a65b9745222ee",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "de6527b74c32bd7a",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "df1911a910d9f7a1",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "e40a6fe56787c834",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "e54092627467ee5f",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "e91aeae8489114c8",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "eeb72248c9c0b4e7",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f2ee8c8a3e9d23fb",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f3631fa5803bf0f4",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f56f49dcec376cbb",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f7417cb457591620",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f7f4920fad4045f0",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "f8baec98e8544766",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "fd10fce47017fa13",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "fedc097e3e8886f4",
      "type": "contains"
    },
    {
      "parent": "cdb4ee2aea69cc6a83331bbe96dc2caa9a299d21329efb0336fc02a82e1839a8",
      "child": "fef92f985714ca65",
      "type": "contains"
    },
    {
      "parent": "cf5d35c026fc9352",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "cfb05003ba72ba14",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "d015daceb06d0f5e",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "d1f542d648442f35",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "d6c8f66bff72bd07",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "da1dfd004a1f39a5",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "da3a65b9745222ee",
      "child": "28c718f924e0e3af",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "de6527b74c32bd7a",
      "child": "7eee1dce79d34bd0",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "df1911a910d9f7a1",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "e40a6fe56787c834",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "e54092627467ee5f",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "e91aeae8489114c8",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "eeb72248c9c0b4e7",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f2ee8c8a3e9d23fb",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f3631fa5803bf0f4",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f56f49dcec376cbb",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f7417cb457591620",
      "child": "70e7071acbb8d0c2",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f7f4920fad4045f0",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "f8baec98e8544766",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "fd10fce47017fa13",
      "child": "7eee1dce79d34bd0",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "fedc097e3e8886f4",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    },
    {
      "parent": "fef92f985714ca65",
      "child": "fd71c2238fc07657",
      "type": "evident-by",
      "metadata": { "kind": "primary" }
    }
  ]}

    # Analyze the relationships
    print("Analyzing artifact relationships...")
    G, stats = analyze_relationships(data["artifactRelationships"])

    # Interactive exploration (uncomment to use)
    print("\nInteractive Exploration:")
    while True:
        print("\nOptions:")
        print("1. Find path between two artifacts")
        print("2. Show all dependencies for an artifact")
        print("3. Show all artifacts that depend on a specific artifact")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            source = input("Enter source artifact ID: ")
            target = input("Enter target artifact ID: ")
            find_dependency_path(G, source, target)

        elif choice == '2':
            artifact = input("Enter artifact ID: ")
            if artifact in G:
                deps = list(G.successors(artifact))
                print(f"\nDirect dependencies of {artifact} ({len(deps)}):")
                for dep in deps:
                    edge_type = G.edges[artifact, dep].get('type', 'unknown')
                    print(f"  {dep} (type: {edge_type})")

                trans_deps = get_transitive_dependencies(G, artifact)
                print(f"\nTransitive dependencies ({len(trans_deps)}):")
                for i, dep in enumerate(list(trans_deps)[:20]):  # Show only first 20
                    print(f"  {dep}")
                if len(trans_deps) > 20:
                    print(f"  ... and {len(trans_deps) - 20} more")
            else:
                print(f"Artifact {artifact} not found")

        elif choice == '3':
            artifact = input("Enter artifact ID: ")
            if artifact in G:
                dependents = list(G.predecessors(artifact))
                print(f"\nArtifacts directly depending on {artifact} ({len(dependents)}):")
                for dep in dependents:
                    edge_type = G.edges[dep, artifact].get('type', 'unknown')
                    print(f"  {dep} (type: {edge_type})")
            else:
                print(f"Artifact {artifact} not found")

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()