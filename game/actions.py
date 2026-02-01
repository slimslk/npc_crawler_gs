from dto.game_action_dto import (
    CreatePlayerActionDTO,
    GetPlayerActionDTO,
    GetFullMapActionDTO,
    LogoutDTO
)
from dto.player_action_dto import (
    MovePlayerActionDTO,
    TakeItemActionDTO,
    ListItemsActionDTO,
    UseItemActionDTO,
    AttackActionDTO,
    SkipTurnActionDTO, AwakeTurnActionDTO,
)

actionDTOMapConfig = {
    "create_player": CreatePlayerActionDTO,
    "get_player": GetPlayerActionDTO,
    "get_full_map": GetFullMapActionDTO,
    "logout": LogoutDTO,

    "move_up": MovePlayerActionDTO,
    "move_down": MovePlayerActionDTO,
    "move_left": MovePlayerActionDTO,
    "move_right": MovePlayerActionDTO,
    "take_item": TakeItemActionDTO,
    "list_items": ListItemsActionDTO,
    "use_item": UseItemActionDTO,
    "attack": AttackActionDTO,
    "skip_turn": SkipTurnActionDTO,
    "awake": AwakeTurnActionDTO,
}

PLAYER_ACTIONS = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "take_item",
    "get_items_list",
    "use_item",
    "attack",
    "skip_turn",
    "awake",
]

GAME_ACTIONS = [
    "create_player",
    "get_full_map",
    "get_player",
    "logout"
]
