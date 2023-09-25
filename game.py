import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("PWS")

    running = True

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_F11]:
            pygame.display.toggle_fullscreen()

        pygame.display.update()
        pygame.time.Clock().tick(60)


class Car:
    def __init__(self, x, y, angle, speed):
        self.x: float = x
        self.y: float = y
        self.angle: float = angle
        self.speed: float = speed

    def __str__(self):
        return f"Car at ({self.x}, {self.y})"


if __name__ == '__main__':
    main()
