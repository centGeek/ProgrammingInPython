import csv
import json
import math
import random
from asyncio.windows_events import INFINITE

# Constants
MAX_ROUNDS = 50
NUMER_OF_SHEEPS = 15
DISTANCE_OF_WOLF_MOVEMENT = 1.0
DISTANCE_OF_SHEEP_MOVEMENT = 0.5
MAX_INIT_POSITION = 10.0
JSON_FILE_NAME = "pos.json"
CSV_FILE_NAME = "alive.csv"


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
        if self.x is not None:
            direction = random.choice(["up", "down", "left", "right"])
            if is_debug_prints:
                print(f"{self.name} movement from {self.x} {self.y} :",
                      direction)
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
        # optimization
        if self.x is not None:
            return self.x, self.y
        else:
            return None


class Sheep(Animal):
    # dead sheeps are counted
    counter_of_Sheeps = 0
    # only alive sheeps counter
    alive_sheeps = 0

    def __init__(self, max_init_posiotion: float, jump_value: float):
        x, y = (random.uniform(-max_init_posiotion, max_init_posiotion),
                random.uniform(-max_init_posiotion, max_init_posiotion))

        Sheep.counter_of_Sheeps += 1
        self.number_of_sheep = Sheep.counter_of_Sheeps
        Sheep.alive_sheeps += 1

        super().__init__(x, y, jump_value, f"Sheep {self.number_of_sheep}")


class Wolf(Animal):
    def __init__(self, jump_value: float, list_of_sheeps, name="Wolf"):
        x, y = 0, 0
        super().__init__(x, y, jump_value, name)
        self.list_of_sheeps = list_of_sheeps
        self.last_chasing_sheep = None

    def calc_square_distance_to_sheep(self, sheep: Sheep):
        if sheep.x is not None:
            return (self.x - sheep.x) ** 2 + (self.y - sheep.y) ** 2
        else:
            # Thanks to that this sheep is never considered to be the closest
            return float('inf')

    def kill_sheep(self, sheep: Sheep):
        sheep.x = None
        sheep.y = None
        Sheep.alive_sheeps -= 1

    def move(self, is_debug_prints: bool = False):
        if self.list_of_sheeps:
            closest = min(self.list_of_sheeps,
                          key=lambda sheep: self.calc_square_distance_to_sheep(
                              sheep))
            dist = math.sqrt(self.calc_square_distance_to_sheep(closest))
            if dist <= self.jump_value:
                self.x = closest.x
                self.y = closest.y
                # self.list_of_sheeps.remove(closest)
                if is_debug_prints:
                    print(f"I ate the sheep at {closest.x} {closest.y}")
                self.kill_sheep(closest)
                self.last_chasing_sheep = None
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


def delete_and_init_files():
    try:
        with open(JSON_FILE_NAME, "w") as json_file:
            json.dump([], json_file)
        with open(CSV_FILE_NAME, "w",newline='') as csv_file:
            csv.writer(csv_file).writerow(
                ["Number of round", "Alive sheeps"])
    except IOError:
        print("Error occurred with file")


def add_to_json(round_counter, wolf, sheeps):
    with open(JSON_FILE_NAME, "r") as json_file:
        json_data = json.load(json_file)

    with open(JSON_FILE_NAME, "w") as json_file:
        dict_round = {
            "round_no": round_counter,
            "wolf_pos": wolf.get_position_tuple(),
            "sheep_pos": [sheep.get_position_tuple() for sheep in sheeps],
        }
        json_data.append(dict_round)
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


def add_to_csv(round_counter, alive_sheeps):
    with open(CSV_FILE_NAME, "a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([f"{round_counter}", f"{alive_sheeps}"])



# Main body
if __name__ == "__main__":
    delete_and_init_files()
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

        add_to_json(round_counter, wolf, sheeps)
        add_to_csv(round_counter, Sheep.alive_sheeps)

        print(f"\nRound number: {round_counter}\n"
              f"{wolf.get_position_string()}\n"
              f"Number of alive Sheeps: {Sheep.alive_sheeps}"
              )
        if wolf.last_chasing_sheep:
            print(
                f"The wolf is chasing sheep with number: {wolf.get_number_of_chasing_sheep()}")
        if eaten_sheep:
            print(f"The wolf eaten sheep number {eaten_sheep}")

        round_counter += 1
