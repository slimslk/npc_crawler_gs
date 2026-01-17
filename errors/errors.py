class DefaultError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PlayerIsDeadError(DefaultError):
    def __init__(self, name):
        super().__init__(f'Player {name} has dead!')


# class InvalidActionNameError(DefaultError):
#     def __init__(self, name):
#         super().__init__(f'Invalid action name: {name}')


# class InvalidActionParametersError(DefaultError):
#     def __init__(self, name):
#         super().__init__(f'Invalid action name: {name}')


class ObjectPositionIsOutOfBoundsError(DefaultError):
    def __init__(self, name):
        super().__init__(f'Object position error {name}')


class PlayerPositionIsOutOfBoundsError(DefaultError):
    def __init__(self, name):
        super().__init__(f'Player position error: {name}')


class PositionIsOccupiedError(DefaultError):
    def __init__(self, name):
        super().__init__(f'Position is occupied: {name}')


class LocationNotFoundError(DefaultError):
    def __init__(self, location_id):
        super().__init__(f'Location not found: {location_id}')


class PlayerNotFoundError(DefaultError):
    def __init__(self, user_id):
        super().__init__(f'Player not found: {user_id}')


class GameMapConsumerError(DefaultError):
    def __init__(self, err):
        super().__init__({err})
