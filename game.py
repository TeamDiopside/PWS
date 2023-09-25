import math

import pygame


def main():
    pygame.init()

    screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 0

    car = Car(1200, 400, math.pi * -0.5, 0)

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

        car.move()

        screen.fill((80, 80, 80))
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
        self.movement_angle = angle

    def rotate(self, angle):
        self.angle += angle

    def move(self):
        self.speed *= 0.95

        sensitivity = 0.1
        acceleration = 1

        active_keys = pygame.key.get_pressed()
        if active_keys[pygame.K_LEFT]:
            self.angle -= sensitivity
        if active_keys[pygame.K_RIGHT]:
            self.angle += sensitivity
        if active_keys[pygame.K_UP]:
            self.speed += acceleration
        if active_keys[pygame.K_DOWN]:
            self.speed -= acceleration

        self.movement_angle += (self.angle - self.movement_angle) * 0.05

        self.x += math.cos(self.movement_angle) * self.speed
        self.y += math.sin(self.movement_angle) * self.speed

    def draw(self, surface: pygame.surface.Surface):
        rect = pygame.rect.Rect((self.x, self.y), (50, 50))
        color = (40, 40, 40)
        surface.fill(color, rect)

        look_rect = pygame.rect.Rect((self.x + math.cos(self.angle) * 50 + 20, self.y + math.sin(self.angle) * 50 + 20), (10, 10))
        surface.fill((180, 80, 80), look_rect)

    def __str__(self):
        return f"Car at ({round(self.x)}, {round(self.y)})"


if __name__ == '__main__':
    main()
