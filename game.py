import math
import random

import numpy
import pygame

import neural_network

debug_info: list[str] = []


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

        debug_info.append(f"FPS: {int(clock.get_fps())}")

        car.move(screen, frame)

        # maak scherm grijs
        screen.fill((100, 100, 110))
        draw_map(screen, car.x, car.y)
        car.draw(screen)
        draw_text(debug_info, screen)

        clear_debug_info()
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
    def move(self, screen, frame):
        self.speed *= 0.97
        acceleration = 0.6

        resistance = acceleration * 7.77
        sensitivity = acceleration * 0.14
        max_rotation = acceleration * 0.04
        rotation = numpy.fmin(sensitivity * self.speed / numpy.fmax(abs(self.speed ** 1.5), resistance), max_rotation)

        ai_enabled = False
        if ai_enabled:
            network = neural_network.main([random.random() * 2 - 1, random.random() * 2 - 1], frame)
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

        add_rounded_debug_info("Speed: ", self.speed)
        add_rounded_debug_info("X: ", self.x)
        add_rounded_debug_info("Y: ", self.y)

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

    # Pre-rotate de weg
    rotated_straight_roads = {
        0: straight_road,
        1: pygame.transform.rotate(straight_road, 90)
    }

    rotated_turn_roads = {
        0: turn_road,
        1: pygame.transform.rotate(turn_road, 90),
        2: pygame.transform.rotate(turn_road, 180),
        3: pygame.transform.rotate(turn_road, 270)
    }

    for tile in built_in_map:

        if tile == "r":
            angle += 1
            screen.blit(rotated_turn_roads[(angle * -1 + 6) % 4], rotated_turn_roads[(angle * -1 + 6) % 4].get_rect(center=(x, y)))
        elif tile == "l":
            angle -= 1
            screen.blit(rotated_turn_roads[(angle * -1 + 3) % 4], rotated_turn_roads[(angle * -1 + 3) % 4].get_rect(center=(x, y)))
        elif tile == "s":
            screen.blit(rotated_straight_roads[angle % 2], rotated_straight_roads[angle % 2].get_rect(center=(x, y)))

        real_angle = angle % 4

        if real_angle == 0:
            x += size
        elif real_angle == 1:
            y += size
        elif real_angle == 2:
            x -= size
        elif real_angle == 3:
            y -= size


def draw_text(text_list: list[str], screen: pygame.surface.Surface):
    font_size = 20
    font = pygame.font.Font("assets/JetBrainsMono.ttf", font_size)

    for i, text in enumerate(text_list):
        text_surf = font.render(text, True, (255, 255, 255), (30, 30, 30))
        text_surf.set_alpha(170)
        screen.blit(text_surf, (0, i * math.ceil(font_size + font_size / 3)))


def add_rounded_debug_info(string: str, number: float):
    debug_info.append(string + str(round(number, 3)))


def clear_debug_info():
    global debug_info
    debug_info = []


if __name__ == '__main__':
    main()
