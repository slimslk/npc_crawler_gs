from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from db.db import db_helper
from models.models import Character
from game.player import Player
from utils.mapper import player_to_player_model, player_stats_to_stats_model


class CharacterRepository:
    def __init__(self):
        pass

    async def create(self, player: Player) -> Character | None:

        stats = player_stats_to_stats_model(player)
        character = player_to_player_model(player)
        print(f"character: {character}, stats: {stats}")
        async for session in db_helper.session_getter():
            try:
                session.add(stats)
                await session.flush()

                character.stats_id = stats.id
                session.add(character)
                await session.commit()
                await session.refresh(character)
                # player.character_id = character.id
                print(f"created character: {character}")
                return character
            except Exception as e:
                session.rollback()
                print(e)
                return None

    async def list_all_by_user_id(self, user_id: str) -> list[Character]:
        async for session in db_helper.session_getter():
            stm = select(Character).where(Character.user_id.__eq__(user_id)).options(selectinload(Character.stats))
            result = await session.execute(stm)
            return result.scalars().all()

    async def get_by_user_id_and_character_name(self, user_id: str, char_name: str) -> Character:
        async for session in db_helper.session_getter():
            stm = (
                select(Character)
                .where(
                    Character.user_id == user_id,
                    Character.name == char_name,
                )
                .options(selectinload(Character.stats))
            )
            result = await session.execute(stm)
            return result.scalar_one_or_none()

    async def list_all(self) -> list[Character]:
        async for session in db_helper.session_getter():
            result = await session.execute(
                select(Character).options(selectinload(Character.stats))
            )
            return result.scalars().all()

    async def update_stats(self, player: Player) -> Character | None:
        async for session in db_helper.session_getter():
            try:
                result = await session.execute(
                    select(Character)
                    .where(Character.name == player.name)
                    .options(selectinload(Character.stats))
                )
                character: Character = result.scalar_one_or_none()
                if not character:
                    return None

                self._update_stats(character, player)

                await session.commit()
                await session.refresh(character)
                return character
            except SQLAlchemyError as e:
                session.rollback()

    def _update_stats(self, character: Character, player: Player) -> Character:
        stats = character.stats
        stats.health = player.health
        stats.energy = player.energy
        stats.hungry = player.hungry
        stats.position_x = player.pos_x
        stats.position_y = player.pos_y
        stats.inventory = player.inventory
        stats.location_id = player.world.map_id
        stats.attack_modifier = player.attack_modifier
        stats.attack_damage = player.attack_damage
        stats.defence = player.defence
        stats.is_dead = player.is_dead
        return character

    async def delete(self, username: str, char_name: str) -> bool:
        async for session in db_helper.session_getter():
            try:
                result = await session.execute(
                    select(Character)
                    .where(Character.user_id == username,
                        Character.name == char_name,
                           )
                    .options(selectinload(Character.stats))
                )
                character = result.scalar_one_or_none()
                if not character:
                    return False

                await session.delete(character.stats)
                await session.delete(character)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
