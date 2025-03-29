import pygame
import sys
from robot_class import Robot

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Robot Pathfinding")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Grid settings
GRID_SIZE = 32
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE

# Create grid (0 = free space, 1 = obstacle)
grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

# Add some example obstacles
for x in range(5, 8):
    for y in range(4, 7):
        grid[x][y] = 1

# Create robot
robot = Robot(GRID_SIZE, GRID_SIZE)  # Start at (1, 1) in grid coordinates

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Set new target for robot
            mouse_pos = pygame.mouse.get_pos()
            robot.move_to(mouse_pos, grid)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Place/remove obstacle at mouse position
                mouse_pos = pygame.mouse.get_pos()
                grid_x = mouse_pos[0] // GRID_SIZE
                grid_y = mouse_pos[1] // GRID_SIZE
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    grid[grid_x][grid_y] = 1 - grid[grid_x][grid_y]  # Toggle obstacle

    # Update
    robot.update()

    # Draw
    screen.fill(WHITE)

    # Draw grid and obstacles
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if grid[x][y] == 1:  # Obstacle
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines

    # Draw robot and path
    robot.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
