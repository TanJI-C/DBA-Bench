"""ExperienceGraph - Paper Section 4.

Heterogeneous directed graph G = (V, E, R) for encoding O&M experience.
6 vertex types, 4 edge types. Loaded from JSON.
"""

import json
from collections import defaultdict
from typing import Dict, List, Optional, Set

from src.agents.baselines.dbaiops.types import DiagnosticPath, GraphEdge, GraphNode


class ExperienceGraph:
    """Paper Section 4: heterogeneous O&M graph model."""

    def __init__(self, graph_path: Optional[str] = None):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._outgoing: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._incoming: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._nodes_by_type: Dict[str, List[str]] = defaultdict(list)
        self._tag_members: Dict[str, Set[str]] = defaultdict(set)

        if graph_path:
            self.load(graph_path)

    def load(self, path: str):
        """Load graph from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for node_data in data.get("nodes", []):
            node = GraphNode(
                id=node_data["id"],
                type=node_data["type"],
                name=node_data["name"],
                content=node_data.get("content", ""),
                attributes=node_data.get("attributes", {}),
            )
            self.nodes[node.id] = node
            self._nodes_by_type[node.type].append(node.id)

        for edge_data in data.get("edges", []):
            edge = GraphEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                type=edge_data["type"],
                attributes=edge_data.get("attributes", {}),
            )
            self.edges.append(edge)
            self._outgoing[edge.source].append(edge)
            self._incoming[edge.target].append(edge)

        # Build tag membership index
        for edge in self.edges:
            src = self.nodes.get(edge.source)
            tgt = self.nodes.get(edge.target)
            if src and src.type == "tag":
                self._tag_members[src.id].add(edge.target)
            if tgt and tgt.type == "tag":
                self._tag_members[tgt.id].add(edge.source)

    # --- Section 4.1: Graph traversal ---

    def get_trigger_vertices(self) -> List[GraphNode]:
        """Get all trigger vertices."""
        return [self.nodes[nid] for nid in self._nodes_by_type.get("trigger", [])]

    def get_nodes_by_type(self, node_type: str) -> List[GraphNode]:
        return [self.nodes[nid] for nid in self._nodes_by_type.get(node_type, [])]

    def get_neighbors(self, node_id: str,
                      edge_type: Optional[str] = None) -> List[GraphNode]:
        """Get outgoing neighbors, optionally filtered by edge type."""
        results = []
        for edge in self._outgoing.get(node_id, []):
            if edge_type and edge.type != edge_type:
                continue
            if edge.target in self.nodes:
                results.append(self.nodes[edge.target])
        return results

    def get_incoming_neighbors(self, node_id: str,
                               edge_type: Optional[str] = None) -> List[GraphNode]:
        """Get incoming neighbors."""
        results = []
        for edge in self._incoming.get(node_id, []):
            if edge_type and edge.type != edge_type:
                continue
            if edge.source in self.nodes:
                results.append(self.nodes[edge.source])
        return results

    # --- Section 6.1: Graph evolution ---

    def find_overlapping_models(self, trigger_id: str) -> List[str]:
        """Proximity Discovery: find other trigger vertices sharing Tag/Metric nodes."""
        shared_nodes: Set[str] = set()
        # Collect all tags and metrics connected to this trigger
        for neighbor in self.get_neighbors(trigger_id):
            if neighbor.type in ("tag", "metric"):
                shared_nodes.add(neighbor.id)
        # Also check containment edges
        for neighbor in self.get_neighbors(trigger_id, "containment"):
            for n2 in self.get_neighbors(neighbor.id):
                if n2.type in ("tag", "metric"):
                    shared_nodes.add(n2.id)

        # Find other triggers connected to the same tags/metrics
        overlapping = []
        for other_trigger_id in self._nodes_by_type.get("trigger", []):
            if other_trigger_id == trigger_id:
                continue
            for neighbor in self.get_neighbors(other_trigger_id):
                if neighbor.id in shared_nodes:
                    overlapping.append(other_trigger_id)
                    break
        return overlapping

    def create_cross_edge(self, source_id: str, target_id: str,
                          edge_type: str = "relevance") -> Optional[GraphEdge]:
        """Dynamically create cross-subgraph edge (graph evolution core)."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        # Avoid duplicates
        for edge in self._outgoing.get(source_id, []):
            if edge.target == target_id and edge.type == edge_type:
                return None
        edge = GraphEdge(
            source=source_id, target=target_id, type=edge_type,
            attributes={"dynamic": True},
        )
        self.edges.append(edge)
        self._outgoing[source_id].append(edge)
        self._incoming[target_id].append(edge)
        return edge

    def get_diagnosis_paths(self, trigger_id: str,
                            max_depth: int = 4) -> List[DiagnosticPath]:
        """BFS from trigger: trigger → tag → experience → metric → tool."""
        if trigger_id not in self.nodes:
            return []

        paths: List[DiagnosticPath] = []
        queue = [(trigger_id, [self.nodes[trigger_id]], [])]
        visited_paths: Set[str] = set()

        while queue:
            current_id, node_path, edge_path = queue.pop(0)
            if len(node_path) > max_depth:
                continue

            for edge in self._outgoing.get(current_id, []):
                if edge.target in {n.id for n in node_path}:
                    continue
                target_node = self.nodes.get(edge.target)
                if not target_node:
                    continue

                new_nodes = node_path + [target_node]
                new_edges = edge_path + [edge]
                path_key = "->".join(n.id for n in new_nodes)

                if path_key not in visited_paths:
                    visited_paths.add(path_key)
                    path = DiagnosticPath(nodes=new_nodes, edges=new_edges)
                    # A path is complete if it reaches a tool or experience node
                    if target_node.type in ("tool", "experience", "metric"):
                        paths.append(path)
                    queue.append((edge.target, new_nodes, new_edges))

        return paths

