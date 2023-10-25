import math
import random

import numpy
import pygame

import neural_network

debug_info: list[str] = []
debug_mode = 4
cam_mode = 2


def main():
    global debug_mode, cam_mode
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w * 0.75, info.current_h * 0.75), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 1

    # Maak stilstaande auto 90 graden naar links gedraaid
    car = Car(0, 0.3, math.pi * -0.5, 0)
    cam = Camera(0, 0)

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
                if event.key == pygame.K_4:
                    debug_mode = 4
                if event.key == pygame.K_F1:
                    cam_mode = 1
                if event.key == pygame.K_F2:
                    cam_mode = 2

        debug_info.append(f"FPS: {int(clock.get_fps())}")

        car.move(frame)

        if cam_mode == 1:
            cam.move()
        else:
            cam.x_speed = 0
            cam.y_speed = 0
            cam.x, cam.y = car.x, car.y

        car.calc_rays(roads)
        car.calc_distance_to_middle(roads)

        if car.rays[0].intersections % 2 == 0:
            debug_info.append("Niet op de weg!!!")

        # maak scherm grijs
        screen.fill((100, 100, 110))

        for road in roads:
            road.draw(screen, cam)
        car.draw(screen, cam)

        if debug_mode > 1:
            draw_text(debug_info, screen)

        clear_debug_info()
        frame += 1
        pygame.display.update()
        clock.tick(60)


# coordinate method om ons leven te vermakkelijken
def world_to_screen(world_coords, cam_x, cam_y, screen):
    return (world_coords[0] - cam_x + screen.get_rect().width * 0.5,
            world_coords[1] - cam_y + screen.get_rect().height * 0.5)


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


class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0

    def move(self):
        acceleration = 1

        active_keys = pygame.key.get_pressed()
        if active_keys[pygame.K_LEFT]:
            self.x_speed -= acceleration
        if active_keys[pygame.K_RIGHT]:
            self.x_speed += acceleration
        if active_keys[pygame.K_UP]:
            self.y_speed -= acceleration
        if active_keys[pygame.K_DOWN]:
            self.y_speed += acceleration
        if active_keys[pygame.K_SPACE]:
            self.x = 0
            self.y = 0
            self.x_speed = 0
            self.y_speed = 0

        self.x_speed *= 0.95
        self.y_speed *= 0.95

        self.x += self.x_speed
        self.y += self.y_speed

        add_rounded_debug_info("Cam X: ", self.x)
        add_rounded_debug_info("Cam Y: ", self.y)


# dit moet boven de Car class want anders werkt die niet, deze class moet dus eerder in de file staan
class Road:
    def __init__(self, x, y, road_type, angle, size):
        self.x: int = x
        self.y: int = y
        self.road_type: str = road_type
        self.angle: int = angle
        self.size: int = size
        self.edges = self.create_edges()
        self.middle_lines = self.create_middle()

    # de coordinaten maken voor de randen die bij het type weg horen
    def create_edges(self):
        edges = []
        coords = []

        if self.road_type == "r":
            coords.append((-1, -1, 1, -1))
            coords.append((1, -1, 1, 1))
        elif self.road_type == "s":
            coords.append((-1, -1, 1, -1))
            coords.append((-1, 1, 1, 1))
        elif self.road_type == "l":
            coords.append((1, -1, 1, 1))
            coords.append((-1, 1, 1, 1))

        for pair in coords:
            vector1 = rotate_vector([pair[0], pair[1]], self.angle)
            vector2 = rotate_vector([pair[2], pair[3]], self.angle)

            start = (self.x + vector1[0] * self.size * 0.5, self.y + vector1[1] * self.size * 0.5)
            end = (self.x + vector2[0] * self.size * 0.5, self.y + vector2[1] * self.size * 0.5)
            edges.append((start[0], start[1], end[0], end[1]))

        return edges

    # de coordinaten maken voor de randen die bij het type weg horen
    def create_middle(self):
        middle = []
        coords = []

        if self.road_type == "r":
            coords.append((0, 0, -1, 0))
            coords.append((0, 1, 0, 0))
        elif self.road_type == "s":
            coords.append((-1, 0, 1, 0))
        elif self.road_type == "l":
            coords.append((0, 0, 0, -1))
            coords.append((-1, 0, 0, 0))

        for pair in coords:
            vector1 = rotate_vector([pair[0], pair[1]], self.angle)
            vector2 = rotate_vector([pair[2], pair[3]], self.angle)

            start = (self.x + vector1[0] * self.size * 0.5, self.y + vector1[1] * self.size * 0.5)
            end = (self.x + vector2[0] * self.size * 0.5, self.y + vector2[1] * self.size * 0.5)
            middle.append((start[0], start[1], end[0], end[1]))

        return middle

    def draw(self, screen: pygame.surface.Surface, cam):
        straight_road = pygame.image.load("assets/road_straight.png")
        turn_road = pygame.image.load("assets/road_turn.png")
        destination = world_to_screen((self.x, self.y), cam.x, cam.y, screen)

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
            pygame.draw.circle(screen, (220, 20, 20), destination, 5)
            for edge in self.edges:
                pygame.draw.line(screen, (240, 20, 50), world_to_screen((edge[0], edge[1]), cam.x, cam.y, screen),
                                 world_to_screen((edge[2], edge[3]), cam.x, cam.y, screen), 5)

        if debug_mode == 4:
            for middle_line in self.middle_lines:
                pygame.draw.line(screen, (0, 200, 200),
                                 world_to_screen((middle_line[0], middle_line[1]), cam.x, cam.y, screen),
                                 world_to_screen((middle_line[2], middle_line[3]), cam.x, cam.y, screen), 5)


# dit kennen we
def rotate_vector(vector, angle):
    angle = numpy.radians(angle)
    matrix = [
        [math.cos(angle), -math.sin(angle)],
        [math.sin(angle), math.cos(angle)]
    ]
    return numpy.matmul(matrix, vector)


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
        self.middle_point: tuple[int, int] = (0, 0)

        # van 0 tot 360 met stappen van 10 (in een cirkel rond de auto dus)
        self.rays: list[Ray] = []
        for ray_angle in range(0, 360, 10):
            self.rays.append(Ray(ray_angle))

    def rotate(self, angle):
        self.angle += angle

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self, frame):
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
        if active_keys[pygame.K_a]:
            self.angle += rotation
        if active_keys[pygame.K_d]:
            self.angle -= rotation
        if active_keys[pygame.K_w]:
            self.speed += acceleration
        if active_keys[pygame.K_s]:
            self.speed -= acceleration
        if active_keys[pygame.K_SPACE]:
            self.x = 0
            self.y = 0
            self.speed = 0

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
    def calc_rays(self, roads: list[Road]):

        for ray in self.rays:
            ray.intersection = 1
            ray.distance = ray.length
            ray.can_draw = False
            ray.intersections = 0

            for road in roads:

                for edge in road.edges:

                    edge_x1, edge_y1, edge_x2, edge_y2 = edge

                    # Meedraaien met de auto
                    ray.angle = math.radians(ray.initial_angle) - self.movement_angle

                    # positie is afhankelijk van middelpunt van auto en middelpunt van scherm
                    x_position, y_position = self.get_middle_coords()

                    # Bereken het eindpunt van de ray op basis van de lengte en de hoek
                    ray_eind_x = x_position + ray.length * math.cos(ray.angle)
                    ray_eind_y = y_position + ray.length * math.sin(ray.angle)

                    cross_product = ((x_position - ray_eind_x) * (edge_y1 - edge_y2)
                                     - (y_position - ray_eind_y) * (edge_x1 - edge_x2))

                    if cross_product != 0:
                        # het punt op de lijn waar het snijpunt ligt (tussen 0 en 1)
                        f_ray = ((x_position - edge_x1) * (edge_y1 - edge_y2)
                                 - (y_position - edge_y1) * (edge_x1 - edge_x2)) / cross_product
                        # het punt op de muur (tussen 0 en 1)
                        f_muur = -((x_position - edge_x1) * (ray_eind_y - y_position)
                                   - (y_position - edge_y1) * (ray_eind_x - x_position)) / cross_product

                        if 0 <= f_ray <= 1 and 0 <= f_muur <= 1:
                            ray.can_draw = True
                            ray.intersection = min(ray.intersection, f_ray)
                            ray.intersections += 1
                            ray.distance = ray.intersection * ray.length
                            if debug_mode == 3:
                                add_rounded_debug_info("Distance: ", ray.distance)

    def calc_distance_to_middle(self, roads: list[Road]):
        self.middle_point = None
        x_middle, y_middle = self.get_middle_coords()

        for road in roads:
            for middle_line in road.middle_lines:
                mx1, my1, mx2, my2 = middle_line

                px1 = x_middle
                py1 = y_middle
                px2 = px1 - my1 - my2
                py2 = py1 + mx1 - mx2

                cross_product = (mx1 - mx2) * (py1 - py2) - (my1 - my2) * (px1 - px2)

                if cross_product != 0:
                    # het punt op de lijn waar het snijpunt ligt (tussen 0 en 1)
                    f_perp = ((px1 - mx1) * (my1 - my2) - (py1 - my1) * (mx1 - mx2)) / cross_product
                    # het punt op de muur (tussen 0 en 1)
                    f_middle = -((px1 - mx1) * (my2 - py1) - (py1 - my1) * (mx2 - px1)) / cross_product

                    if 0 <= f_middle <= 1:
                        int_x = px1 + f_perp * px2
                        int_y = py1 + f_perp * py2
                        if self.middle_point is not None:
                            distance = math.sqrt(
                                self.middle_point[0] * self.middle_point[0] + self.middle_point[1] * self.middle_point[
                                    1])
                            new_distance = math.sqrt(int_x * int_x + int_y * int_y)
                            if new_distance < distance:
                                self.middle_point = (int_x, int_y)
                        else:
                            self.middle_point = (int_x, int_y)

    # draw past veranderingen van move toe op het scherm
    def draw(self, screen: pygame.surface.Surface, cam):
        screen_coords = world_to_screen(self.get_middle_coords(), cam.x, cam.y, screen)
        add_rounded_debug_info("Screen X: ", screen_coords[0])
        add_rounded_debug_info("Screen Y: ", screen_coords[1])
        image, rect = rotate_image(self.image, math.degrees(self.movement_angle), screen_coords)
        screen.blit(image, rect)

        if debug_mode == 3:
            for ray in self.rays:
                if ray.can_draw:
                    # screen coordinates
                    snijpunt_x = screen_coords[0] + ray.distance * math.cos(ray.angle)
                    snijpunt_y = screen_coords[1] + ray.distance * math.sin(ray.angle)

                    pygame.draw.circle(screen, (255, 255, 255), (snijpunt_x, snijpunt_y), 5)
                    pygame.draw.line(screen, (255, 255, 255), screen_coords, (snijpunt_x, snijpunt_y))

        if debug_mode == 4 and self.middle_point is not None:
            pygame.draw.line(screen, (255, 255, 255), screen_coords, world_to_screen(self.middle_point, cam.x, cam.y, screen))

    def get_middle_coords(self):
        return self.x, self.y

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


def rotate_image(surface, angle, pos):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pos (tuple, list, pygame.math.Vector2): the center off the object in screen coordinates.
    """
    rotated_image = pygame.transform.rotozoom(surface, angle, 1)  # Rotate the image.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pos)
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
