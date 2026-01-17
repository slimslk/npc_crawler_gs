from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    __abstract__ = True


class CharStats(Base):
    __tablename__ = "char_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    health: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    energy: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    hungry: Mapped[int]
    position_x: Mapped[int]
    position_y: Mapped[int]
    inventory: Mapped[list] = mapped_column(JSONB, default=[])
    location_id: Mapped[str]
    attack_modifier: Mapped[int]
    attack_damage: Mapped[int]
    defence: Mapped[int]
    is_dead: Mapped[bool] = mapped_column(default=False)

    # Связь с персонажем (если нужно)
    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="stats",
        uselist=False
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    stats_id: Mapped[int | None] = mapped_column(ForeignKey("char_stats.id"), unique=True)
    user_id: Mapped[str | None] = mapped_column(String(120))

    stats: Mapped["CharStats"] = relationship(
        "CharStats",
        back_populates="character",
        uselist=False
    )
