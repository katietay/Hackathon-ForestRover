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

# Main function
def main():
    # Load and scale path
    original_path = load_path("extracted_path.csv")
    path = scale_path(original_path)
    
    if not path:
        print("No path found in CSV file")
        return
    
    # Set start and destination points (can be specified by user)
    # Example: First 1/4 and last 1/4 of path
    start_point = path[len(path) // 4]
    destination_point = path[3 * len(path) // 4]
    
    # Allow user to adjust start and destination
    font = pygame.font.SysFont(None, 24)
    adjusting = True
    dragging_start = False
    dragging_destination = False
    
    while adjusting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    adjusting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Check if clicking start or destination
                start_dist = sqrt((mouse_pos[0] - start_point[0])**2 + (mouse_pos[1] - start_point[1])**2)
                dest_dist = sqrt((mouse_pos[0] - destination_point[0])**2 + (mouse_pos[1] - destination_point[1])**2)
                
                if start_dist < ROBOT_RADIUS * 2:
                    dragging_start = True
                elif dest_dist < DESTINATION_RADIUS * 2:
                    dragging_destination = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_start = False
                dragging_destination = False
                
        if dragging_start:
            mouse_pos = pygame.mouse.get_pos()
            closest_idx = find_closest_path_point(mouse_pos, path)
            start_point = path[closest_idx]
            
        if dragging_destination:
            mouse_pos = pygame.mouse.get_pos()
            closest_idx = find_closest_path_point(mouse_pos, path)
            destination_point = path[closest_idx]
        
        # Draw setup screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw path
        if len(path) > 1:
            pygame.draw.lines(screen, PATH_COLOR, False, path, 2)
        
        # Draw start and destination
        pygame.draw.circle(screen, ROBOT_COLOR, (int(start_point[0]), int(start_point[1])), ROBOT_RADIUS)
        pygame.draw.circle(screen, DESTINATION_COLOR, (int(destination_point[0]), int(destination_point[1])), DESTINATION_RADIUS)
        
        # Draw instructions
        text = font.render("Drag to move start (red) and destination (blue). Press Enter to start.", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Find indices in path
    start_index = find_closest_path_point(start_point, path)
    destination_index = find_closest_path_point(destination_point, path)
    
    # Create path segment from start to destination
    if start_index <= destination_index:
        active_path = path[start_index:destination_index+1]
    else:
        # Handle case where destination is before start in path
        active_path = path[start_index:] + path[:destination_index+1]
    
    # Initialize robot position
    robot_pos = active_path[0]
    current_index = 0
    target_index = 1 if len(active_path) > 1 else 0
    destination_reached = False
    
    # Main simulation loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Reset
                    robot_pos = active_path[0]
                    current_index = 0
                    target_index = 1 if len(active_path) > 1 else 0
                    destination_reached = False
        
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw full path (dimmed)
        if len(path) > 1:
            pygame.draw.lines(screen, (0, 100, 0), False, path, 1)
        
        # Draw active path segment (bright)
        if len(active_path) > 1:
            pygame.draw.lines(screen, PATH_COLOR, False, active_path, 2)
        
        # Move robot along path if not at destination
        if not destination_reached and current_index < len(active_path) - 1:
            # Current position and target
            target_pos = active_path[target_index]
            
            # Calculate direction vector
            dx = target_pos[0] - robot_pos[0]
            dy = target_pos[1] - robot_pos[1]
            distance = sqrt(dx**2 + dy**2)
            
            # If we've reached the target point, move to next target
            if distance < SPEED:
                current_index += 1
                if current_index == len(active_path) - 1:
                    robot_pos = active_path[-1]
                    destination_reached = True
                else:
                    target_index = current_index + 1
                    robot_pos = active_path[current_index]
            else:
                # Normalize direction and move
                dx = dx / distance * SPEED
                dy = dy / distance * SPEED
                robot_pos = (robot_pos[0] + dx, robot_pos[1] + dy)
        
        # Draw destination
        pygame.draw.circle(screen, DESTINATION_COLOR, (int(destination_point[0]), int(destination_point[1])), DESTINATION_RADIUS)
        
        # Draw robot
        pygame.draw.circle(screen, ROBOT_COLOR, (int(robot_pos[0]), int(robot_pos[1])), ROBOT_RADIUS)
        
        # Display status
        if destination_reached:
            status_text = font.render("Destination reached! Press R to reset.", True, (255, 255, 255))
        else:
            status_text = font.render("Robot moving to destination...", True, (255, 255, 255))
        screen.blit(status_text, (10, 10))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()