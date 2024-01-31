import math
import random
import time

import numpy
import pygame

import network

debug_mode = 2
ai_enabled = True
debug_info: list[str] = []   # Lijst met alles wat op het scherm komt te staan
loose_cam = False            # Of de camera stilstaat of aan een auto zit
mortal_cars = True           # Of de auto's kunnen crashen
automatic_continue = True    # Of de volgende generatie automatisch start als de generatie klaar is
random_roads = True          # Of de weg elke generatie moet veranderen

# RGB-waarden voor de kleuren van dingen
background_color = (100, 100, 110)
ray_color = (255, 255, 255)
edge_color = (240, 20, 50)
middle_line_color = (20, 200, 250)
text_color = (255, 255, 255)
text_bg_color = (30, 30, 30)

straight_road = pygame.image.load("assets/road_straight.png")
turn_road = pygame.image.load("assets/road_turn.png")
beginning_road = pygame.image.load("assets/road_beginning.png")
end_road = pygame.image.load("assets/road_end.png")

max_change = 0.15   # de maximale hoeveelheid die weights en biases kunnen veranderen per generatie
max_time = 20       # de maximale tijd per generatie in seconden

# Alle ingebouwde wegen die we kunnen aanzetten
# built_in_map = "bslsrsrssssrsrlse"
# built_in_map = "bssssrsslssslsssrsse"
# built_in_map = "bsslssrsssssrssssrsrlse"
# built_in_map = "bssrsrssssrsssslsslsrssse"
built_in_map = "bsssrsssslssse"
# built_in_map = "bsssssssssssrsrslsssssse"
# built_in_map = "bsrslsslssssssssrsrsle"
# built_in_map = "bsrslsslssslssrsrsssslrsre"
# built_in_map = "bslsre"

# Alle ingebouwde maps voor het trainen
training_maps = [
    "bssssssssssrsslse",
    "bsssslsssssrsslse",
    "bssssrsssssrsslse",
    "bssslsrssssrsslse",
    "bsssrslssssrsslse",
    "bssslslssssrsslse",
    "bsssrsrsssssrsslse",
    "bssrsssssssrsslse",
    "bsslsssssssrsslse",
    "bssssssrsssrsslse",
    "bsssssslsssrsslse",
]


# Inputs in de console zetten
def main():
    amount = int(input("Amount of cars: "))
    name = input("Generation name: ")
    generation = int(input("Generation: "))
    go(amount, name, generation)


# Weights en biases uit een file halen en de simulatie starten
def go(amount, name, generation):
    weights, biases = network.get_network_from_file(name, generation)
    game(amount, weights, biases, name, generation)


# De simulatie: beginwaarden en de loop
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

    # De lijst met auto's maken
    cars: list[Car] = create_cars(car_amount, starting_weights, starting_biases)
    selected_car_index = 0

    cam = Camera(0, 0.001)

    roads, middle_segments, middle_lengths, total_length = create_roads()

    # De loop die er voor zorgt dat we steeds nieuwe frames krijgen, alles wat hierin zit wordt elke frame gedaan
    while running:

        # --- UPDATE --- hier berekenen we alles voor deze frame

        # Delta time is de tijd die de vorige frame nodig had,
        # hiermee kunnen we de bewegingen met verschillende FPS gelijk laten lopen
        delta_time = clock.get_time() / 16.6667

        global max_change
        global max_time
        continue_gen = False
        for event in pygame.event.get():
            # Afsluiten als je op het kruisje drukt
            if event.type == pygame.QUIT:
                running = False

            # Voor elke ingedrukte knop iets doen
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
                if event.key == pygame.K_6:
                    debug_mode = 6
                if event.key == pygame.K_e:
                    loose_cam = not loose_cam
                if event.key == pygame.K_LEFTBRACKET:
                    selected_car_index -= 1
                    selected_car_index = selected_car_index % car_amount
                if event.key == pygame.K_RIGHTBRACKET:
                    selected_car_index += 1
                    selected_car_index = selected_car_index % car_amount
                if event.key == pygame.K_EQUALS:
                    max_change += 0.01
                if event.key == pygame.K_MINUS:
                    max_change -= 0.01
                if event.key == pygame.K_c:
                    continue_gen = True
                if event.key == pygame.K_p:
                    max_time += 1
                if event.key == pygame.K_o:
                    max_time -= 1

        # Tekst aan het scherm toevoegen, dit moet elke frame opnieuw
        debug_info.append(f"FPS: {int(clock.get_fps())}")
        debug_info.append(f"Generation: {name} {generation}")
        add_rounded_debug_info(f"Time: ", time.time() - gen_time)
        add_rounded_debug_info(f"Max Change: ", max_change)

        selected_car = cars[selected_car_index]
        selected_car.add_debug_info(selected_car_index)

        alive_cars = len(cars)

        # Voor elke auto de rays berekenen, de bewegingen berekenen en kijken of de auto gecrasht is
        for car in cars:
            if car.on_road and not continue_gen:
                car.calc_rays(roads)
                car.move(cars, selected_car_index, delta_time)

                # Crashen als de ray een even aantal lijnen tegenkomt of als de tijd op is
                if car.rays[0].intersections % 2 == 0 and mortal_cars or time.time() - gen_time > max_time:
                    car.crash(roads, middle_segments, middle_lengths, total_length, gen_time)
            else:
                alive_cars -= 1

        # De volgende generatie starten als alle auto's gecrasht zijn en uitzoeken wie de winnaar is
        if alive_cars <= 0:
            best_car = cars[0]
            finished_cars = []
            for car in cars:
                if car.distance_traveled > best_car.distance_traveled:
                    best_car = car
                if car.distance_traveled > 0.99:
                    finished_cars.append(car)

            for car in finished_cars:
                if car.finished_time < best_car.finished_time:
                    best_car = car

            if automatic_continue or continue_gen:
                gen_time = time.time()
                cars = create_cars(car_amount, best_car.weights, best_car.biases)
                if random_roads:
                    roads, middle_segments, middle_lengths, total_length = create_roads()
                generation += 1
                network.output_network_to_file(best_car.weights, best_car.biases, name, generation)

        if loose_cam:
            cam.move()
        else:
            cam.speed = Vector(0, 0)
            cam.pos = selected_car.pos
            cam.calculate_mouse_movement()

        # --- DRAW --- hier tekenen we alles op het scherm

        # Maak scherm grijs
        screen.fill(background_color)

        for i, road in enumerate(roads):
            if debug_mode != 6:
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
    # Altijd de beste auto weer in de volgende generatie stoppen
    cars = [Car(weights, biases)]

    # Het neural network aanpassen voor alle andere auto's
    for i in range(amount - 1):
        changed_weights = network.change_weights(weights, max_change)
        changed_biases = network.change_biases(biases, max_change / 3)
        cars.append(Car(changed_weights, changed_biases))
    return cars


def create_roads():
    roads: list[Road] = []
    middle_segments = []
    middle_lengths: list[float] = []
    x, y = 0, 0
    direction = 0
    size = 200

    selected_map = training_maps[random.randint(0, len(training_maps) - 1)]

    for road_type in selected_map:
        simplified_direction = direction % 4

        # Steeds naar de volgende positie schuiven
        if simplified_direction == 0:
            x += size
        elif simplified_direction == 1:
            y += size
        elif simplified_direction == 2:
            x -= size
        elif simplified_direction == 3:
            y -= size

        roads.append(Road(x, y, road_type, simplified_direction * 90, size))

        # De richting aanpassen voor de volgende
        if road_type == "r":
            direction += 1
        elif road_type == "l":
            direction -= 1

    total_length = 0
    for road in roads:
        for segment in road.middle_lines:
            middle_segments.append(segment)
            length = numpy.sqrt((segment[0] - segment[2]) ** 2 + (segment[1] - segment[3]) ** 2)
            middle_lengths.append(length)
            total_length += length

    return roads, middle_segments, middle_lengths, total_length


class Camera:
    def __init__(self, x, y):
        self.pos = Vector(x, y)
        self.speed = Vector(0, 0)
        self.mouse_down = Vector(0, 0)   # Waar de muis heeft geklikt

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

        self.calculate_mouse_movement()

        self.speed.x *= 0.95
        self.speed.y *= 0.95

        self.pos += self.speed

        debug_info.append("")
        add_rounded_debug_info("Cam X: ", self.pos.x)
        add_rounded_debug_info("Cam Y: ", self.pos.y)

    def calculate_mouse_movement(self):
        new_mouse = Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        if pygame.mouse.get_pressed()[0]:
            self.pos -= new_mouse - self.mouse_down
            global loose_cam
            loose_cam = True
        self.mouse_down = new_mouse


# De bekende
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
        return Vector(self.x * number, self.y * number)


# Coördinaten van de wereld vertalen naar coordinaten op het scherm
def world_to_screen(world_coords: tuple, cam: Camera, screen):
    return (world_coords[0] - cam.pos.x + screen.get_rect().width * 0.5,
            world_coords[1] - cam.pos.y + screen.get_rect().height * 0.5)


# Hetzelfde maar dan voor een vector
def world_to_screen_vec(world_coords: Vector, cam: Camera, screen):
    return (world_coords.x - cam.pos.x + screen.get_rect().width * 0.5,
            world_coords.y - cam.pos.y + screen.get_rect().height * 0.5)


class Road:
    def __init__(self, x, y, road_type, angle, size):
        self.pos = Vector(x, y)
        self.road_type: str = road_type
        self.angle: int = angle
        self.size: int = size
        self.edges = self.create_edges()
        self.middle_lines = self.create_middle()

    # De coördinaten maken voor de randen die bij het type weg horen
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

    # De coördinaten maken voor de middellijk die bij het type weg hoort
    def create_middle(self):
        middle = []
        coords = []

        if self.road_type == "s" or self.road_type == "b":
            coords.append((-1, 0, 1, 0))
        elif self.road_type == "r":
            coords.append((-0.6, 0, -1, 0))
            coords.append((-0.6, 0, 0, 0.6))
            coords.append((0, 1, 0, 0.6))
        elif self.road_type == "l":
            coords.append((-1, 0, -0.6, 0))
            coords.append((-0.6, 0, 0, -0.6))
            coords.append((0, -0.6, 0, -1))
        elif self.road_type == "e":
            coords.append((-1, 0, 0, 0))

        for pair in coords:
            vector1 = rotate_vector([pair[0], pair[1]], self.angle)
            vector2 = rotate_vector([pair[2], pair[3]], self.angle)

            start = (self.pos.x + vector1[0] * self.size * 0.5, self.pos.y + vector1[1] * self.size * 0.5)
            end = (self.pos.x + vector2[0] * self.size * 0.5, self.pos.y + vector2[1] * self.size * 0.5)
            middle.append((start[0], start[1], end[0], end[1]))

        return middle

    # De berekende wegen tekenen op het scherm op basis van de positie van de camera.
    def draw(self, screen: pygame.surface.Surface, cam):
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

        # Als debugmodus 3 aan staat ook de middelpunten en randen tekenen
        if debug_mode == 3:
            pygame.draw.circle(screen, edge_color, destination, 5)
            for edge in self.edges:
                pygame.draw.line(screen, edge_color, world_to_screen((edge[0], edge[1]), cam, screen),
                                 world_to_screen((edge[2], edge[3]), cam, screen), 5)

    # Als debugmodus 4 aan staat ook de middellijn over de weg tekenen
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
    def __init__(self, weights, biases):
        self.weights = weights
        self.biases = biases
        self.pos = Vector(200, 0.3)
        self.angle = math.pi * -0.5
        self.speed = 0
        self.image = pygame.image.load("assets/red_car.png")
        self.movement_angle = math.pi * -0.5
        self.middle_point: Vector = Vector(0, 0)
        self.middle = (0, 0, 0)
        self.distance_traveled = 0
        self.on_road = True
        self.finished_time = 0

        self.rays: list[Ray] = []
        for ray_angle in range(180, 361, 30):
            self.rays.append(Ray(ray_angle))

    # move gebeurt 60 keer per seconde, past waarden van de auto aan
    def move(self, cars, selected_car_index, delta_time):
        # De wrijving van de banden, waardoor de snelheid afneemt
        self.speed *= 0.97 ** delta_time
        acceleration = 0.6

        # De kleine afstand die je in deze frame kan draaien, gebaseerd op hoe snel je gaat
        x = 0.08 * abs(self.speed) - 1
        d_rotation = 0.05 * (1 - x * x)

        if self.speed < 0:
            d_rotation = -d_rotation

        reduced_angle = abs(self.movement_angle % (0.5 * math.pi) - 0.25 * math.pi)
        add_rounded_debug_info("Reduced Angle: ", reduced_angle)

        if ai_enabled:
            inputs = [self.speed, reduced_angle]
            for ray in self.rays:  # Alle rays aan de inputlijst toevoegen
                inputs.append(ray.distance)
            outputs = network.calculate(self.weights, self.biases, inputs)

            # Outputs omzetten naar getallen van -1 naar 1
            steering = outputs[0] * 2 - 1
            gas = outputs[1] * 2 - 1

            # De outputs gebruiken
            self.angle += d_rotation * steering * delta_time
            self.speed += acceleration * -gas * delta_time

        if cars.index(self) == selected_car_index and not ai_enabled:
            active_keys = pygame.key.get_pressed()
            if active_keys[pygame.K_a]:
                self.angle += d_rotation * delta_time
            if active_keys[pygame.K_d]:
                self.angle -= d_rotation * delta_time
            if active_keys[pygame.K_w]:
                self.speed += acceleration * delta_time
            if active_keys[pygame.K_s]:
                self.speed -= acceleration * delta_time
            if active_keys[pygame.K_SPACE]:
                self.pos = Vector(0, 0)
                self.speed = 0

        self.movement_angle += (self.angle - self.movement_angle) * 0.1 * delta_time

        self.pos.x += -math.sin(self.movement_angle) * self.speed * delta_time
        self.pos.y += -math.cos(self.movement_angle) * self.speed * delta_time

    # Wanneer de auto van de weg af raakt, wordt de tijd opgeslagen en de afgelegde afstand berekend
    def crash(self, roads, middle_segments, middle_lengths, total_length, gen_time):
        self.on_road = False
        self.finished_time = time.time() - gen_time
        self.calc_distance_to_finish(roads, middle_segments, middle_lengths, total_length)

    # Ray casting om afstand tot de rand van de weg te detecteren
    def calc_rays(self, roads: list[Road]):
        for ray in self.rays:
            ray.intersection = 1
            ray.distance = ray.max_distance
            ray.can_draw = False
            ray.intersections = 0

            # Meedraaien met de auto
            ray.angle = math.radians(ray.initial_angle) - self.movement_angle

            # Voor elke edge van elke road kijken of deze de ray snijdt
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

    # Bereken de afstand tot de finish door te kijken bij welke middellijn de auto zich bevindt en de lengte van de middellijnen van gepasseerde wegdelen bij elkaar op te tellen.
    def calc_distance_to_finish(self, roads: list[Road], middle_segments, middle_lengths, total_length):
        self.middle_point = None

        # Kijk op welk wegdeel de auto zit
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
                                self.middle = (middle_line, f_middle)
                        else:
                            self.middle_point = ints
                            self.middle = (middle_line, f_middle)
                    else:
                        # De kortste afstand zit op een hoekpunt
                        new_distance1 = (p1 - m1).length()
                        new_distance2 = (p1 - m2).length()
                        closest = m1 if new_distance1 < new_distance2 else m2
                        if self.middle_point is not None:
                            if (p1 - closest).length() < (p1 - self.middle_point).length():
                                self.middle_point = closest
                                self.middle = (middle_line, 0 if closest == m1 else 1)
                        else:
                            self.middle_point = closest
                            self.middle = (middle_line, 0 if closest == m1 else 1)

        segment = middle_segments.index(self.middle[0])
        previous_length = 0
        # Afstanden van de middellijnen van vorige wegdelen optellen
        for i in range(segment):
            previous_length += middle_lengths[i]
        # Bereken totale afgelegde afstand en deel dit door de totale afstand tussen start en finish om een getal tussen 0 en 1 te krijgen
        self.distance_traveled = (previous_length + middle_lengths[segment] * self.middle[1]) / total_length

    # Draw past veranderingen van move toe op het scherm
    def draw(self, screen: pygame.surface.Surface, cam):
        screen_coords = world_to_screen((self.pos.x, self.pos.y), cam, screen)
        image, rect = rotate_image(self.image, math.degrees(self.movement_angle), screen_coords)
        screen.blit(image, rect)

    def draw_debug(self, screen: pygame.surface.Surface, cam):
        screen_coords = world_to_screen((self.pos.x, self.pos.y), cam, screen)

        # Als debugmodus 3 aan staat de rays tekenen rond de auto
        if debug_mode == 3 or debug_mode == 6:
            for ray in self.rays:
                if ray.can_draw:
                    # screen coordinates
                    snijpunt_x = screen_coords[0] + ray.distance * math.cos(ray.angle)
                    snijpunt_y = screen_coords[1] + ray.distance * math.sin(ray.angle)

                    pygame.draw.circle(screen, ray_color, (snijpunt_x, snijpunt_y), 5)
                    pygame.draw.line(screen, ray_color, screen_coords, (snijpunt_x, snijpunt_y))

        # Als debugmodus 4 aan staat een lijntje trekken tussen de middellijn en de auto, mits de auto van de weg is geraakt
        if debug_mode == 4 and self.middle_point is not None and not self.on_road:
            pygame.draw.line(screen, middle_line_color, screen_coords,
                             world_to_screen_vec(self.middle_point, cam, screen), 3)
            pygame.draw.circle(screen, middle_line_color, world_to_screen_vec(self.middle_point, cam, screen), 5)
            pygame.draw.circle(screen, middle_line_color, world_to_screen((self.pos.x, self.pos.y), cam, screen), 5)

        # Debugmodus 5 geeft de hoek aan waar de auto naartoe wil draaien
        if debug_mode == 5:
            pygame.draw.line(screen, middle_line_color, world_to_screen_vec(self.pos, cam, screen), world_to_screen(
                (-math.sin(self.angle) * 150 + self.pos.x, -math.cos(self.angle) * 150 + self.pos.y), cam, screen), 3)
            pygame.draw.line(screen, ray_color, world_to_screen_vec(self.pos, cam, screen), world_to_screen(
                (-math.sin(self.movement_angle) * 150 + self.pos.x, -math.cos(self.movement_angle) * 150 + self.pos.y),
                cam, screen), 3)

    # Voegt informatie van de auto toe aan de debugmodus
    def add_debug_info(self, index):
        debug_info.append("")
        debug_info.append(f"AUTO {index + 1}")
        add_rounded_debug_info("X: ", self.pos.x)
        add_rounded_debug_info("Y: ", self.pos.y)

        if self.on_road:
            add_rounded_debug_info("Snelheid: ", self.speed)
            add_rounded_debug_info("Hoek: ", self.angle)
        else:
            debug_info.append("Niet op de weg!!!")
            debug_info.append(f"Distance: {self.distance_traveled}")
            debug_info.append(f"Time: {self.finished_time}")

    def __str__(self):
        return f"Car at ({round(self.pos.x)}, {round(self.pos.y)})"


# Berekent een snijpunt tussen 2 vectoren
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


# Ray object met eigenschappen
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


# Zorgt ervoor dat de tekst van de debugmodus op het scherm wordt weergegeven
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


# Eerste wat er gebeurt als je de code uitvoert, voert main() uit (bovenaan de code)
if __name__ == '__main__':
    main()
    # cProfile.run("main()")
    # start(3, "alpha", 0)
