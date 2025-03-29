import heapq
from typing import List, Tuple, Dict

class Algorithm:
    def __init__(self):
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-directional movement

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic"""
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


    def get_neighbors(self, pos: Tuple[int, int], grid: List[List[int]]) -> List[Tuple[int, int]]:
        """Returns valid neighboring positions"""
        neighbors = []
        for dx, dy in self.directions:
            new_x, new_y = pos[0] + dx, pos[1] + dy
            
            if (0 <= new_x < len(grid) and 
                0 <= new_y < len(grid[0]) and 
                grid[new_x][new_y] != 1):  # Assuming 1 represents obstacles
                neighbors.append((new_x, new_y))
        return neighbors

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  grid: List[List[int]]) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm"""
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        cost_so_far: Dict[Tuple[int, int], float] = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next_pos in self.get_neighbors(current, grid):
                new_cost = cost_so_far[current] + 1

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruct path
        current = goal
        path = []
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        
        path.reverse()
        return path if path[0] == start else []
