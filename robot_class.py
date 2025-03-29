# robot_class.py
import pygame
from algorithm import Algorithm

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.robot = pygame.Rect(x, y, 20, 20)
        self.algorithm = Algorithm()
        self.current_path = []
        self.current_waypoint = 0
        self.has_path = False
        self.target = None
        self.waypoints = []
        self.current_target_index = 0

    def set_waypoints(self, points, grid):
        """Set the list of grid points for the robot to visit"""
        self.waypoints = points
        self.current_target_index = 0
        self.recalculate_path_from_current(grid)

    def recalculate_path_from_current(self, grid):
        """Recalculate path from current position to target"""
        if self.current_target_index < len(self.waypoints):
            current_pos = (int(self.x // 32), int(self.y // 32))
            target = self.waypoints[self.current_target_index]
            
            # If we're already at the target, move to next waypoint
            if current_pos == target:
                self.current_target_index += 1
                if self.current_target_index < len(self.waypoints):
                    target = self.waypoints[self.current_target_index]
                else:
                    self.has_path = False
                    return

            # Calculate new path from current position
            new_path = self.algorithm.find_path(current_pos, target, grid)
            
            if new_path:
                self.current_path = new_path
                self.current_waypoint = 0
                self.has_path = True
            else:
                # If no path found, keep trying from current position
                self.has_path = False

    def update(self, grid):
        """Update robot position"""
        if self.has_path and self.current_waypoint < len(self.current_path):
            # Convert grid coordinates to pixel coordinates
            target_x = self.current_path[self.current_waypoint][0] * 32 + 16
            target_y = self.current_path[self.current_waypoint][1] * 32 + 16

            # Calculate direction
            dx = target_x - self.x
            dy = target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < self.speed:
                self.current_waypoint += 1
                if self.current_waypoint >= len(self.current_path):
                    # Reached current target, move to next waypoint
                    self.current_target_index += 1
                    self.recalculate_path_from_current(grid)
            else:
                # Normalize movement
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Update position
                self.x += dx
                self.y += dy
                self.robot.x = self.x
                self.robot.y = self.y

    def handle_obstacle_change(self, grid):
        """Handle obstacle changes by recalculating path from current position"""
        self.recalculate_path_from_current(grid)

    def draw(self, screen):
        """Draw robot, path, and waypoints"""
        # Draw path
        if self.has_path:
            for i in range(len(self.current_path) - 1):
                start_pos = (self.current_path[i][0] * 32 + 16,
                           self.current_path[i][1] * 32 + 16)
                end_pos = (self.current_path[i+1][0] * 32 + 16,
                         self.current_path[i+1][1] * 32 + 16)
                pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)

        # Draw waypoints
        for i, point in enumerate(self.waypoints):
            color = (0, 0, 255) if i >= self.current_target_index else (100, 100, 100)
            pygame.draw.circle(screen, color, 
                             (point[0] * 32 + 16, point[1] * 32 + 16), 5)

        # Draw robot
        pygame.draw.rect(screen, (255, 0, 0), self.robot)
