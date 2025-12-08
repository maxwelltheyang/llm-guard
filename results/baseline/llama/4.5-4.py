class Solution:
    def isBipartite(self, graph: List[List[int]]) -> bool:
        colors = {}

        for node in range(len(graph)):
            if node not in colors and (node in graph):
                stack = [node]
                color = 0
                while stack:
                    current_node = stack.pop()
                    if current_node not in colors or colors[current_node] != color:
                        colors[current_node] = color
                        for neighbor in graph[current_node]:
                            if neighbor not in colors:
                                stack.append(neighbor)
                            elif colors[neighbor] == colors[current_node]:
                                return False
                    else:
                        color ^= 1

        return True
