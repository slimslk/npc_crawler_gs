from game.player import Player


class PlayerController:

    def __init__(self, player: Player):
        self.__player = player

    def get_player(self):
        return self.__player

    async def move_up(self, steps: int = 1):
        action = {"action": "move", "params": [(-1, 0), steps]}
        await self.__do_action(action)

    async def move_down(self, steps: int = 1):
        action = {"action": "move", "params": [(1, 0), steps]}
        await self.__do_action(action)

    async def move_left(self, steps: int = 1):
        action = {"action": "move", "params": [(0, -1), steps]}
        await self.__do_action(action)

    async def move_right(self, steps: int = 1):
        action = {"action": "move", "params": [(0, 1), steps]}
        await self.__do_action(action)

    async def take_item(self):
        action = {"action": "take_object", "params": []}
        await self.__do_action(action)

    async def get_items_list(self):
        action = {"action": "show_list_of_items", "params": []}
        await self.__do_action(action)

    async def use_item(self, index: int):
        action = {"action": "use_item", "params": [index]}
        await self.__do_action(action)

    async def attack(self):
        action = {"action": "attack"}
        await self.__do_action(action)

    async def skip_turn(self):
        action = {"action": "skip_turn", "params": []}
        await self.__do_action(action)

    def get_player_info(self):
        return self.__player.get_player_parameters()

    async def __do_action(self, action):
        return await self.__player.do_action(action)

# Activities: {"action": "move", "params": [(0,1), 1]} - move right one step
# Activities: {"action": "take_object", "params": []} - take item in front of you
# Activities: {"action": "show_list_of_items", "params": []} - move right one step
# Activities: {"action": "use_item", "params": [1]} - use item under index 1
# Activities: {"action": "attack", "params": [(0,1)]} - attack in front of the player with power and damage
# Activities: {"action": "skip_turn", "params": []} - skip turn and restore 1 energy
