from typing import Any, ClassVar

from pydantic import BaseModel, model_validator

from errors.action_errors import IncorrectParameters


class BaseActionDto(BaseModel):
    action: str
    params_value: Any = None
    max_params: ClassVar[int] = 1
    params_required: ClassVar[bool] = True

    @model_validator(mode="before")
    @classmethod
    def get_params(cls, data):
        params = data.get("params_value", [])
        if isinstance(params, list):
            if len(params) > 0 or cls.params_required:
                try:
                    if cls.max_params == 1:
                        data["params_value"] = data["params_value"][0]
                    else:
                        data["params_value"] = data["params_value"][:cls.max_params]
                    return data
                except IndexError:
                    raise IncorrectParameters("Missing required parameters.")
            else:
                data["params_value"] = None
                return data
        else:
            raise IncorrectParameters("Params value must be list")
