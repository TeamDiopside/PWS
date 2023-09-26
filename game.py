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

        car.move(screen)

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
    def move(self, screen):
        self.speed *= 0.97
        acceleration = 0.5

        resistance = acceleration * 7.77
        sensitivity = acceleration * 0.14
        max_rotation = acceleration * 0.04
        rotation = numpy.fmin(sensitivity * self.speed / numpy.fmax(abs(self.speed ** 1.5), resistance), max_rotation)

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

        self.movement_angle += (self.angle - self.movement_angle) * 0.1

        self.x += -math.sin(self.movement_angle) * self.speed
        self.y += -math.cos(self.movement_angle) * self.speed

        screen_right = screen.get_rect().width - 50
        screen_down = screen.get_rect().height - 50

        if self.x < -50 or self.x > screen_right or self.y < -50 or self.y > screen_down:
            self.speed = 0

        self.x = numpy.fmax(self.x, -50)
        self.y = numpy.fmax(self.y, -50)
        self.x = numpy.fmin(self.x, screen_right)
        self.y = numpy.fmin(self.y, screen_down)

    # draw gebeurt ook 60 keer per seconde, past veranderingen van move toe op het scherm
    def draw(self, surface: pygame.surface.Surface):
        image, rect = rotate_center(self.image, math.degrees(self.movement_angle), self.image.get_rect().center, pygame.math.Vector2(self.x, self.y))
        surface.blit(image, rect)

    def __str__(self):
        return f"Car at ({round(self.x)}, {round(self.y)})"


def rotate_center(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, angle, 1)  # Rotate the image.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


if __name__ == '__main__':
    main()
