import math
import random

# Constants
MAX_ROUNDS = 50
NUMER_OF_SHEEPS = 15
DISTANCE_OF_WOLF_MOVEMENT = 1.0
DISTANCE_OF_SHEEP_MOVEMENT = 0.5
MAX_INIT_POSITION = 10.0


class Animal:
    def __init__(self, x: float, y: float, jump_value: float, name):
        """
         Init of an animal representation.
         :param x: position of the sheep in X
         :param y: position of the sheep in Y
         """
        self.x = x
        self.y = y
        self.jump_value = jump_value
        self.name = name

    def move(self):
        direction = random.choice(["up", "down", "left", "right"])
        match direction:
            case "up":
                self.y += self.jump_value
            case "down":
                self.y -= self.jump_value
            case "left":
                self.x -= self.jump_value
            case "right":
                self.x += self.jump_value

    def get_position_string(self):
        return f"{self.name} is at {self.x}, {self.y}"


class Sheep(Animal):
    counter_of_Sheeps = 0

    def __init__(self, max_init_posiotion: float, jump_value: float,name):
        x, y = (random.uniform(-max_init_posiotion, max_init_posiotion),
                random.uniform(-max_init_posiotion, max_init_posiotion))
        super().__init__(x, y, jump_value, name)
        Sheep.counter_of_Sheeps += 1


class Wolf(Animal):
    def __init__(self, jump_value: float, list_of_sheeps, name="Wolf"):
        x, y = 0, 0
        super().__init__(x, y, jump_value, name)
        self.list_of_sheeps = list_of_sheeps
        self.last_chasing_sheep = None

    def calc_square_distance_to_sheep(self, sheep: Sheep):
        return (self.x - sheep.x) ** 2 + (self.y - sheep.y) ** 2

    def move(self):
        if self.list_of_sheeps:
            closest = min(self.list_of_sheeps,
                          key=lambda sheep: self.calc_square_distance_to_sheep(
                              sheep))
            dist = math.sqrt(self.calc_square_distance_to_sheep(closest))
            if dist <= self.jump_value:
                print("I ate the sheep")
                self.list_of_sheeps.remove(closest)
                self.x = closest.x
                self.y = closest.y
            else:
                self.last_chasing_sheep = closest

                dx = (closest.x - self.x) / dist
                dy = (closest.y - self.y) / dist

                self.x += dx * self.jump_value
                self.y += dy * self.jump_value



# Main body
round_counter = 1
sheeps = []
for i in range(NUMER_OF_SHEEPS):
    sheeps.append(Sheep(MAX_INIT_POSITION, DISTANCE_OF_SHEEP_MOVEMENT,f"Sheep {i+1}"))
wolf = Wolf(DISTANCE_OF_WOLF_MOVEMENT, sheeps)
while True:
    if round_counter == MAX_ROUNDS:
        break
    if sheeps:
        for sheep in sheeps:
            sheep.move()
    else:
        break
    wolf.move()
    round_counter += 1
