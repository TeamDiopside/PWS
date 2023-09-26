import math

import numpy
import pygame


def main():
    pygame.init()

    screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 0

    # Maak stilstaande auto op x coordinaat 800, y coordinaat 450, 90 graden naar links gedraaid
    car = Car(800, 450, math.pi * -0.5, 0)

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

        car.move()

        # maak scherm grijs
        screen.fill((100, 100, 100))
        car.draw(screen)

        frame += 1
        pygame.display.update()
        clock.tick(60)


class Car:
    def __init__(self, x, y, angle, speed):
        self.x: float = x
        self.y: float = y
        self.angle: float = angle
        self.speed: float = speed
        self.image = pygame.image.load("assets/red_car.png")
        self.movement_angle = angle

    def rotate(self, angle):
        self.angle += angle

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self):
        self.speed *= 0.95

        resistance = 7
        sensitivity = 0.13
        acceleration = 0.9
        max_rotation = 0.04
        rotation = numpy.fmin(sensitivity * self.speed / numpy.fmax(abs(self.speed ** 1.5), resistance), max_rotation)

        print(rotation)

        active_keys = pygame.key.get_pressed()
        if active_keys[pygame.K_LEFT] or active_keys[pygame.K_a]:
            self.angle += rotation
        if active_keys[pygame.K_RIGHT] or active_keys[pygame.K_d]:
            self.angle -= rotation
        if active_keys[pygame.K_UP] or active_keys[pygame.K_w]:
            self.speed += acceleration
        if active_keys[pygame.K_DOWN] or active_keys[pygame.K_s]:
            self.speed -= acceleration
        if active_keys[pygame.K_SPACE]:
            self.speed += 3

        self.movement_angle += (self.angle - self.movement_angle) * 0.05

        self.x += -math.sin(self.movement_angle) * self.speed
        self.y += -math.cos(self.movement_angle) * self.speed

    # draw gebeurt ook 60 keer per seconde, past veranderingen van move toe op het scherm
    def draw(self, surface: pygame.surface.Surface):
        surface.blit(rotate_center(self.image, self.movement_angle), (self.x, self.y), surface.get_rect())

    def __str__(self):
        return f"Car at ({round(self.x)}, {round(self.y)})"


def rotate_center(image, angle):
    rot_image = pygame.transform.rotate(image, math.degrees(angle))
    rot_rect = image.get_rect().copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


if __name__ == '__main__':
    main()
