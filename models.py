from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, TEXT
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PHASES_DESC:
    start_game = 1
    in_game = 2
    game_over = 3
    winner = 4


PHASE_TEXT = {
    PHASES_DESC.start_game: 'Старт игры',
    PHASES_DESC.in_game: 'В процессе игры',
    PHASES_DESC.game_over: 'Смерть персонажа',
    PHASES_DESC.winner: 'Победа в игре',
}


class Phases(Base):
    __tablename__ = "phases"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)


class Monsters(Base):
    __tablename__ = "monster"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    damage = Column(Integer, nullable=False)
    drop_item_id = Column(Integer,
                          ForeignKey('items.item_id', ondelete='CASCADE', name="fk_monster_to_items"),
                          nullable=False, index=True)

    drop_item = relationship("Items")


class Npc(Base):
    __tablename__ = "npc_list"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False, index=True)
    dialog = relationship("NpcDialogs", back_populates="npc")


class NpcDialogs(Base):
    __tablename__ = "npc_text"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    text = Column(TEXT, nullable=False)
    phase_id = Column(Integer,
                      ForeignKey('phases.id', ondelete='CASCADE', name="fk_npc_text_to_phases"),
                      nullable=False, index=True)
    npc_id = Column(Integer,
                    ForeignKey('npc_list.id', ondelete='CASCADE', name="fk_npc_text_to_npc_list"),
                    nullable=False, index=True)

    npc = relationship("Npc", back_populates="dialog")


class Items(Base):
    __tablename__ = "items"

    item_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    heal_power = Column(Integer, nullable=False)


class ProtagonistDB(Base):
    __tablename__ = "players"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    hp = Column(Integer, nullable=False, default=10)
    inventory = relationship("InventoryDB", back_populates="player")


class InventoryDB(Base):
    __tablename__ = "inventory"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    player_id = Column(Integer,
                       ForeignKey('players.id', ondelete='CASCADE', name="fk_inventory_to_players"),
                       nullable=False, index=True)
    item_id = Column(Integer,
                     ForeignKey('items.item_id', ondelete='CASCADE', name="fk_inventory_to_items"),
                     nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)
    player = relationship("ProtagonistDB", back_populates="inventory")
    item = relationship("Items")
