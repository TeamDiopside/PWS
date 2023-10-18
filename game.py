import math
import random

import numpy
import pygame

import neural_network

debug_info: list[str] = []
debug_mode = 3


def main():
    global debug_mode
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w * 0.75, info.current_h * 0.75), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 1

    # Maak stilstaande auto 90 graden naar links gedraaid
    car = Car(0, 0.3, math.pi * -0.5, 0)

    roads = create_roads()

    while running:
        for event in pygame.event.get():
            # afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    debug_mode = 1
                if event.key == pygame.K_2:
                    debug_mode = 2
                if event.key == pygame.K_3:
                    debug_mode = 3

        debug_info.append(f"FPS: {int(clock.get_fps())}")

        car.move(screen, frame)
        car.calc_rays(screen, roads, car.x, car.y)

        if car.rays[0].intersections % 2 == 0:
            debug_info.append("Niet op de weg!!!")

        # maak scherm grijs
        screen.fill((100, 100, 110))

        for road in roads:
            road.draw(screen, car.x, car.y)
        car.draw(screen)

        if debug_mode > 1:
            draw_text(debug_info, screen)

        clear_debug_info()
        frame += 1
        pygame.display.update()
        clock.tick(60)


def create_roads():
    roads: list[Road] = []
    built_in_map = ["s", "l", "s", "r", "s", "r", "s", "s", "s", "s", "r", "s", "r", "l", "s", "r", "s", "r"]
    x, y = 0, 0
    direction = 0
    size = 200

    for road_type in built_in_map:
        simplified_direction = direction % 4

        # de huidige positie verschuiven
        if simplified_direction == 0:
            x += size
        elif simplified_direction == 1:
            y += size
        elif simplified_direction == 2:
            x -= size
        elif simplified_direction == 3:
            y -= size

        roads.append(Road(x, y, road_type, simplified_direction * 90, size))

        # de richting aanpassen voor de volgende
        if road_type == "r":
            direction += 1
        elif road_type == "l":
            direction -= 1

    return roads


# dit moet boven de Car class want anders werkt die niet, deze class moet dus eerder in de file staan
class Road:
    def __init__(self, x, y, road_type, angle, size):
        self.x: int = x
        self.y: int = y
        self.road_type: str = road_type
        self.angle: int = angle
        self.size: int = size
        self.edges = self.create_edges()

    def create_edges(self):
        edges_ = []

        x1, x2, x3, x4 = -0.5, -0.5, -0.5, 0.5
        y1, y2, y3, y4 = -0.5, +0.5, -0.5, -0.5

        if self.angle == 0:
            if self.road_type == "r":
                x1, x2, y1, y2 = -0.5, 0.5, -0.5, -0.5
                x3, x4, y3, y4 = 0.5, 0.5, -0.5, 0.5
            elif self.road_type == "s":
                x1, x2, y1, y2 = -0.5, 0.5, -0.5, -0.5
                x3, x4, y3, y4 = -0.5, 0.5, 0.5, 0.5
            elif self.road_type == "l":
                x1, x2, y1, y2 = 0.5, 0.5, -0.5, 0.5
                x3, x4, y3, y4 = -0.5, 0.5, 0.5, 0.5
        elif self.angle == 90:
            if self.road_type == "r":
                x1, x2, y1, y2 = 0.5, 0.5, -0.5, 0.5
                x3, x4, y3, y4 = -0.5, 0.5, 0.5, 0.5
            elif self.road_type == "s":
                x1, x2, y1, y2 = -0.5, -0.5, -0.5, 0.5
                x3, x4, y3, y4 = 0.5, 0.5, -0.5, 0.5
            elif self.road_type == "l":
                x1, x2, y1, y2 = -0.5, 0.5, 0.5, 0.5
                x3, x4, y3, y4 = -0.5, -0.5, -0.5, 0.5
        elif self.angle == 180:
            if self.road_type == "r":
                x1, x2, y1, y2 = -0.5, 0.5, 0.5, 0.5
                x3, x4, y3, y4 = -0.5, -0.5, -0.5, 0.5
            elif self.road_type == "s":
                x1, x2, y1, y2 = 0.5, -0.5, 0.5, 0.5
                x3, x4, y3, y4 = 0.5, -0.5, -0.5, -0.5
            elif self.road_type == "l":
                x1, x2, y1, y2 = -0.5, -0.5, -0.5, 0.5
                x3, x4, y3, y4 = 0.5, -0.5, -0.5, -0.5
        elif self.angle == 270:
            if self.road_type == "r":
                x1, x2, y1, y2 = -0.5, -0.5, -0.5, 0.5
                x3, x4, y3, y4 = -0.5, 0.5, -0.5, -0.5
            elif self.road_type == "s":
                x1, x2, y1, y2 = 0.5, 0.5, -0.5, 0.5
                x3, x4, y3, y4 = -0.5, -0.5, -0.5, 0.5
            elif self.road_type == "l":
                x1, x2, y1, y2 = 0.5, -0.5, -0.5, -0.5
                x3, x4, y3, y4 = 0.5, 0.5, -0.5, 0.5

        line_1_start = (self.x + x1 * self.size, self.y + y1 * self.size)
        line_1_end = (self.x + x2 * self.size, self.y + y2 * self.size)
        line_2_start = (self.x + x3 * self.size, self.y + y3 * self.size)
        line_2_end = (self.x + x4 * self.size, self.y + y4 * self.size)

        edges_.append((line_1_start[0], line_1_start[1], line_1_end[0], line_1_end[1]))
        edges_.append((line_2_start[0], line_2_start[1], line_2_end[0], line_2_end[1]))

        return edges_

    def draw(self, screen: pygame.surface.Surface, cam_x, cam_y):
        straight_road = pygame.image.load("assets/road_straight.png")
        turn_road = pygame.image.load("assets/road_turn.png")
        destination = (self.x - cam_x, self.y - cam_y)

        if self.road_type == "r":
            image = pygame.transform.rotate(turn_road, -self.angle + 90)
            screen.blit(image, image.get_rect(center=destination))
        elif self.road_type == "l":
            image = pygame.transform.rotate(turn_road, -self.angle)
            screen.blit(image, image.get_rect(center=destination))
        elif self.road_type == "s":
            image = pygame.transform.rotate(straight_road, self.angle)
            screen.blit(image, image.get_rect(center=destination))

        if debug_mode == 3:
            pygame.draw.circle(screen, (255, 0, 0), destination, 5)

            for edge in self.edges:
                pygame.draw.line(screen, (255, 0, 0), (edge[0] - cam_x, edge[1] - cam_y), (edge[2] - cam_x, edge[3] - cam_y), 5)


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

        # van 0 tot 360 met stappen van 10 (in een cirkel rond de auto dus)
        self.rays: list[Ray] = []
        for ray_angle in range(0, 360, 10):
            self.rays.append(Ray(ray_angle))

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

        add_rounded_debug_info("Snelheid: ", self.speed)
        add_rounded_debug_info("Hoek: ", self.angle)
        add_rounded_debug_info("X: ", self.x)
        add_rounded_debug_info("Y: ", self.y)

    # ray casting om afstand tot de rand van de weg te detecteren
    def calc_rays(self, screen: pygame.surface.Surface, roads: list[Road], cam_x, cam_y):

        for ray in self.rays:
            ray.intersection = 1
            ray.distance = ray.length
            ray.can_draw = False
            ray.intersections = 0

            for road in roads:

                for edge in road.edges:

                    edge_x1, edge_y1, edge_x2, edge_y2 = edge
                    edge_x1 -= cam_x
                    edge_x2 -= cam_x
                    edge_y1 -= cam_y
                    edge_y2 -= cam_y

                    # Meedraaien met de auto
                    ray.angle = math.radians(ray.initial_angle) - self.movement_angle

                    # positie is afhankelijk van middelpunt van auto en middelpunt van scherm
                    x_position = self.image.get_rect().center[0] + screen.get_rect().width * 0.5
                    y_position = self.image.get_rect().center[1] + screen.get_rect().height * 0.5

                    # Bereken het eindpunt van de ray op basis van de lengte en de hoek
                    ray_eind_x = x_position + ray.length * math.cos(ray.angle)
                    ray_eind_y = y_position + ray.length * math.sin(ray.angle)

                    # kijk voor snijpunt
                    snijpunt = (x_position - ray_eind_x) * (edge_y1 - edge_y2) - (y_position - ray_eind_y) * (
                                edge_x1 - edge_x2)

                    if snijpunt != 0:
                        # het punt op de lijn waar het snijpunt ligt (tussen 0 en 1)
                        f_ray = ((x_position - edge_x1) * (edge_y1 - edge_y2) - (y_position - edge_y1) * (
                                    edge_x1 - edge_x2)) / snijpunt
                        # het punt op de muur (tussen 0 en 1)
                        f_muur = -((x_position - edge_x1) * (ray_eind_y - y_position) - (y_position - edge_y1) * (
                                    ray_eind_x - x_position)) / snijpunt

                        if 0 <= f_ray <= 1 and 0 <= f_muur <= 1:
                            ray.can_draw = True
                            ray.intersection = min(ray.intersection, f_ray)
                            ray.intersections += 1
                            ray.distance = ray.intersection * ray.length

    # draw gebeurt ook 60 keer per seconde, past veranderingen van move toe op het scherm
    def draw(self, screen: pygame.surface.Surface):
        image, rect = rotate_image(self.image, math.degrees(self.movement_angle), self.image.get_rect().center,
                                   pygame.math.Vector2(screen.get_rect().width * 0.5, screen.get_rect().height * 0.5))
        screen.blit(image, rect)

        if debug_mode == 3:
            for ray in self.rays:
                if ray.can_draw:
                    x_middle, y_middle = self.get_middle_coords(screen)
                    snijpunt_x = x_middle + ray.distance * math.cos(ray.angle)
                    snijpunt_y = y_middle + ray.distance * math.sin(ray.angle)

                    pygame.draw.circle(screen, (255, 255, 255), (snijpunt_x, snijpunt_y), 5)
                    pygame.draw.line(screen, (255, 255, 255), (x_middle, y_middle), (snijpunt_x, snijpunt_y))

    def get_middle_coords(self, screen):
        x_position = self.image.get_rect().center[0] + screen.get_rect().width * 0.5
        y_position = self.image.get_rect().center[1] + screen.get_rect().height * 0.5
        return x_position, y_position

    def __str__(self):
        return f"Car at ({round(self.x)}, {round(self.y)})"


class Ray:
    def __init__(self, angle):
        self.angle = angle
        self.initial_angle = angle
        self.intersection = 1
        self.can_draw = False
        self.length = 10_000_000_000
        self.distance = 0
        self.intersections = 0


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


def draw_text(text_list: list[str], screen: pygame.surface.Surface):
    font_size = 20
    font = pygame.font.Font("assets/JetBrainsMono.ttf", font_size)

    for i, text in enumerate(text_list):
        text_surf = font.render(text, True, (255, 255, 255), (30, 30, 30))
        text_surf.set_alpha(170)
        screen.blit(text_surf, (0, i * text_surf.get_rect().height))


def add_rounded_debug_info(string: str, number: float):
    debug_info.append(string + str(round(number, 3)))


def clear_debug_info():
    global debug_info
    debug_info = []


if __name__ == '__main__':
    main()
