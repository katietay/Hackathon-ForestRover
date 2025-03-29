# robot_class.py
import pygame
import math
from algorithm import Algorithm

class Robot:
    def __init__(self, x, y):
        print(f"Initializing Robot at position ({x}, {y})")
        self.x = x
        self.y = y
        self.grid_x = x // 32
        self.grid_y = y // 32
        self.speed = 2
        self.robot = pygame.Rect(x - 10, y - 10, 20, 20)
        self.algorithm = Algorithm()
        self.current_path = []
        self.current_waypoint = 0
        self.has_path = False
        self.waypoints = []
        self.current_target_index = 0
        self.current_elevation = 0
        self.current_slope = 0

    def set_waypoints(self, points, grid):
        print(f"Setting waypoints: {points}")
        self.waypoints = points
        # Start from the robot's current grid position
        current_pos = (self.grid_x, self.grid_y)
        print(f"Current grid position: {current_pos}")
        self.current_target_index = 0
        
        # Don't recalculate path if we're already at the first waypoint
        if current_pos != self.waypoints[0]:
            self.recalculate_path_from_current(grid)
        else:
            # If we're at the first waypoint, move to the second
            self.current_target_index = 1
            self.recalculate_path_from_current(grid)

    def recalculate_path_from_current(self, grid):
        if self.current_target_index < len(self.waypoints):
            current_pos = (self.grid_x, self.grid_y)
            target = self.waypoints[self.current_target_index]
            
            print(f"Calculating path from {current_pos} to {target}")
            
            new_path = self.algorithm.find_path(current_pos, target, grid)
            
            if new_path:
                print(f"Found path with {len(new_path)} points: {new_path}")
                self.current_path = new_path
                self.current_waypoint = 0
                self.has_path = True
            else:
                print(f"No path found from {current_pos} to {target}!")
                self.has_path = False
        else:
            print("Reached final waypoint, no more targets.")
            self.has_path = False

    def update(self, grid):
        if self.has_path and self.current_waypoint < len(self.current_path):
            # Get target position in grid coordinates
            target_grid = self.current_path[self.current_waypoint]
            # Convert to pixel coordinates (center of grid cell)
            target_x = target_grid[0] * 32 + 16
            target_y = target_grid[1] * 32 + 16

            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            print(f"Moving towards: {target_grid}, Distance: {distance}")
            print(f"Current position: ({self.x}, {self.y}), Target: ({target_x}, {target_y})")

            if distance > self.speed:
                # Normalize direction and apply speed
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Update position
                self.x += dx
                self.y += dy
                # Update grid position
                self.grid_x = int(self.x // 32)
                self.grid_y = int(self.y // 32)
                
                print(f"New position: ({self.x}, {self.y}), Grid: ({self.grid_x}, {self.grid_y})")
                
                self.robot = pygame.Rect(self.x - 10, self.y - 10, 20, 20)

                # Update elevation
                if 0 <= self.grid_x < grid.shape[0] and 0 <= self.grid_y < grid.shape[1]:
                    self.current_elevation = grid[self.grid_x, self.grid_y, 1]
                    
                    # Calculate slope if we have a previous point
                    if self.current_waypoint > 0:
                        prev_grid = self.current_path[self.current_waypoint - 1]
                        self.current_slope = self.algorithm.get_slope(prev_grid, target_grid, grid)
            else:
                print(f"Reached waypoint {self.current_waypoint}")
                self.current_waypoint += 1
                if self.current_waypoint >= len(self.current_path):
                    print(f"Completed path to target {self.current_target_index}")
                    self.current_target_index += 1
                    self.recalculate_path_from_current(grid)
        else:
            if not self.has_path:
                print("No valid path to follow")
            elif self.current_waypoint >= len(self.current_path):
                print(f"Reached end of current path segment")

    def draw(self, screen, grid, path_color=(255, 0, 0), robot_color=(0, 0, 255)):
        # Draw path with brighter color and thicker lines
        if self.has_path and len(self.current_path) > 1:
            for i in range(len(self.current_path) - 1):
                start_pos = (self.current_path[i][0] * 32 + 16,
                           self.current_path[i][1] * 32 + 16)
                end_pos = (self.current_path[i+1][0] * 32 + 16,
                          self.current_path[i+1][1] * 32 + 16)
                pygame.draw.line(screen, path_color, start_pos, end_pos, 3)  # Thicker line
                
                # Add dots at path points for better visibility
                pygame.draw.circle(screen, path_color, start_pos, 3)
            
            # Draw last point
            last_pos = (self.current_path[-1][0] * 32 + 16,
                       self.current_path[-1][1] * 32 + 16)
            pygame.draw.circle(screen, path_color, last_pos, 3)

        # Draw robot with customizable color
        pygame.draw.rect(screen, robot_color, self.robot)
        
        # Add a border around the robot for better visibility
        border = self.robot.copy()
        border.inflate_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0), border, 2)
        
        # Draw debug information with white background for better visibility
        font = pygame.font.Font(None, 24)
        
        # Create position text
        pos_text = font.render(f"Pos: ({int(self.x)}, {int(self.y)}) Grid: ({self.grid_x}, {self.grid_y})", True, (0, 0, 0))
        pos_rect = pos_text.get_rect(topleft=(10, 50))
        
        # Create background for position text
        bg_rect = pos_rect.copy()
        bg_rect.inflate_ip(10, 6)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
        
        # Display position text
        screen.blit(pos_text, pos_rect)

        # Display target information if we have a path
        if self.has_path and self.current_waypoint < len(self.current_path):
            target = self.current_path[self.current_waypoint]
            target_text = font.render(f"Target: {target}", True, (0, 0, 0))
            target_rect = target_text.get_rect(topleft=(10, 75))
            
            # Create background for target text
            bg_rect = target_rect.copy()
            bg_rect.inflate_ip(10, 6)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
            
            # Display target text
            screen.blit(target_text, target_rect)
            
    def draw_without_path(self, screen, grid, robot_color=(0, 0, 255)):
        """Draw only the robot without drawing the path"""
        # Draw robot with customizable color
        pygame.draw.rect(screen, robot_color, self.robot)
        
        # Add a border around the robot for better visibility
        border = self.robot.copy()
        border.inflate_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0), border, 2)
        
        # Draw debug information with white background for better visibility
        font = pygame.font.Font(None, 24)
        
        # Create position text
        pos_text = font.render(f"Pos: ({int(self.x)}, {int(self.y)}) Grid: ({self.grid_x}, {self.grid_y})", True, (0, 0, 0))
        pos_rect = pos_text.get_rect(topleft=(10, 50))
        
        # Create background for position text
        bg_rect = pos_rect.copy()
        bg_rect.inflate_ip(10, 6)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
        
        # Display position text
        screen.blit(pos_text, pos_rect)

    def handle_obstacle_change(self, grid):
        """Recalculate path when obstacles change"""
        self.recalculate_path_from_current(grid)