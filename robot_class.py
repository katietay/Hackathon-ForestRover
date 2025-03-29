import pygame
from algorithm import Algorithm

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.robot = pygame.Rect(x, y, 20, 20)  # Adjust size as needed
        self.algorithm = Algorithm()
        self.current_path = []
        self.current_waypoint = 0
        self.has_path = False
        self.target = None

    def move_to(self, target_pos, grid):
        """Set new target and calculate path"""
        self.target = target_pos
        start = (int(self.x // 32), int(self.y // 32))  # Convert to grid coordinates
        target_grid = (int(target_pos[0] // 32), int(target_pos[1] // 32))
        self.current_path = self.algorithm.find_path(start, target_grid, grid)
        self.current_waypoint = 0
        self.has_path = len(self.current_path) > 0

    def update(self):
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
            else:
                # Normalize movement
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                # Update position
                self.x += dx
                self.y += dy
                self.robot.x = self.x
                self.robot.y = self.y

    def draw(self, screen):
        """Draw robot and path"""
        # Draw path
        if self.has_path:
            for i in range(len(self.current_path) - 1):
                start_pos = (self.current_path[i][0] * 32 + 16,
                           self.current_path[i][1] * 32 + 16)
                end_pos = (self.current_path[i+1][0] * 32 + 16,
                         self.current_path[i+1][1] * 32 + 16)
                pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)

        # Draw robot
        pygame.draw.rect(screen, (255, 0, 0), self.robot)
