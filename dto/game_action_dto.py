from typing import Literal, ClassVar

from pydantic import Field

from dto.base_action_dto import BaseActionDto


class CreatePlayerActionDTO(BaseActionDto):
    action: Literal["create_player"]
    params_value: str = Field(min_length=3)


class GetPlayerActionDTO(BaseActionDto):
    action: Literal["get_player"]
    params_value: str = Field(min_length=3)


class GetFullMapActionDTO(BaseActionDto):
    action: Literal["get_full_map"]
    params_value: str = Field(min_length=1)
    params_required: ClassVar[bool] = False


class LogoutDTO(BaseActionDto):
    action: Literal["logout"]
    params_value: None
    params_required: ClassVar[bool] = False
