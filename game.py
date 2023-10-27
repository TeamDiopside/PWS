import math
import random

import numpy
import pygame

import neural_network

debug_info: list[str] = []
debug_mode = 4
loose_cam = False

background_color = (100, 100, 110)
ray_color = (255, 255, 255)
edge_color = (240, 20, 50)
middle_line_color = (20, 200, 250)
text_color = (255, 255, 255)
text_bg_color = (30, 30, 30)


def main():
    global debug_mode, loose_cam
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w * 0.75, info.current_h * 0.75), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 1

    # Maak auto's
    car_amount = 10
    cars: list[Car] = []
    selected_car_index = 0

    for i in range(car_amount):
        cars.append(Car(150, 0.3, math.pi * -0.5, 0))

    cam = Camera(0, 0.001)

    roads = create_roads()

    while running:

        # --- UPDATE ---

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
                if event.key == pygame.K_e:
                    loose_cam = not loose_cam
                if event.key == pygame.K_LEFTBRACKET:
                    selected_car_index -= 1
                    selected_car_index = selected_car_index % car_amount
                if event.key == pygame.K_RIGHTBRACKET:
                    selected_car_index += 1
                    selected_car_index = selected_car_index % car_amount
        selected_car = cars[selected_car_index]

        debug_info.append(f"FPS: {int(clock.get_fps())}")

        for car in cars:
            debug_info.append("")
            debug_info.append(f"AUTO {cars.index(car) + 1}")

            if car.on_road:
                car.move(frame, cars, selected_car_index)
                car.calc_rays(roads)

                if car.rays[0].intersections % 2 == 0:
                    car.on_road = False
                    car.calc_distance_to_finish(roads)
            else:
                debug_info.append("Niet op de weg!!!")
                debug_info.append(f"Distance: {car.distance_to_finish}")

        if loose_cam:
            cam.move()
        else:
            cam.speed = Vector(0, 0)
            cam.pos = selected_car.pos
            cam.mouse_move()

        # --- DRAW ---

        # maak scherm grijs
        screen.fill(background_color)

        for i, road in enumerate(roads):
            road.draw(screen, cam)
            road.draw_middle(screen, cam, abs(2 * i / len(roads) - 1))

        for car in cars:
            car.draw(screen, cam)

        selected_car.draw_debug(screen, cam)

        if debug_mode > 1:
            draw_text(debug_info, screen)

        clear_debug_info()
        frame += 1
        pygame.display.update()
        clock.tick(60)


def create_roads():
    roads: list[Road] = []
    built_in_map = ["s", "l", "s", "r", "s", "r", "s", "s", "s", "s", "r", "s", "r", "l", "s", "r", "s"]
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
        self.pos = Vector(x, y)
        self.speed = Vector(0, 0)
        self.mouse_down = Vector(0, 0)

    def move(self):
        acceleration = 1

        active_keys = pygame.key.get_pressed()
        if active_keys[pygame.K_LEFT]:
            self.speed.x -= acceleration
        if active_keys[pygame.K_RIGHT]:
            self.speed.x += acceleration
        if active_keys[pygame.K_UP]:
            self.speed.y -= acceleration
        if active_keys[pygame.K_DOWN]:
            self.speed.y += acceleration
        if active_keys[pygame.K_SPACE]:
            self.pos = Vector(0, 0)
            self.speed = Vector(0, 0)

        self.mouse_move()

        self.speed.x *= 0.95
        self.speed.y *= 0.95

        self.pos += self.speed

        add_rounded_debug_info("Cam X: ", self.pos.x)
        add_rounded_debug_info("Cam Y: ", self.pos.y)

    def mouse_move(self):
        new_mouse = Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        if pygame.mouse.get_pressed()[0]:
            self.pos -= new_mouse - self.mouse_down
            global loose_cam
            loose_cam = True
        self.mouse_down = new_mouse


# coordinate method om ons leven makkelijker te maken
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, other):
        return self.x * other.y - self.y * other.x

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def rotate_90(self):
        return Vector(-self.y, self.x)

    def multiply(self, number):
        self.x *= number
        self.y *= number
        return self


def world_to_screen(world_coords: tuple, cam: Camera, screen):
    return (world_coords[0] - cam.pos.x + screen.get_rect().width * 0.5,
            world_coords[1] - cam.pos.y + screen.get_rect().height * 0.5)


def world_vec_to_screen(world_coords: Vector, cam: Camera, screen):
    return (world_coords.x - cam.pos.x + screen.get_rect().width * 0.5,
            world_coords.y - cam.pos.y + screen.get_rect().height * 0.5)


# dit moet boven de Car class want anders werkt die niet, deze class moet dus eerder in de file staan
class Road:
    def __init__(self, x, y, road_type, angle, size):
        self.pos = Vector(x, y)
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

            start = (self.pos.x + vector1[0] * self.size * 0.5, self.pos.y + vector1[1] * self.size * 0.5)
            end = (self.pos.x + vector2[0] * self.size * 0.5, self.pos.y + vector2[1] * self.size * 0.5)
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

            start = (self.pos.x + vector1[0] * self.size * 0.5, self.pos.y + vector1[1] * self.size * 0.5)
            end = (self.pos.x + vector2[0] * self.size * 0.5, self.pos.y + vector2[1] * self.size * 0.5)
            middle.append((start[0], start[1], end[0], end[1]))

        return middle

    def draw(self, screen: pygame.surface.Surface, cam):
        straight_road = pygame.image.load("assets/road_straight.png")
        turn_road = pygame.image.load("assets/road_turn.png")
        destination = world_to_screen((self.pos.x, self.pos.y), cam, screen)

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
            pygame.draw.circle(screen, edge_color, destination, 5)
            for edge in self.edges:
                pygame.draw.line(screen, edge_color, world_to_screen((edge[0], edge[1]), cam, screen),
                                 world_to_screen((edge[2], edge[3]), cam, screen), 5)

    def draw_middle(self, screen, cam, color):
        if debug_mode == 4:
            for middle_line in self.middle_lines:
                pygame.draw.line(screen, (0, 200 * color, 150),
                                 world_to_screen((middle_line[0], middle_line[1]), cam, screen),
                                 world_to_screen((middle_line[2], middle_line[3]), cam, screen), 5)


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
        self.pos = Vector(x, y)
        self.angle: float = angle
        self.speed: float = speed
        self.image = pygame.image.load("assets/red_car.png")
        self.movement_angle = angle
        self.middle_point: Vector = Vector(0, 0)
        self.middle_segment = (0, 0, 0)
        self.distance_to_finish = 0
        self.on_road = True

        # van 0 tot 360 met stappen van 10 (in een cirkel rond de auto dus)
        self.rays: list[Ray] = []
        for ray_angle in range(180, 361, 30):
            self.rays.append(Ray(ray_angle))

    def rotate(self, angle):
        self.angle += angle

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self, frame, cars, selected_car_index):
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

        if cars.index(self) == selected_car_index:
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
                self.pos = Vector(0, 0)
                self.speed = 0

        self.movement_angle += (self.angle - self.movement_angle) * 0.1

        self.pos.x += -math.sin(self.movement_angle) * self.speed
        self.pos.y += -math.cos(self.movement_angle) * self.speed

        add_rounded_debug_info("Snelheid: ", self.speed)
        add_rounded_debug_info("Hoek: ", self.angle)
        add_rounded_debug_info("X: ", self.pos.x)
        add_rounded_debug_info("Y: ", self.pos.y)

    # ray casting om afstand tot de rand van de weg te detecteren
    def calc_rays(self, roads: list[Road]):

        for ray in self.rays:
            ray.intersection = 1
            ray.distance = ray.length
            ray.can_draw = False
            ray.intersections = 0

            for road in roads:

                for edge in road.edges:

                    e1 = Vector(edge[0], edge[1])
                    e2 = Vector(edge[2], edge[3])

                    # Meedraaien met de auto
                    ray.angle = math.radians(ray.initial_angle) - self.movement_angle

                    # Bereken het eindpunt van de ray op basis van de lengte en de hoek
                    r1 = self.pos
                    r2 = Vector(self.pos.x + ray.length * math.cos(ray.angle), self.pos.y + ray.length * math.sin(ray.angle))

                    cross_product = (r1 - r2) * (e1 - e2)

                    if cross_product != 0:
                        # het punt op de lijn waar het snijpunt ligt (tussen 0 en 1)
                        f_ray = (r1 - e1) * (e1 - e2) / cross_product
                        # het punt op de muur (tussen 0 en 1)
                        f_muur = (r1 - e1) * (r1 - r2) / cross_product

                        if 0 <= f_ray and 0 <= f_muur <= 1:
                            ray.can_draw = True
                            ray.intersection = min(ray.intersection, f_ray)
                            ray.intersections += 1
                            ray.distance = ray.intersection * ray.length

    def calc_distance_to_finish(self, roads: list[Road]):
        self.middle_point = None

        for i, road in enumerate(roads):
            for j, middle_line in enumerate(road.middle_lines):

                m1 = Vector(middle_line[0], middle_line[1])
                m2 = Vector(middle_line[2], middle_line[3])

                p1 = Vector(self.pos.x, self.pos.y)
                p2 = p1 + (m1 - m2).rotate_90()

                cross_product = (m1 - m2) * (p1 - p2)

                if cross_product != 0:
                    f_perp = (m1 - p1) * (m1 - m2) / cross_product
                    f_middle = (m1 - p1) * (p1 - p2) / cross_product

                    if 0 <= f_middle <= 1:
                        # De kortste afstand zit midden op een lijnstuk
                        ints = p1 + (p2 - p1).multiply(f_perp)
                        if self.middle_point is not None:
                            distance = (p1 - self.middle_point).length()
                            new_distance = (p1 - ints).length()
                            if new_distance < distance:
                                self.middle_point = ints
                                self.middle_segment = (i, j, f_middle)
                        else:
                            self.middle_point = ints
                            self.middle_segment = (i, j, f_middle)
                    else:
                        # De kortste afstand zit op een hoekpunt
                        new_distance1 = (p1 - m1).length()
                        new_distance2 = (p1 - m2).length()
                        closest = m1 if new_distance1 < new_distance2 else m2
                        if self.middle_point is not None:
                            if (p1 - closest).length() < (p1 - self.middle_point).length():
                                self.middle_point = closest
                                self.middle_segment = (i, j, 0 if closest == m1 else 1)
                        else:
                            self.middle_point = closest
                            self.middle_segment = (i, j, 0 if closest == m1 else 1)

        self.distance_to_finish = (self.middle_segment[0] + 0.5 * self.middle_segment[1] + self.middle_segment[2]) / len(roads)

    # draw past veranderingen van move toe op het scherm
    def draw(self, screen: pygame.surface.Surface, cam):
        screen_coords = world_to_screen((self.pos.x, self.pos.y), cam, screen)
        image, rect = rotate_image(self.image, math.degrees(self.movement_angle), screen_coords)
        screen.blit(image, rect)

    def draw_debug(self, screen: pygame.surface.Surface, cam):
        screen_coords = world_to_screen((self.pos.x, self.pos.y), cam, screen)

        if debug_mode == 3:
            for ray in self.rays:
                if ray.can_draw:
                    # screen coordinates
                    snijpunt_x = screen_coords[0] + ray.distance * math.cos(ray.angle)
                    snijpunt_y = screen_coords[1] + ray.distance * math.sin(ray.angle)

                    pygame.draw.circle(screen, ray_color, (snijpunt_x, snijpunt_y), 5)
                    pygame.draw.line(screen, ray_color, screen_coords, (snijpunt_x, snijpunt_y))

        if debug_mode == 4 and self.middle_point is not None and not self.on_road:
            pygame.draw.line(screen, middle_line_color, screen_coords, world_vec_to_screen(self.middle_point, cam, screen), 3)
            pygame.draw.circle(screen, middle_line_color, world_vec_to_screen(self.middle_point, cam, screen), 5)
            pygame.draw.circle(screen, middle_line_color, world_to_screen((self.pos.x, self.pos.y), cam, screen), 5)

    def __str__(self):
        return f"Car at ({round(self.pos.x)}, {round(self.pos.y)})"


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
    font_size = 15
    font = pygame.font.Font("assets/JetBrainsMono.ttf", font_size)

    for i, text in enumerate(text_list):
        text_surf = font.render(text, True, text_color, text_bg_color)
        text_surf.set_alpha(170)
        screen.blit(text_surf, (0, i * text_surf.get_rect().height))


def add_rounded_debug_info(string: str, number: float):
    debug_info.append(string + str(round(number, 3)))


def clear_debug_info():
    global debug_info
    debug_info = []


if __name__ == '__main__':
    main()
