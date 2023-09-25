import math

import pygame


def main():
    pygame.init()

    screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)

    pygame.display.set_caption("PWS")

    running = True
    t = 0

    car = Car(0, 0, 0.4, 1)

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

        car.move()

        screen.fill((80, 80, 80))

        car.draw(screen)

        t += 1
        pygame.display.update()
        pygame.time.Clock().tick(60)


class Car:
    def __init__(self, x, y, angle, speed):
        self.x: float = x
        self.y: float = y
        self.angle: float = angle
        self.speed: float = speed

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, surface: pygame.surface.Surface):
        surface.fill((40, 40, 40), pygame.rect.Rect((self.x - 10, self.y - 10), (self.x + 10, self.y + 10)))

    def __str__(self):
        return f"Car at ({self.x}, {self.y})"


if __name__ == '__main__':
    main()
