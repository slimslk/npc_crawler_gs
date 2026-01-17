import copy
import random

from errors.errors import PositionIsOccupiedError
from game.item.dummy import Dummy
from game.item.grass import Grass
from game.item.meat import Meat
from game.item.red_potion import HealthPotion
from game.item.sword import Sword
from game.item.tree import Tree
from game.item.yellow_potion import EnergyPotion
from game.location import Location
from game.map import Map


async def add_objects_to_map_in_random_places(location, object_type, amount: int):
    i = 0
    tries = 0
    max_tries = 10
    while i < amount:
        tries += 1
        obj = copy.copy(object_type)
        loc_len, loc_width = location.get_location_size()
        pos_x = random.randint(0, loc_len - 1)
        pos_y = random.randint(0, loc_width - 1)
        try:
            await location.add_object_to_world(obj, pos_x, pos_y)
        except PositionIsOccupiedError:
            if tries > max_tries:
                i += 1
            continue
        i += 1


async def generate_main_location() -> Location:
    location_height = 100
    location_width = 100
    tree_coefficient = 0.2
    meet_coefficient = 0.015
    sword_coefficient = 0.001
    health_potion_coefficient = 0.005
    energy_potion_coefficient = 0.005
    dummy_coefficient = 0.002
    main_location = await generate_location(location_height, location_width, "Aisuron")
    tree = Tree()
    await add_objects_to_map_in_random_places(main_location, tree,
                                              int(location_height * location_width * tree_coefficient))
    meat = Meat()
    await add_objects_to_map_in_random_places(main_location, meat,
                                              int(location_height * location_width * meet_coefficient))
    sword = Sword()
    await add_objects_to_map_in_random_places(main_location, sword,
                                              int(location_height * location_width * sword_coefficient))
    dummy = Dummy()
    await add_objects_to_map_in_random_places(main_location, dummy,
                                              int(location_height * location_width * dummy_coefficient))
    hp_potion = HealthPotion()
    await add_objects_to_map_in_random_places(main_location, hp_potion,
                                              int(location_height * location_width * health_potion_coefficient))
    en_potion = EnergyPotion()
    await add_objects_to_map_in_random_places(main_location, en_potion,
                                              int(location_height * location_width * energy_potion_coefficient))
    return main_location


async def generate_location(height: int, width: int, name: str) -> Location:
    grass_map = [[[Grass()] for _ in range(width)] for _ in range(height)]
    main_map = Map(grass_map)
    location = Location(main_map, name)
    return location
