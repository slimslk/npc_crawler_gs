from typing import Any, ClassVar

from pydantic import BaseModel, model_validator


class BaseActionDto(BaseModel):
    action: str
    params_value: Any = None
    max_params: ClassVar[int] = 1

    @model_validator(mode="before")
    @classmethod
    def get_params(cls, data):
        if isinstance(data.get("params_value"), list):
            if cls.max_params == 1:
                data["params_value"] = data["params_value"][0]
            else:
                data["params_value"] = data["params_value"][:cls.max_params]
        return data
