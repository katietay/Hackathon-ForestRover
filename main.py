# main.py
import pygame
import sys
from robot_class import Robot

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    WINDOW_SIZE = (800, 600)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Robot Pathfinding Test Case")

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

    # Create robot at starting position (2, 2)
    robot = Robot(2 * GRID_SIZE, 2 * GRID_SIZE)

    # Define start and end points
    waypoints = [
        (2, 2),     # Starting point (A)
        (18, 14),   # Ending point (B)
    ]

    # Set the waypoints for the robot
    robot.set_waypoints(waypoints, grid)

    # Game loop
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 36)

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Add/remove obstacle at clicked position
                mouse_pos = pygame.mouse.get_pos()
                grid_x = mouse_pos[0] // GRID_SIZE
                grid_y = mouse_pos[1] // GRID_SIZE
                if (grid_x, grid_y) not in waypoints:  # Don't place obstacles on waypoints
                    grid[grid_x][grid_y] = 1 - grid[grid_x][grid_y]  # Toggle obstacle
                    # Recalculate path from current position when obstacle is added/removed
                    robot.handle_obstacle_change(grid)

        # Update
        robot.update(grid)

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

        # Draw waypoint labels
        labels = ['A', 'B']
        for i, point in enumerate(waypoints):
            text = font.render(labels[i], True, (0, 0, 255))
            text_rect = text.get_rect(center=(point[0] * GRID_SIZE + 16, 
                                            point[1] * GRID_SIZE + 16))
            screen.blit(text, text_rect)

        # Draw instructions
        info_text = font.render("Click to add/remove obstacles", True, BLACK)
        screen.blit(info_text, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
