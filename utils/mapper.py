from game.player import Player
from models.models import CharStats, Character


def player_stats_to_stats_model(player: Player) -> CharStats:
    return CharStats(
        health=player.health,
        energy=player.energy,
        hungry=player.hungry,
        position_x=player.pos_x,
        position_y=player.pos_y,
        inventory=player.inventory,
        location_id=player.world.map_id,
        attack_modifier=player.attack_modifier,
        attack_damage=player.attack_damage,
        defence=player.defence,
        is_dead=player.is_dead,
    )


def player_to_player_model(player: Player) -> Character:
    return Character(
        name=player.name,
        user_id=player.user_id,
    )


def character_model_to_player(character: Character) -> Player:
    player = Player(character.user_id, character.name)
    player.health = character.stats.health
    player.pos_x = character.stats.position_x
    player.pos_y = character.stats.position_y
    player.energy = character.stats.energy
    player.hungry = character.stats.hungry
    player.direction = (0, -1)
    player.inventory = character.stats.inventory
    player.is_dead = character.stats.is_dead
    player.defence = character.stats.defence
    player.attack_modifier = character.stats.attack_modifier
    player.attack_damage = character.stats.attack_damage
    return player

