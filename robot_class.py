import pygame
import numpy as np
import heapq

class Robot:
    def __init__(self, speed, width=20, height=20):
        self.robot = pygame.Rect(0, 0, width, height)
        self.speed = speed
        self.path = []
        self.route_points = []
        self.target = None
        self.current_segment = 0
        self.movement_type = "terrain"  # Default to terrain-based pathfinding
        self.distance_threshold = 100
        self.terrain_data = None  # Will store the terrain data
        self.terrain_grid = None  # Will store processed grid
        self.terrain_width = 0
        self.terrain_height = 0

    def load_terrain_data(self, filename):
        """Load terrain data from file and process it"""
        terrain_rows = []
        with open(filename, 'r') as file:
            for line in file:
                row = [int(val) for val in line.split()]
                terrain_rows.append(row)
        
        self.terrain_data = np.array(terrain_rows)
        self.terrain_height, self.terrain_width = self.terrain_data.shape
        print(f"Loaded terrain with dimensions: {self.terrain_width}x{self.terrain_height}")
        
    def find_path(self, target_pos):
        self.target = target_pos
        self.current_segment = 0
        
        # Calculate distance to target
        dx = target_pos[0] - self.robot.centerx
        dy = target_pos[1] - self.robot.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Choose movement type based on distance
        if distance < self.distance_threshold:
            self.movement_type = "euclidean"
            self.update_route_points()
        else:
            # Use optimal path through terrain
            self.movement_type = "terrain"
            self.find_terrain_path(target_pos)

    def find_terrain_path(self, target_pos):
        """Find optimal path using terrain data"""
        if self.terrain_data is None:
            # Fallback to manhattan if no terrain data
            self.movement_type = "manhattan"
            self.update_route_points()
            return
            
        # Convert screen positions to terrain grid indices
        start_x, start_y = self.robot.centerx, self.robot.centery
        target_x, target_y = target_pos
        
        # Scale coordinates to match terrain grid
        start_grid_x = min(int(start_x * self.terrain_width / pygame.display.get_surface().get_width()), self.terrain_width - 1)
        start_grid_y = min(int(start_y * self.terrain_height / pygame.display.get_surface().get_height()), self.terrain_height - 1)
        target_grid_x = min(int(target_x * self.terrain_width / pygame.display.get_surface().get_width()), self.terrain_width - 1)
        target_grid_y = min(int(target_y * self.terrain_height / pygame.display.get_surface().get_height()), self.terrain_height - 1)
        
        # Use A* to find path
        path = self.a_star_search((start_grid_y, start_grid_x), (target_grid_y, target_grid_x))
        
        if path:
            # Convert grid path back to screen coordinates
            screen_width = pygame.display.get_surface().get_width()
            screen_height = pygame.display.get_surface().get_height()
            
            self.route_points = []
            # Start with current robot position
            self.route_points.append((self.robot.centerx, self.robot.centery))
            
            # Add all path points (skip first since it's the start)
            for grid_y, grid_x in path[1:]:
                screen_x = int(grid_x * screen_width / self.terrain_width)
                screen_y = int(grid_y * screen_height / self.terrain_height)
                self.route_points.append((screen_x, screen_y))
            
            # Set path for movement
            self.path = self.route_points.copy()
            self.current_segment = 1  # Start at first segment (after start point)
        else:
            # Fallback to manhattan if no path found
            self.movement_type = "manhattan"
            self.update_route_points()

    def a_star_search(self, start, goal):
        """A* pathfinding algorithm using terrain data as cost map"""
        # Higher values = better path (lower cost)
        max_value = np.max(self.terrain_data)
        
        # Priority queue for A*
        open_set = [(0, 0, start, [])]  # (f_score, g_score, position, path)
        closed_set = set()
        
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
                
            new_path = path + [current]
            
            if current == goal:
                return new_path
                
            closed_set.add(current)
            
            # Check all 8 neighbors
            for dy, dx in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                ny, nx = current[0] + dy, current[1] + dx
                
                # Check boundaries
                if 0 <= ny < self.terrain_height and 0 <= nx < self.terrain_width:
                    if (ny, nx) not in closed_set:
                        # Cost is inverse of terrain value (higher values = better paths)
                        # Add a small base cost for each move
                        terrain_value = self.terrain_data[ny, nx]
                        move_cost = 1.0 - (terrain_value / max_value)
                        
                        # Diagonal moves cost more
                        if dx != 0 and dy != 0:
                            move_cost *= 1.414
                            
                        new_g = g + move_cost + 0.1  # Add small base cost
                        
                        # Heuristic (Euclidean distance)
                        h = ((ny - goal[0]) ** 2 + (nx - goal[1]) ** 2) ** 0.5
                        f = new_g + h
                        
                        heapq.heappush(open_set, (f, new_g, (ny, nx), new_path))
        
        return None  # No path found

    def update_route_points(self):
        if self.target:
            start_pos = (self.robot.centerx, self.robot.centery)
            if self.movement_type == "manhattan":
                self.route_points = [
                    start_pos,
                    (start_pos[0], self.target[1]),  # Vertical line
                    self.target  # Horizontal to target
                ]
                self.path = self.route_points.copy()
                self.current_segment = 1
            elif self.movement_type == "euclidean":
                self.route_points = [
                    start_pos,
                    self.target
                ]
                self.path = self.route_points.copy()
                self.current_segment = 1

    def update(self):
        if not self.target or not self.path:
            return

        try:
            if self.movement_type == "terrain" or self.movement_type == "euclidean":
                # For both terrain and euclidean, we follow waypoints directly
                if self.current_segment < len(self.path):
                    current_pos = (self.robot.centerx, self.robot.centery)
                    target_pos = self.path[self.current_segment]
                    
                    dx = target_pos[0] - current_pos[0]
                    dy = target_pos[1] - current_pos[1]
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    
                    if distance < self.speed:
                        # Reached this waypoint, move to next
                        self.robot.x = target_pos[0] - self.robot.width // 2
                        self.robot.y = target_pos[1] - self.robot.height // 2
                        self.current_segment += 1
                        
                        # If we're at the end of the path
                        if self.current_segment >= len(self.path):
                            self.target = None
                            return
                    else:
                        # Move toward waypoint
                        move_x = (dx / distance) * self.speed
                        move_y = (dy / distance) * self.speed
                        self.robot.x += move_x
                        self.robot.y += move_y
            
            elif self.movement_type == "manhattan":
                # Manhattan movement
                if self.current_segment == 1:
                    # Move vertically first
                    current_pos = (self.robot.centerx, self.robot.centery)
                    target_y = self.path[1][1]
                    
                    if abs(current_pos[1] - target_y) > self.speed:
                        if current_pos[1] < target_y:
                            self.robot.y += self.speed
                        else:
                            self.robot.y -= self.speed
                    else:
                        self.robot.y = target_y - self.robot.height // 2
                        self.current_segment = 2
                
                elif self.current_segment == 2:
                    # Move horizontally
                    current_pos = (self.robot.centerx, self.robot.centery)
                    target_x = self.path[2][0]
                    
                    if abs(current_pos[0] - target_x) > self.speed:
                        if current_pos[0] < target_x:
                            self.robot.x += self.speed
                        else:
                            self.robot.x -= self.speed
                    else:
                        self.robot.x = target_x - self.robot.width // 2
                        self.target = None
                        return

        except (IndexError, ValueError):
            self.path = []
            self.route_points = []
            self.target = None
