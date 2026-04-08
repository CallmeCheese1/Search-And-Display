class VisualizationTree:
    def __init__(self, root_node):
        self.root = root_node

        #Eventually, this will hold the entire tree, with parents and children.
        self.edges = []
        self._edges_set = set()
    
    def add_edge(self, parent_node, child_node):
        edge = (parent_node, child_node)
        if edge not in self._edges_set:
            self._edges_set.add(edge)
            self.edges.append(edge)
    
    def __str__(self):
        """String representation of the visualization tree for printing."""
        result = f"VisualizationTree:\n"
        result += f"  Root: {self.root}\n"
        result += f"  Edges: {len(self.edges)}\n"
        
        if self.edges:
            result += "  Tree Structure:\n"
            for i, (parent, child) in enumerate(self.edges):
                result += f"    {i+1}. {parent} -> {child}\n"
        else:
            result += "  No edges yet\n"
        
        return result
    