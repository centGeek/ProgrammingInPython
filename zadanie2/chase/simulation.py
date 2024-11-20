import json
import math
import os
import random

# Constants
MAX_ROUNDS = 50
NUMER_OF_SHEEPS = 15
DISTANCE_OF_WOLF_MOVEMENT = 1.0
DISTANCE_OF_SHEEP_MOVEMENT = 0.5
MAX_INIT_POSITION = 10.0
JSON_FILE_NAME = "pos.json"
CSV_FILE_NAME = "pos.json"


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

    def move(self, is_debug_prints: bool = False):
        direction = random.choice(["up", "down", "left", "right"])
        if is_debug_prints:
            print(f"{self.name} movement from {self.x} {self.y} :", direction)
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
        return f"{self.name} is at ({self.x:.3f},{self.y:.3f})"

    def get_position_tuple(self):
        return (self.x, self.y)

class Sheep(Animal):
    counter_of_Sheeps = 0

    def __init__(self, max_init_posiotion: float, jump_value: float):
        x, y = (random.uniform(-max_init_posiotion, max_init_posiotion),
                random.uniform(-max_init_posiotion, max_init_posiotion))

        Sheep.counter_of_Sheeps += 1
        self.number_of_sheep = Sheep.counter_of_Sheeps

        super().__init__(x, y, jump_value, f"Sheep {self.number_of_sheep}")


class Wolf(Animal):
    def __init__(self, jump_value: float, list_of_sheeps, name="Wolf"):
        x, y = 0, 0
        super().__init__(x, y, jump_value, name)
        self.list_of_sheeps = list_of_sheeps
        self.last_chasing_sheep = None

    def calc_square_distance_to_sheep(self, sheep: Sheep):
        return (self.x - sheep.x) ** 2 + (self.y - sheep.y) ** 2

    def move(self, is_debug_prints: bool = False):
        if self.list_of_sheeps:
            closest = min(self.list_of_sheeps,
                          key=lambda sheep: self.calc_square_distance_to_sheep(
                              sheep))
            dist = math.sqrt(self.calc_square_distance_to_sheep(closest))
            if dist <= self.jump_value:
                if is_debug_prints:
                    print(f"I ate the sheep at {closest.x} {closest.y}")
                self.list_of_sheeps.remove(closest)
                self.x = closest.x
                self.y = closest.y
                return closest.number_of_sheep
            else:
                if is_debug_prints:
                    print(f"{self.name} movement from {self.x} {self.y} :")
                self.last_chasing_sheep = closest

                dx = (closest.x - self.x) / dist
                dy = (closest.y - self.y) / dist

                self.x += dx * self.jump_value
                self.y += dy * self.jump_value
                return None

    def get_number_of_chasing_sheep(self):
        return self.last_chasing_sheep.number_of_sheep


def delete_prev_files():
    if os.path.exists(JSON_FILE_NAME):
        os.remove(JSON_FILE_NAME)
    if os.path.exists(CSV_FILE_NAME):
        os.remove(CSV_FILE_NAME)


# Main body
if __name__ == "__main__":
    delete_prev_files()
    round_counter = 1
    sheeps = []
    for i in range(NUMER_OF_SHEEPS):
        sheeps.append(
            Sheep(MAX_INIT_POSITION, DISTANCE_OF_SHEEP_MOVEMENT))
    wolf = Wolf(DISTANCE_OF_WOLF_MOVEMENT, sheeps)

    while round_counter <= MAX_ROUNDS:
        if sheeps:
            for sheep in sheeps:
                sheep.move(False)
        else:
            break
        eaten_sheep = wolf.move(False)

        #Write to Json
        with open(JSON_FILE_NAME, "w") as json_file:

            dict_round = {
                "round_no" : round_counter,
                "wolf_pos" : wolf.get_position_tuple(),
                "sheep_pos": [sheep.get_position_tuple() for sheep in sheeps],
            }

            json.dump(dict_round, json_file,ensure_ascii=False, indent=4)

        print(f"\nRound number: {round_counter}\n"
              f"{wolf.get_position_string()}\n"
              f"Number of alive Sheeps: {len(sheeps)}\n"
              f"The wolf is chasing sheep with number: {wolf.get_number_of_chasing_sheep()}"
              # TODO poprawić na to czy ściga
              )
        if eaten_sheep:
            print(f"The wolf eaten sheep number {eaten_sheep}")

        round_counter += 1
