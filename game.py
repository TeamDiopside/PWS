import math
import time

import numpy
import pygame

import network

debug_info: list[str] = []
debug_mode = 2
loose_cam = False

background_color = (100, 100, 110)
ray_color = (255, 255, 255)
edge_color = (240, 20, 50)
middle_line_color = (20, 200, 250)
text_color = (255, 255, 255)
text_bg_color = (30, 30, 30)

max_change = 0.05
max_time = 15


def main():
    amount = int(input("Amount of cars: "))
    name = input("Generation name: ")
    generation = int(input("Generation: "))
    go(amount, name, generation)


def go(amount, name, generation):
    weights, biases = network.get_network_from_file(name, generation)
    game(amount, weights, biases, name, generation)


def game(car_amount, starting_weights, starting_biases, name, generation):
    global debug_mode, loose_cam
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w * 0.75, info.current_h * 0.75), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    pygame.display.set_caption("PWS")

    running = True
    frame = 1
    gen_time = time.time()

    # Maak auto's
    cars: list[Car] = create_cars(car_amount, starting_weights, starting_biases)
    selected_car_index = 0

    cam = Camera(0, 0.001)

    roads = create_roads()

    while running:
        delta_time = clock.get_time() / 16.6667

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
                if event.key == pygame.K_5:
                    debug_mode = 5
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
        debug_info.append(f"Generation: {name} {generation}")
        add_rounded_debug_info(f"Time: ", time.time() - gen_time)

        selected_car.add_debug_text(selected_car_index)

        alive_cars = len(cars)
        for car in cars:
            if time.time() - gen_time > max_time:
                car.on_road = False
            if car.on_road:
                car.calc_rays(roads)
                car.move(cars, selected_car_index, delta_time)

                if car.rays[0].intersections % 2 == 0 and car.is_mortal:
                    car.on_road = False
                    car.calc_distance_to_finish(roads)
            else:
                alive_cars -= 1

        if alive_cars <= 0:
            gen_time = time.time()
            best_car = cars[0]
            finished_cars = []
            for car in cars:
                if car.distance_traveled > best_car.distance_traveled:
                    best_car = car
                if car.distance_traveled > 0.99:
                    car.finished_time = time.time()
                    finished_cars.append(car)

            for car in finished_cars:
                if car.finished_time < best_car.finished_time:
                    best_car = car

            cars = create_cars(car_amount, best_car.weights, best_car.biases)
            generation += 1
            network.output_network_to_file(best_car.weights, best_car.biases, name, generation)

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
        clock.tick()


def create_cars(amount, weights, biases):
    def get_car(w, b):
        return Car(200, 0.3, math.pi * -0.5, 0, True, w, b)

    cars = [get_car(weights, biases)]

    for i in range(amount - 1):
        we = network.change_weights(weights, max_change)
        bi = network.change_biases(biases, max_change)
        cars.append(get_car(we, bi))

    return cars


def create_roads():
    roads: list[Road] = []
    # built_in_map = "bslsrsrssssrsrlse"
    # built_in_map = "bsslssrsssssrssssrsrlse"
    built_in_map = "bssrsrssssrsssslsslsrssse"
    # built_in_map = "bsssssssssssrsrslsssssse"
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
        elif self.road_type == "b":
            coords.append((-1, -1, 1, -1))
            coords.append((-1, 1, 1, 1))
            coords.append((-1, -1, -1, 1))
        elif self.road_type == "e":
            coords.append((-1, -1, 1, -1))
            coords.append((-1, 1, 1, 1))
            coords.append((1, -1, 1, 1))

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

        if self.road_type == "s" or self.road_type == "b":
            coords.append((-1, 0, 1, 0))
        elif self.road_type == "r":
            coords.append((0, 0, -1, 0))
            coords.append((0, 1, 0, 0))
        elif self.road_type == "l":
            coords.append((0, 0, 0, -1))
            coords.append((-1, 0, 0, 0))
        elif self.road_type == "e":
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
        beginning_road = pygame.image.load("assets/road_beginning.png")
        end_road = pygame.image.load("assets/road_end.png")
        destination = world_to_screen((self.pos.x, self.pos.y), cam, screen)

        image = straight_road

        if self.road_type == "r":
            image = pygame.transform.rotate(turn_road, -self.angle + 90)
        elif self.road_type == "l":
            image = pygame.transform.rotate(turn_road, -self.angle)
        elif self.road_type == "s":
            image = pygame.transform.rotate(straight_road, self.angle)
        elif self.road_type == "b":
            image = pygame.transform.rotate(beginning_road, self.angle)
        elif self.road_type == "e":
            image = pygame.transform.rotate(end_road, -self.angle)

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
    def __init__(self, x, y, angle, speed, mortal, weights, biases):
        self.weights = weights
        self.biases = biases
        self.is_mortal = mortal
        self.pos = Vector(x, y)
        self.angle: float = angle
        self.speed: float = speed
        self.image = pygame.image.load("assets/red_car.png")
        self.movement_angle = angle
        self.middle_point: Vector = Vector(0, 0)
        self.middle_segment = (0, 0, 0)
        self.distance_traveled = 0
        self.on_road = True
        self.finished_time = 0

        # van 0 tot 360 met stappen van 10 (in een cirkel rond de auto dus)
        self.rays: list[Ray] = []
        for ray_angle in range(180, 361, 30):
            self.rays.append(Ray(ray_angle))

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self, cars, selected_car_index, delta_time):
        self.speed *= 0.97 ** delta_time
        acceleration = 0.6

        # de kleine afstand die je in deze frame kan draaien, gebaseerd op hoe snel je gaat
        d_rotation = 0
        if self.speed != 0:
            x = 0.08 * abs(self.speed) - 1
            d_rotation = delta_time * 0.05 * (1 - x * x)

        if self.speed < 0:
            d_rotation = -d_rotation

        ai_enabled = True
        if ai_enabled:
            inputs = [self.speed, self.movement_angle]
            for ray in self.rays:
                inputs.append(ray.distance)
            outputs = network.calculate(self.weights, self.biases, inputs)
            steering = outputs[0] * 2 - 1
            gas = outputs[1] * 2 - 1

            self.angle += d_rotation * steering
            self.speed += acceleration * -gas

        if cars.index(self) == selected_car_index and not ai_enabled:
            active_keys = pygame.key.get_pressed()
            if active_keys[pygame.K_a]:
                self.angle += d_rotation
            if active_keys[pygame.K_d]:
                self.angle -= d_rotation
            if active_keys[pygame.K_w]:
                self.speed += acceleration * delta_time
            if active_keys[pygame.K_s]:
                self.speed -= acceleration * delta_time
            if active_keys[pygame.K_SPACE]:
                self.pos = Vector(0, 0)
                self.speed = 0

        self.movement_angle += (self.angle - self.movement_angle) * 0.1 * delta_time
        # self.movement_angle = self.angle

        self.pos.x += -math.sin(self.movement_angle) * self.speed * delta_time
        self.pos.y += -math.cos(self.movement_angle) * self.speed * delta_time

    # ray casting om afstand tot de rand van de weg te detecteren
    def calc_rays(self, roads: list[Road]):

        for ray in self.rays:
            ray.intersection = 1
            ray.distance = ray.max_distance
            ray.can_draw = False
            ray.intersections = 0

            # Meedraaien met de auto
            ray.angle = math.radians(ray.initial_angle) - self.movement_angle

            for road in roads:

                for edge in road.edges:

                    e1 = Vector(edge[0], edge[1])
                    e2 = Vector(edge[2], edge[3])

                    # Bereken het eindpunt van de ray op basis van de lengte en de hoek
                    r1 = self.pos
                    r2 = Vector(self.pos.x + ray.max_distance * math.cos(ray.angle),
                                self.pos.y + ray.max_distance * math.sin(ray.angle))

                    f_ray, f_muur, parallel = intersection(r1, r2, e1, e2)

                    if 0 <= f_ray and 0 <= f_muur <= 1 and not parallel:
                        ray.can_draw = True
                        ray.intersection = min(ray.intersection, f_ray)
                        ray.intersections += 1
                        ray.distance = ray.intersection * ray.max_distance

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

        self.distance_traveled = (self.middle_segment[0] + 0.5 * self.middle_segment[1] + self.middle_segment[
            2]) / len(roads)

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
            pygame.draw.line(screen, middle_line_color, screen_coords,
                             world_vec_to_screen(self.middle_point, cam, screen), 3)
            pygame.draw.circle(screen, middle_line_color, world_vec_to_screen(self.middle_point, cam, screen), 5)
            pygame.draw.circle(screen, middle_line_color, world_to_screen((self.pos.x, self.pos.y), cam, screen), 5)

        if debug_mode == 5:
            pygame.draw.line(screen, middle_line_color, world_vec_to_screen(self.pos, cam, screen), world_to_screen(
                (-math.sin(self.angle) * 150 + self.pos.x, -math.cos(self.angle) * 150 + self.pos.y), cam, screen), 3)
            pygame.draw.line(screen, ray_color, world_vec_to_screen(self.pos, cam, screen), world_to_screen(
                (-math.sin(self.movement_angle) * 150 + self.pos.x, -math.cos(self.movement_angle) * 150 + self.pos.y),
                cam, screen), 3)

    def add_debug_text(self, index):
        debug_info.append("")
        debug_info.append(f"AUTO {index + 1}")

        if self.on_road:
            add_rounded_debug_info("Snelheid: ", self.speed)
            add_rounded_debug_info("Hoek: ", self.angle)
            add_rounded_debug_info("X: ", self.pos.x)
            add_rounded_debug_info("Y: ", self.pos.y)
        else:
            debug_info.append("Niet op de weg!!!")
            debug_info.append(f"Distance: {self.distance_traveled}")


    def __str__(self):
        return f"Car at ({round(self.pos.x)}, {round(self.pos.y)})"


def intersection(a1, a2, b1, b2):
    cross = (b1.x - b2.x) * (a1.y - a2.y) - (b1.y - b2.y) * (a1.x - a2.x)
    if cross != 0:
        mpx = b1.x - a1.x
        mpy = b1.y - a1.y
        f_a = (mpx * (b1.y - b2.y) - mpy * (b1.x - b2.x)) / cross
        f_b = (mpx * (a1.y - a2.y) - mpy * (a1.x - a2.x)) / cross
        return f_a, f_b, False
    else:
        return 0, 0, True


class Ray:
    def __init__(self, angle):
        self.angle = angle
        self.initial_angle = angle
        self.intersection = 1
        self.can_draw = False
        self.max_distance = 1000
        self.distance = 0
        self.intersections = 0

    def __str__(self):
        return f"Distance: {self.distance}"


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
    # start(3, "alpha", 0)
