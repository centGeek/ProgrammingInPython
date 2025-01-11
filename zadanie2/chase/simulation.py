import argparse
import configparser
import csv
import json
import math
import random
import logging
import os

# Constants OR Global Var
MAX_ROUNDS = 50
NUMBER_OF_SHEEP = 15
DISTANCE_OF_SHEEP_MOVEMENT = 0.5
DISTANCE_OF_WOLF_MOVEMENT = 1.0
MAX_INIT_POSITION = 10.0
CONFIG_FILE_NAME = ""
JSON_FILE_NAME = "pos.json"
CSV_FILE_NAME = "alive.csv"

logger = None


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
        # dead sheep cannot move
        if self.x is not None:
            direction = random.choice(["up", "down", "left", "right"])
            logger.debug("%s chooses direction: %s", self.name, direction)
            match direction:
                case "up":
                    self.y += self.jump_value
                case "down":
                    self.y -= self.jump_value
                case "left":
                    self.x -= self.jump_value
                case "right":
                    self.x += self.jump_value
            logger.debug("%s moves to (%f,%f)", self.name, self.x, self.y)

    def get_position_string(self):
        return f"{self.name} is at ({self.x:.3f},{self.y:.3f})"

    def get_position_tuple(self):
        # optimization
        if self.x is not None:
            return self.x, self.y
        else:
            return None


class Sheep(Animal):
    # dead sheep are counted too
    counter_of_sheep = 0
    # only alive sheep counter
    alive_sheep = 0

    def __init__(self, max_init_posiotion: float, jump_value: float):
        x, y = (random.uniform(-max_init_posiotion, max_init_posiotion),
                random.uniform(-max_init_posiotion, max_init_posiotion))

        Sheep.counter_of_sheep += 1
        self.number_of_sheep = Sheep.counter_of_sheep
        Sheep.alive_sheep += 1

        super().__init__(x, y, jump_value, f"Sheep {self.number_of_sheep}")
        logger.debug("%s initialized at: (%f,%f)",
                     self.name, self.x, self.y)


class Wolf(Animal):
    def __init__(self, jump_value: float, list_of_sheep, name="Wolf"):
        x, y = 0, 0
        super().__init__(x, y, jump_value, name)
        self.list_of_sheep = list_of_sheep
        self.last_chasing_sheep = None

    def calc_square_distance_to_sheep(self, sheep: Sheep):
        if sheep.x is not None:
            return (self.x - sheep.x) ** 2 + (self.y - sheep.y) ** 2
        else:
            # Thanks to that dead sheep is never considered to be the closest
            return float('inf')

    def kill_sheep(self, sheep: Sheep):
        sheep.x = None
        sheep.y = None
        Sheep.alive_sheep -= 1

    def move(self):
        closest = min(self.list_of_sheep,
                      key=lambda sheep: self.calc_square_distance_to_sheep(
                          sheep))
        dist = math.sqrt(self.calc_square_distance_to_sheep(closest))
        logger.debug("%s is closest to %s, distance %f", self.name,
                     closest.name, dist)
        if dist <= self.jump_value:
            self.x = closest.x
            self.y = closest.y

            self.kill_sheep(closest)
            self.last_chasing_sheep = None
            logger.debug("%s moved to (%f,%f)", self.name, self.x, self.y)
            return closest
        else:
            self.last_chasing_sheep = closest
            logger.info("%s is chasing %s", self.name, closest.name)

            dx = (closest.x - self.x) / dist
            dy = (closest.y - self.y) / dist

            self.x += dx * self.jump_value
            self.y += dy * self.jump_value
            logger.debug("%s moved to (%f,%f)", self.name, self.x, self.y)
            return None

    def get_number_of_chasing_sheep(self):
        return self.last_chasing_sheep.number_of_sheep


def delete_and_init_files():
    try:
        with open(JSON_FILE_NAME, "w") as json_file:
            json.dump([], json_file)
            logger.debug("Empty collection saved to json")

        with open(CSV_FILE_NAME, "w", newline='') as csv_file:
            csv.writer(csv_file).writerow(
                ["Number of round", "Alive sheep"])
            logger.debug("Header saved to csv")

    except IOError:
        logger.error("An error occurred when preparing files")


def add_to_json(round_counter, wolf, sheep):
    try:
        with open(JSON_FILE_NAME, "r") as json_file:
            json_data = json.load(json_file)
    except IOError:
        logger.error("Error occurred with reading json")
    try:
        with open(JSON_FILE_NAME, "w") as json_file:
            dict_round = {
                "round_no": round_counter,
                "wolf_pos": wolf.get_position_tuple(),
                "sheep_pos": [_sheep.get_position_tuple() for _sheep in sheep],
            }
            json_data.append(dict_round)
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            logger.debug("Data saved into json")
    except IOError:
        logger.error("Error occurred with writing to json")


def add_to_csv(round_counter, alive_sheep):
    try:
        with open(CSV_FILE_NAME, "a", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([f"{round_counter}", f"{alive_sheep}"])
            logger.debug("Data saved into csv")
    except IOError:
        logger.error("Error occurred with appending to csv")


def get_logger(logging_level):
    if logging_level is None:
        _logger = logging.getLogger()
        _logger.addHandler(logging.NullHandler())
        return _logger
    logging.basicConfig(filename="chase.log",
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filemode="w")
    _logger = logging.getLogger()
    _logger.setLevel(logging_level)
    return _logger


def load_config(config_path):
    if config_path is None:
        return None
    try:
        config = configparser.ConfigParser()
        config.read(config_path)

        max_init_pos_to_check = config['Sheep']['InitPosLimit']
        dist_of_sheep_mov = config['Sheep']['MoveDist']

        dist_of_wolf_mov = config['Wolf']['MoveDist']

        try:
            max_init_pos_to_check = float(max_init_pos_to_check)
        except ValueError:
            raise configparser.Error(
                "InitPosLimit in config must be a number!")
        if max_init_pos_to_check <= 0:
            raise configparser.Error(
                "InitPosLimit in config must be greater than 0")

        try:
            dist_of_sheep_mov = float(dist_of_sheep_mov)
        except ValueError:
            raise configparser.Error(
                "MoveDist for sheep in config must be a number!")
        if dist_of_sheep_mov <= 0:
            raise configparser.Error(
                "MoveDist for sheep in config must be greater than 0")
        try:
            dist_of_wolf_mov = float(dist_of_wolf_mov)
        except ValueError:
            raise configparser.Error(
                "MoveDist for wolf in config must be a number!")
        if dist_of_wolf_mov <= 0:
            raise configparser.Error(
                "MoveDist for wolf in config must be greater than 0")

        global MAX_INIT_POSITION, DISTANCE_OF_SHEEP_MOVEMENT, DISTANCE_OF_WOLF_MOVEMENT

        MAX_INIT_POSITION = max_init_pos_to_check
        DISTANCE_OF_SHEEP_MOVEMENT = dist_of_sheep_mov
        DISTANCE_OF_WOLF_MOVEMENT = dist_of_wolf_mov

        logger.debug(
            "Config loaded successfully, loaded data: "
            "Sheep:[InitPosLimit %f, MoveDist %f] "
            "Wolf:[MoveDist %f]", MAX_INIT_POSITION,
            DISTANCE_OF_SHEEP_MOVEMENT, DISTANCE_OF_WOLF_MOVEMENT)
    except KeyError:
        DISTANCE_OF_WOLF_MOVEMENT = 1.0
        DISTANCE_OF_SHEEP_MOVEMENT = 0.5
        MAX_INIT_POSITION = 10.0
        logging.critical("Config file was corrupted, default values applied")


def validate_config(file_path):
    if not file_path.endswith(".ini"):
        raise argparse.ArgumentTypeError("Config file must be a .ini file")
    try:
        with open(file_path, "r") as _:
            return file_path
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"File '{file_path}' does not exist")
    except IOError:
        raise argparse.ArgumentTypeError(
            f"File '{file_path}' cannot be opened")


def positive_int_rounds(val):
    try:
        int_value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Number of rounds should be NUMBER not text")
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            "Number of rounds should be positive integer.")
    return int_value


def positive_int_sheep(val):
    try:
        int_value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Number of sheep should be NUMBER not text")
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            "Number of sheep should be positive integer.")
    return int_value


def argument_parse():
    global NUMBER_OF_SHEEP, MAX_ROUNDS

    parser = argparse.ArgumentParser(description="Chase sheep simulation.")

    parser.add_argument("-c", "--config", type=validate_config,
                        help="Path to .ini config file", metavar="FILE")

    parser.add_argument("-l", "--log",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR",
                                 "CRITICAL"],
                        help="Logging level should be one of "
                             "[DEBUG, INFO, WARNING, ERROR, CRITICAL]",
                        metavar="LEVEL")

    parser.add_argument("-r", "--rounds", type=positive_int_rounds,
                        default=MAX_ROUNDS, help="Number of rounds",
                        metavar="NUM")

    parser.add_argument("-s", "--sheep", type=positive_int_sheep,
                        default=NUMBER_OF_SHEEP, help="Number of sheep",
                        metavar="NUM")

    parser.add_argument("-w", "--wait", action="store_true",
                        help="Pauses program after each round,"
                             " waiting for any keyboard input.")

    args = parser.parse_args()

    log_levels_dict = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }

    args.log = log_levels_dict.get(args.log, None)

    if args.sheep:
        NUMBER_OF_SHEEP = args.sheep
    if args.rounds:
        MAX_ROUNDS = args.rounds

    return args


def main():
    args = argument_parse()
    global logger
    logger = get_logger(args.log)
    load_config(args.config)

    delete_and_init_files()
    round_counter = 1
    sheep = [Sheep(MAX_INIT_POSITION, DISTANCE_OF_SHEEP_MOVEMENT) for _ in
             range(NUMBER_OF_SHEEP)]
    logger.info("Position of all sheep were determined")
    wolf = Wolf(DISTANCE_OF_WOLF_MOVEMENT, sheep)

    while True:
        if round_counter > MAX_ROUNDS:
            logger.info("Simulation terminated as max "
                        "number of rounds have been reached")
            break
        if Sheep.alive_sheep > 0:
            logger.info("Round %d started", round_counter)
            for _sheep in sheep:
                _sheep.move()
        else:
            logger.info("Simulation terminated as all sheep have been eaten")
            break
        logger.info("All alive sheep moved")

        eaten_sheep = wolf.move()

        logger.info("Wolf has moved")

        add_to_json(round_counter, wolf, sheep)
        add_to_csv(round_counter, Sheep.alive_sheep)

        print(f"\nRound number: {round_counter}\n"
              f"{wolf.get_position_string()}\n"
              f"Number of alive Sheep: {Sheep.alive_sheep}"
              )
        if wolf.last_chasing_sheep:
            print(
                f"The wolf is chasing sheep with number:"
                f" {wolf.get_number_of_chasing_sheep()}")
        if eaten_sheep:
            print(f"The wolf has eaten {eaten_sheep.name}")
            logger.info("%s was eaten", eaten_sheep.name)
        logger.info("End of round %d, alive sheep: %d", round_counter,
                    Sheep.alive_sheep)
        if args.wait:
            # input("\nFor next round press any key\n")
            os.system('pause')
        round_counter += 1


# Main body
if __name__ == "__main__":
    main()
