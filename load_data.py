from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Npc, NpcDialogs, Phases, PHASE_TEXT, PHASES_DESC, Items, Monsters

engine = create_engine("sqlite:///test.sqlite", echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


class Monster:
    pass


with Session(engine) as session:
    phases = []
    for ph, pht in PHASE_TEXT.items():
        phases.append(Phases(
            id=ph,
            name=pht
        ))

    session.add_all(phases)

    npc_1 = Npc(name="Сумасшедший житель",
                dialog=[
                    NpcDialogs(
                        text="Привет, помоги мне!",
                        phase_id=PHASES_DESC.start_game),
                    NpcDialogs(
                        text="Давай, давай!",
                        phase_id=PHASES_DESC.in_game),
                    NpcDialogs(
                        text="Ой блин, попробуешь еще раз?",
                        phase_id=PHASES_DESC.game_over),
                    NpcDialogs(
                        text="Ура, ты победил!",
                        phase_id=PHASES_DESC.winner)
                ])

    session.add(npc_1)

    session.commit()

    item1 = Items(name="Зелье малого исцеления", heal_power=1)
    session.add(item1)

    item2 = Items(name="Зелье большого исцеления", heal_power=4)
    session.add(item2)
    session.flush()

    item3 = Items(name="Хвост дракона", heal_power=0)
    session.add(item3)
    session.flush()

    monster1 = Monsters(name="Крыса", damage=1, drop_item_id=item1.item_id)
    monster2 = Monsters(name="Волк", damage=3, drop_item_id=item2.item_id)
    monster3 = Monsters(name="Дракон", damage=5, drop_item_id=item3.item_id)

    session.add(monster1)
    session.add(monster2)
    session.add(monster3)

    session.commit()
