import pygame
import pandas as pd
import tcod
import numpy as np
from math import sqrt

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
PATH_COLOR = (0, 255, 0)
ROBOT_COLOR = (255, 0, 0)
DESTINATION_COLOR = (0, 0, 255)
ROBOT_RADIUS = 5
DESTINATION_RADIUS = 8
SPEED = 2

# Create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robot Path Traversal")
clock = pygame.time.Clock()

# Load path from CSV
def load_path(csv_file):
    df = pd.read_csv(csv_file)
    path = [(int(row.x), int(row.y)) for _, row in df.iterrows()]
    return path

# Scale path to fit screen
def scale_path(path, padding=50):
    if not path:
        return []
        
    # Find min/max coordinates
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Calculate scale factors
    scale_x = (SCREEN_WIDTH - 2 * padding) / (max_x - min_x) if max_x > min_x else 1
    scale_y = (SCREEN_HEIGHT - 2 * padding) / (max_y - min_y) if max_y > min_y else 1
    scale = min(scale_x, scale_y)
    
    # Scale path
    scaled_path = []
    for x, y in path:
        scaled_x = padding + (x - min_x) * scale
        scaled_y = padding + (y - min_y) * scale
        scaled_path.append((scaled_x, scaled_y))
    
    return scaled_path

# Find closest point on path to given position
def find_closest_path_point(position, path):
    min_dist = float('inf')
    closest_index = 0
    
    for i, point in enumerate(path):
        dist = sqrt((position[0] - point[0])**2 + (position[1] - point[1])**2)
        if dist < min_dist:
            min_dist = dist
            closest_index = i
            
    return closest_index
# Add these new functions after your existing functions but before main()
def find_target_path_point(click_position, path):
    """
    Find the nearest point on path to clicked position and calculate shortest path
    """
    min_dist = float('inf')
    closest_index = 0
    closest_point = None
    
    # Find closest point on path to click position
    for i, point in enumerate(path):
        dist = sqrt((click_position[0] - point[0])**2 + 
                   (click_position[1] - point[1])**2)
        if dist < min_dist:
            min_dist = dist
            closest_index = i
            closest_point = point
            
    return closest_index, closest_point, min_dist
def find_shortest_path(path, start_index, end_index):
    """
    Determine the shortest direction to traverse the path
    Returns the path points in the correct order
    """
    # Get path length in both directions
    forward_path = path[start_index:end_index + 1]
    backward_path = path[end_index:start_index - 1:-1] if start_index > 0 else path[end_index::-1]
    
    # Calculate total distance for both directions
    def calculate_path_distance(path_points):
        distance = 0
        for i in range(len(path_points) - 1):
            dx = path_points[i+1][0] - path_points[i][0]
            dy = path_points[i+1][1] - path_points[i][1]
            distance += sqrt(dx**2 + dy**2)
        return distance
    
    forward_distance = calculate_path_distance(forward_path)
    backward_distance = calculate_path_distance(backward_path)
    
    return forward_path if forward_distance <= backward_distance else backward_path

def main():
    # Load and scale path
    original_path = load_path("extracted_path.csv")
    path = scale_path(original_path)
    
    if not path:
        print("No path found in CSV file")
        return
    
    # Initialize pygame components
    font = pygame.font.SysFont(None, 24)
    
    # Phase 1: Target Selection
    selecting_target = True
    start_point = None
    end_point = None
    shortest_path = None
    
    while selecting_target:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                if start_point is None:
                    # First click sets start point
                    _, closest_point, _ = find_target_path_point(click_pos, path)
                    start_point = closest_point
                else:
                    # Second click sets end point and ends selection
                    _, closest_point, _ = find_target_path_point(click_pos, path)
                    end_point = closest_point
                    # Find indices and calculate shortest path
                    start_index = path.index(start_point)
                    end_index = path.index(end_point)
                    shortest_path = find_shortest_path(path, start_index, end_index)
                    selecting_target = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        # Draw selection screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw path
        if len(path) > 1:
            pygame.draw.lines(screen, PATH_COLOR, False, path, 2)
        
        # Draw start point if selected
        if start_point:
            pygame.draw.circle(screen, (0, 255, 0), 
                             (int(start_point[0]), int(start_point[1])), 
                             DESTINATION_RADIUS)
        
        # Draw instructions
        text = font.render(
            "Click to set start point" if start_point is None else "Click to set end point", 
            True, (255, 255, 255)
        )
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Robot movement simulation
    robot_pos = start_point
    current_path_index = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Reset
                    robot_pos = start_point
                    current_path_index = 0
        
        screen.fill(BACKGROUND_COLOR)
        
        # Draw full path
        if len(path) > 1:
            pygame.draw.lines(screen, PATH_COLOR, False, path, 2)
        
        # Draw shortest path in different color
        if shortest_path and len(shortest_path) > 1:
            pygame.draw.lines(screen, (255, 255, 0), False, shortest_path, 3)
        
        # Draw start and end points
        pygame.draw.circle(screen, (0, 255, 0), 
                         (int(start_point[0]), int(start_point[1])), 
                         DESTINATION_RADIUS)
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(end_point[0]), int(end_point[1])), 
                         DESTINATION_RADIUS)
        
        # Move robot along path
        if current_path_index < len(shortest_path) - 1:
            target = shortest_path[current_path_index + 1]
            dx = target[0] - robot_pos[0]
            dy = target[1] - robot_pos[1]
            distance = sqrt(dx**2 + dy**2)
            
            if distance < SPEED:
                robot_pos = target
                current_path_index += 1
            else:
                dx = dx / distance * SPEED
                dy = dy / distance * SPEED
                robot_pos = (robot_pos[0] + dx, robot_pos[1] + dy)
        
        # Draw robot
        pygame.draw.circle(screen, ROBOT_COLOR, 
                         (int(robot_pos[0]), int(robot_pos[1])), 
                         ROBOT_RADIUS)
        
        # Display status and progress
        if current_path_index < len(shortest_path) - 1:
            progress = (current_path_index / (len(shortest_path)-1)) * 100
            status = f"Following path... {progress:.1f}%"
        else:
            status = "Destination reached! Press R to reset"
        
        status_text = font.render(status, True, (255, 255, 255))
        screen.blit(status_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()