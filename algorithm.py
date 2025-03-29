import heapq
import math
from typing import List, Tuple, Dict

class Algorithm:
    def __init__(self):
        # 8-directional movement: horizontal, vertical, and diagonal
        self.directions = [
            (0, 1),   # right
            (1, 0),   # down
            (0, -1),  # left
            (-1, 0),  # up
            (1, 1),   # down-right
            (-1, 1),  # up-right
            (1, -1),  # down-left
            (-1, -1)  # up-left
        ]

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic"""
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_neighbors(self, pos: Tuple[int, int], grid: List[List[int]]) -> List[Tuple[int, int]]:
        """Returns valid neighboring positions"""
        neighbors = []
        for dx, dy in self.directions:
            new_x, new_y = pos[0] + dx, pos[1] + dy
            
            # Check if position is within grid bounds and not an obstacle
            if (0 <= new_x < len(grid) and 
                0 <= new_y < len(grid[0]) and 
                grid[new_x][new_y] != 1):
                
                # For diagonal movements, check if both adjacent cells are free
                if dx != 0 and dy != 0:
                    if grid[pos[0]][pos[1] + dy] == 1 or grid[pos[0] + dx][pos[1]] == 1:
                        continue  # Skip if diagonal movement is blocked
                
                neighbors.append((new_x, new_y))
        return neighbors

    def get_movement_cost(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> float:
        """Calculate movement cost between adjacent cells"""
        dx = abs(current[0] - next_pos[0])
        dy = abs(current[1] - next_pos[1])
        
        # Diagonal movement costs sqrt(2), orthogonal movement costs 1
        return math.sqrt(2) if dx == 1 and dy == 1 else 1.0

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  grid: List[List[int]]) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm using Euclidean distance"""
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
                new_cost = cost_so_far[current] + self.get_movement_cost(current, next_pos)

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruct path
        current = goal
        path = []
        
        # If goal was never reached, return empty path
        if goal not in came_from:
            return []
            
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        
        path.reverse()
        return path

    def smooth_path(self, path: List[Tuple[int, int]], grid: List[List[int]]) -> List[Tuple[int, int]]:
        """Optional: Smooth the path to make it more natural"""
        if len(path) < 3:
            return path

        smoothed = [path[0]]
        current_idx = 0

        while current_idx < len(path) - 1:
            # Look ahead as far as possible for direct line of sight
            for look_ahead in range(len(path) - 1, current_idx, -1):
                if self.has_line_of_sight(path[current_idx], path[look_ahead], grid):
                    smoothed.append(path[look_ahead])
                    current_idx = look_ahead
                    break
            current_idx += 1

        return smoothed

    def has_line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int], 
                         grid: List[List[int]]) -> bool:
        """Check if there's a clear line of sight between two points"""
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        for _ in range(n):
            if grid[int(x)][int(y)] == 1:
                return False
                
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx

        return True
