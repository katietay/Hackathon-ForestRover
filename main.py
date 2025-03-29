import pygame
from robot_class import Robot 

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1000, 750))

bot = Robot(1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 

    screen.fill((0,0,0))

    bot.update()

    pygame.draw.rect(screen, (255,0,0), bot.robot)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()