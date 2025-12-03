import inspect
import random

from game.item.corpse import Corpse
from game.map import Map
from game.item.def_object import DefaultObject
from game.errors import InvalidActionNameError, InvalidActionParametersError
from config.configuration import game_tick
from game.game_observer import GameObjectObserver


class Player:
    __MAX_HEALTH = 25
    __MAX_ENERGY = 100
    __MAX_HUNGRY = (10 * 60 * 1000) / game_tick  # The player can survive for 10 minutes with a full hunger bar.
    __is_solid: bool = True

    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.pos_x = 0
        self.pos_y = 0
        self.health = self.__MAX_HEALTH
        self.energy = self.__MAX_ENERGY
        self.hungry = self.__MAX_HUNGRY
        self.world: Map | None = None
        self.direction = (0, -1)
        self.inventory: list[DefaultObject] = []
        self.is_dead = False
        self.defence = 8
        self.attack_modifier = 0
        self.attack_damage = 4
        self.skip_counter = 0
        self.observers: set[GameObjectObserver] = set()

    def add_observer(self, observer: GameObjectObserver):
        self.observers.add(observer)

    def remove_observer(self, observer: GameObjectObserver):
        self.observers.remove(observer)

    def is_solid(self):
        return self.__is_solid

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def set_direction(self, x, y):
        x = 1 if x > 0 else (-1 if x < 0 else 0)
        y = 1 if y > 0 else (-1 if y < 0 else 0)
        self.direction = (x, y)

    def get_defence(self):
        return self.defence

    async def set_defence(self, defence: int):
        self.defence = defence
        await self.notify_observers()

    async def set_map(self, world: Map):
        self.world = world
        await self.notify_observers()

    async def increase_hungry(self, amount: int):
        amount = int(amount)
        self.hungry -= amount
        if self.hungry < 0:
            self.hungry = 0
            await self.decrease_health(5)
        if self.hungry % 100 == 0:
            await self.notify_observers()

    async def decrease_hungry(self, amount: int):
        amount = int(amount)
        self.hungry += amount
        if self.hungry > self.__MAX_HUNGRY:
            self.hungry = self.__MAX_HUNGRY
        await self.notify_observers()

    async def decrease_energy(self, amount: int):
        amount = int(amount)
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0
        # if self.energy == 100*0.75:
        #     await self.notify_observers()
        # if self.energy == 100*0.5:
        #     await self.notify_observers()
        # if self.energy == 100*0.25:
        #     await self.notify_observers()
        # if self.energy < 100 * 0.1:
        #     await self.notify_observers()
        await self.notify_observers()

    async def increase_energy(self, amount: int):
        amount = int(amount)
        self.energy += amount
        if self.energy > self.__MAX_ENERGY:
            self.energy = self.__MAX_ENERGY
        await self.notify_observers()

    async def decrease_health(self, amount: int):
        amount = int(amount)
        self.health -= amount
        if self.health <= 0:
            await self.process_death()
        await self.notify_observers()

    async def increase_health(self, amount: int):
        amount = int(amount)
        self.health += amount
        if self.health > self.__MAX_HEALTH:
            self.health = self.__MAX_HEALTH
        await self.notify_observers()

    """
    Right: (0, 1)
    Left: (0, -1)
    Down: (1, 0)
    Up: (-1, 0)
    Diagonals: (1, 1), (1, -1) , (-1, 1), (-1, -1)"""

    async def move(self, direction: tuple[int, int], steps: int):
        steps = int(steps)
        if self.energy <= 0:
            return

        self.set_direction(direction[0], direction[1])
        await self.decrease_energy(1)

        steps_count = 0
        old_pos_x = self.pos_x
        old_pos_y = self.pos_y

        for _ in range(steps):
            self.pos_x += direction[0]
            self.pos_y += direction[1]
            if (self.pos_x < 0 or self.pos_y < 0 or
                    self.pos_x > (self.world.get_map_size()[0] - 1) or (self.pos_y > self.world.get_map_size()[1] - 1)):
                self.pos_x -= direction[0]
                self.pos_y -= direction[1]
                break
            steps_count += 1
            if self.world.get_first_object(self.pos_x, self.pos_y).is_solid():
                if steps_count > 1:
                    self.health -= (steps_count - 1) * 10
                self.pos_x -= direction[0]
                self.pos_y -= direction[1]
                break

        if old_pos_x != self.pos_x or old_pos_y != self.pos_y:
            await self.notify_observers()
            await self.world.move_player(self, old_pos_x, old_pos_y, self.pos_x, self.pos_y)

    async def take_object(self, direction: tuple[int, int] = None):
        await self.decrease_energy(1)
        if direction:
            x = self.pos_x + direction[0]
            y = self.pos_y + direction[1]
        else:
            x = self.pos_x + self.direction[0]
            y = self.pos_y + self.direction[1]
        item = self.world.get_first_object(x, y)
        if item.is_collectable():
            await item.get_world_map().remove_first_object(x, y)
            item.set_position(-1, -1)
            self.inventory.append(item)
            await self.notify_observers()

    def show_list_of_items(self, amount=-1):
        amount = int(amount)
        if not len(self.inventory):
            return "-" * 10
        return ", ".join([f"{index}: {item.get_name()}" for
                          index, item in enumerate(self.inventory[0:amount], start=1)])

    async def use_item(self, index):
        index = int(index)
        if index >= len(self.inventory):
            await self.do_nothing()
        else:
            await self.decrease_energy(1)
            item = self.inventory[index]
            action = item.use()
            if item.is_consumable():
                self.inventory.pop(index)
            await self.do_action(action)
        await self.notify_observers()

    async def attack(self, power: tuple[int, int] = (0, 4), direction: tuple[int, int] = None):
        await self.decrease_energy(1)
        if direction:
            obj = self.world.get_first_object(self.pos_x + direction[0], self.pos_y + direction[1])
        else:
            obj = self.world.get_first_object(self.pos_x + self.direction[0], self.pos_y + self.direction[1])
        if power:
            attack_power = random.randint(1, 20) + power[0]
            damage = random.randint(1, power[1])
        else:
            attack_power = random.randint(1, 20) + self.attack_modifier
            damage = random.randint(1, self.attack_damage)
        if isinstance(obj, Player):
            if obj.defence < attack_power:
                await obj.decrease_health(damage)
        if isinstance(obj, DefaultObject):
            await obj.decrease_hp(damage)
        await self.notify_observers()

    async def skip_turn(self):
        if self.skip_counter <= (5 * 1000) / game_tick:
            self.skip_counter += 1
        else:
            await self.increase_energy(1)
            self.skip_counter = 0

    async def do_nothing(self):
        await self.skip_turn()

    async def do_action(self, action: dict):
        await self.increase_hungry(1)
        if self.__check_is_player_dead():
            return None
        action_name = action.get("action", "do_nothing")
        if action_name != "skip_turn":
            self.skip_counter = 0
        method = getattr(self, action_name, "do_nothing")
        if method is not None and callable(method):
            try:
                if inspect.iscoroutinefunction(method):
                    result = await method(*action.get("params", []))
                else:
                    result = method(*action.get("params", []))
            except TypeError:
                raise InvalidActionParametersError(
                    f"action_name: {action.get(action_name)}, params: {action.get("params")}"
                )
        else:
            raise InvalidActionNameError(action_name)
        return result

    def get_player_parameters(self):
        return {
            "id": self.id,
            "name": self.name,
            "health": self.health,
            "energy": self.energy,
            "hungry": self.hungry,
            "position": (self.pos_x, self.pos_y),
            "direction": self.direction,
            "inventory": [item.name for item in self.inventory],
            "location_id": self.world.map_id,
            "attack_modifier": self.attack_modifier,
            "attack_damage": self.attack_damage,
            "defence": self.defence,
            "is_dead": self.is_dead
        }

    async def process_death(self):
        corpse = Corpse()
        corpse.corpse_name = self.name
        await self.world.replace_object(corpse, self.pos_x, self.pos_y)
        self.is_dead = True
        for item in self.inventory:
            x = self.pos_x
            y = self.pos_y
            while (x == self.pos_x and y == self.pos_y) or self.world.location_map[x][y][0].is_solid():
                x = self.pos_x + random.randint(0, 1)
                y = self.pos_y + random.randint(0, 1)
            await self.world.place_object(item, x, y)
        self.inventory = []

    def __check_is_player_dead(self) -> bool:
        return self.is_dead

    def __str__(self):
        return f"Player: {self.name}"

    async def notify_observers(self):
        data = {self.id: self.get_player_parameters()}
        for observer in self.observers:
            await observer.update(data)
