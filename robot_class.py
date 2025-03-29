import pygame

class Robot:
    def __init__(self, speed):
        self.speed = speed
        self.robot = pygame.Rect(300, 300, 10, 10)

    def update(self):

        #EXAMPLE ON BASIC MOVEMENT
        if self.robot.centerx > 500: 
            self.move_left()
        else:
            self.move_right()

    def move_left(self):
        self.robot.move_ip(-self.speed, 0)

    def move_right(self):
        self.robot.move_ip(self.speed, 0)

    def move_up(self):
        self.robot.move_ip(0, -self.speed)

    def move_down(self):
        self.robot.move_ip(0, self.speed)
