from pydantic import BaseModel

# from config.settings import KafkaSettings, Settings


def build_from_settings(*, base,
                        settings,
                        prefix: str,
                        model: type[BaseModel], ) -> BaseModel:
    data = {"base": base}
    for field in model.model_fields.keys():
        if field == "base":
            continue

        settings_key = f"{prefix}_{field}"
        if hasattr(settings, settings_key):
            data[field] = getattr(settings, settings_key)

    return model.model_validate(data)
