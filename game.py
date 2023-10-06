import math
import random

import numpy
import pygame

import neural_network


def main():
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w * 0.75, info.current_h * 0.75), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 1

    # Maak stilstaande auto op x coordinaat 800, y coordinaat 450, 90 graden naar links gedraaid
    car = Car(800, 450, math.pi * -0.5, 0)

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

        car.move(screen, frame)

        # maak scherm grijs
        screen.fill((100, 100, 110))
        draw_map(screen, car.x, car.y)
        car.draw(screen)

        frame += 1
        pygame.display.update()
        clock.tick(60)


class Car:
    def __init__(self, x, y, angle, speed):
        self.x: float = x
        self.y: float = y
        self.dx: float = 0
        self.dy: float = 0
        self.angle: float = angle
        self.speed: float = speed
        self.image = pygame.image.load("assets/red_car.png")
        self.movement_angle = angle

    def rotate(self, angle):
        self.angle += angle

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self, screen, cycle):
        self.speed *= 0.97
        acceleration = 0.6

        resistance = acceleration * 7.77
        sensitivity = acceleration * 0.14
        max_rotation = acceleration * 0.04
        rotation = numpy.fmin(sensitivity * self.speed / numpy.fmax(abs(self.speed ** 1.5), resistance), max_rotation)

        network = neural_network.main([random.random() * 2 - 1, random.random() * 2 - 1], cycle)
        steering = network[0] * 2 - 1
        gas = network[1] * 2 - 1
        print(network)

        self.angle += rotation * steering
        self.speed += acceleration * gas

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
            self.x = screen.get_rect().width * 0.5
            self.y = screen.get_rect().height * 0.5

        self.movement_angle += (self.angle - self.movement_angle) * 0.1

        self.dx = -math.sin(self.movement_angle) * self.speed
        self.dy = -math.cos(self.movement_angle) * self.speed

        self.x += self.dx
        self.y += self.dy

    # draw gebeurt ook 60 keer per seconde, past veranderingen van move toe op het scherm
    def draw(self, surface: pygame.surface.Surface):
        image, rect = rotate_image(self.image, math.degrees(self.movement_angle), self.image.get_rect().center,
                                   pygame.math.Vector2(surface.get_rect().width * 0.5, surface.get_rect().height * 0.5))
        surface.blit(image, rect)

    def __str__(self):
        return f"Car at ({round(self.x)}, {round(self.y)})"


# snippet van iemand anders
def rotate_image(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, angle, 1)  # Rotate the image.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot + offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


def draw_map(screen, cam_x, cam_y):
    # baan is een lijst van stukjes weg
    # s = straight
    # l = links
    # r = rechts

    built_in_map = ["s", "l", "s", "r", "s", "r", "s", "s", "s", "s", "r", "s", "r", "l", "s", "r", "s", "r"]

    x: int = 100 - cam_x + screen.get_rect().width * 0.5
    y: int = 100 - cam_y + screen.get_rect().height * 0.5
    angle = 0
    size = 200

    straight_road = pygame.image.load("assets/road_straight.png")
    turn_road = pygame.image.load("assets/road_turn.png")

    for tile in built_in_map:
        # screen.fill((30, 30, 40), pygame.rect.Rect(x, y, size, size))

        if tile == "r":
            angle += 1
            image, rect = rotate_image(turn_road, angle * -90 + 180, turn_road.get_rect().center, pygame.Vector2(x, y))
            screen.blit(image, rect)
        elif tile == "l":
            angle -= 1
            image, rect = rotate_image(turn_road, angle * -90 - 90, turn_road.get_rect().center, pygame.Vector2(x, y))
            screen.blit(image, rect)
        elif tile == "s":
            image, rect = rotate_image(straight_road, angle * 90, straight_road.get_rect().center, pygame.Vector2(x, y))
            screen.blit(image, rect)

        real_angle = angle % 4

        if real_angle == 0:
            x += size
        elif real_angle == 1:
            y += size
        elif real_angle == 2:
            x -= size
        elif real_angle == 3:
            y -= size


if __name__ == '__main__':
    main()
