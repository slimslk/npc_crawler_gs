from pydantic import Field
from typing_extensions import Annotated

from dto.base_action_dto import BaseActionDto
from typing import Literal, Sequence, ClassVar

move_actions = Literal["move_up", "move_down", "move_left", "move_right"]
BoundedInt = Annotated[int, Field(ge=-1, le=1)]
Direction = Annotated[Sequence[BoundedInt], Field(min_length=2, max_length=2)]


class MovePlayerActionDTO(BaseActionDto):
    action: move_actions
    params_value: int | None = Field(gte=0, default=1)
    params_required: ClassVar[bool] = False


class TakeItemActionDTO(BaseActionDto):
    action: Literal["take_item"]
    params_value: Direction | None = None
    params_required: ClassVar[bool] = False


class ListItemsActionDTO(BaseActionDto):
    action: Literal["list_items"]
    params_value: int | None = Field(default=None, gt=0)
    params_required: ClassVar[bool] = False


class UseItemActionDTO(BaseActionDto):
    action: Literal["use_item"]
    params_value: int = Field(ge=0, default=1)


class AttackActionDTO(BaseActionDto):
    action: Literal["attack"]
    params_value: Direction
    params_required: ClassVar[bool] = False


class SkipTurnActionDTO(BaseActionDto):
    action: Literal["skip_turn"]
    params_value: None
    params_required: ClassVar[bool] = False


class AwakeTurnActionDTO(BaseActionDto):
    action: Literal["awake"]
    params_value: None
    params_required: ClassVar[bool] = False
