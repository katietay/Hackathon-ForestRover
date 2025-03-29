import pygame
from robot_class import Robot
from PIL import Image
import rasterio
import numpy as np

pygame.init()
with rasterio.open("South_Clear_Creek_BareEarth_Hillshade_1m_chunk_8192_0.tiff") as src:
    data = src.read(1)
    with open("shade.txt", "w") as f:
        for row in data:
            f.write(" ".join(map(str, row)) + "\n")

image = Image.open("South_Clear_Creek_BareEarth_Hillshade_1m_chunk_8192_0.tiff")
width, height = image.size

screen = pygame.display.set_mode((512 , 512))
clock = pygame.time.Clock()

imp = pygame.image.load("shade.tiff").convert()
screen.blit(imp, (0, 0))

# Create robot and load terrain data
bot = Robot(2, width=10, height=10)
bot.load_terrain_data("shade.txt")

# Add font for displaying current mode
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Create a heatmap visualization overlay (optional)
def create_terrain_overlay(terrain_data, alpha=128):
    max_value = np.max(terrain_data)
    min_value = np.min(terrain_data)
    
    h, w = terrain_data.shape
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    
    for y in range(h):
        for x in range(w):
            # Normalize to 0-255 range
            value = terrain_data[y, x]
            normalized = int(255 * (value - min_value) / (max_value - min_value))
            
            # Higher values (better paths) are brighter green
            overlay.set_at((x, y), (0, normalized, 0, alpha))
    
    return pygame.transform.scale(overlay, (width, height))

# Create overlay (comment out if not needed)
# overlay = create_terrain_overlay(bot.terrain_data, alpha=50)
camera = pygame.Rect(0,0, width, height)
# For toggling overlay
show_overlay = False
show_help = True
position = (500, 200)
running = True
panning = False
pan_start = (0, 0)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            panning = True
            pan_start = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                panning = False
        elif event.type == pygame.MOUSEMOTION:
            if panning:
                dx, dy = event.pos[0] - pan_start[0], event.pos[1] - pan_start[1]
                camera.x += dx
                camera.y += dy
                pan_start = event.pos
                camera.x = max(0, min(camera.x, width - camera.width))
                camera.y = max(0, min(camera.y, height - camera.height))


        
    bot.find_path(position)
    screen.blit(imp, (0, 0))
    
    # Show terrain overlay if enabled
    if show_overlay and hasattr(bot, 'terrain_data') and bot.terrain_data is not None:
        overlay = create_terrain_overlay(bot.terrain_data, alpha=50)
        screen.blit(overlay, (0, 0))
    
    try:
        if bot.target:
            bot.update()
    except ValueError:
        bot.path = []
        
    # Draw route if there are route points
    if len(bot.route_points) > 1:
        pygame.draw.lines(screen, (0, 255, 0), False, bot.route_points, 2)
        
        # Draw small circles at waypoints for visibility
        for point in bot.route_points:
            pygame.draw.circle(screen, (255, 255, 0), point, 3)
    
    # Draw the robot
    pygame.draw.rect(screen, (255, 0, 0), bot.robot)
    
    # Display current movement type and distance threshold
    text = font.render(f"Mode: {bot.movement_type} (Threshold: {bot.distance_threshold}px)", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    # Show help text
    if show_help:
        help_text = [
            "Click anywhere to move the robot",
            "Press 'o' to toggle terrain overlay",
            "Press 'm' to cycle movement modes",
            "Press 'h' to hide this help"
        ]
        
        for i, line in enumerate(help_text):
            help_line = small_font.render(line, True, (255, 255, 255))
            screen.blit(help_line, (10, height - 100 + i*20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
