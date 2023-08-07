"""
Порядок запуска
1. Поставить зависимости из requirements.txt
2. Загрузить исходные данные в БД
    python load_data.py
3. Запустить игру
    python protogonist.py
    ...
    повторить запуск несколько раз, будет загружаться предыдущее сохранение
"""

import random

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session

from models import ProtagonistDB, InventoryDB, PHASES_DESC, Npc, Monsters

TEST_ITEM = {
    "item_id": 1,
    "name": "Flask",
    "power": 2,
}

TEST_INVENTORY = {
    "item": TEST_ITEM,
    "count": 2
}


class NPC:
    def __init__(self, npc_id, session):
        self.session = session
        self.npc_id = npc_id
        self.name = 'NPC not found in DB'
        self.messages = {}
        self.load()

    def load(self):
        npc = self.session.get(Npc, self.npc_id)
        if not npc:
            raise Exception('NPC не найден в БД')

        print('#### Загрузка NPC: {}'.format(npc.name))
        self.name = npc.name
        self.messages = {}
        for message in npc.dialog:
            phase_id = message.phase_id
            if phase_id not in self.messages:
                self.messages[phase_id] = []

            self.messages[phase_id].append(message.text)

    def say_smth(self, phase=PHASES_DESC.start_game):
        phase_messages = self.messages.get(phase)
        if phase_messages:
            return phase_messages[0]

        return "Nothing to say"


class Enemy:
    def __init__(self, id, session):
        self.session = session
        self.id = id
        self.name = 'Enemy not loaded'
        self.damage = 1
        self.drop = TEST_ITEM
        self.load()

    def load(self):
        enemy = self.session.get(Monsters, self.id)
        if not enemy:
            raise Exception('Monster не найден в БД')

        print('#### Загрузка монстра: {}'.format(enemy.name))
        self.name = enemy.name
        self.damage = enemy.damage
        self.drop = {
            'name': enemy.drop_item.name,
            'item_id': enemy.drop_item.item_id,
            'power': enemy.drop_item.heal_power
        }

    def attack(self):
        att = random.randint(1, 6)
        return att

    def get_drop(self):
        # print("drop 40: ", self.drop)
        return self.drop


class Direction:
    pass


class Inventory:
    def __init__(self, player_id, session):
        self.session = session
        self.player_id = player_id
        self.items = {}
        self.load()

    def clear(self):
        self.items = {}

    def get(self, item_id):
        # print("get", self.items)
        item = self.items.get(item_id)
        if item is None:
            return None
        if item["count"] > 0:
            item["count"] -= 1
            if item["count"] == 0:
                del self.items[item_id]
        return item["item"]

    def put(self, item):
        item_id_ = item["item_id"]
        itm = self.items.get(item_id_)
        # print("put 70", itm)
        if itm is None:
            self.items[item_id_] = {
                "item": item,
                "count": 1
            }
            return
        itm["count"] += 1
        # print("put 78", self.items)
        return

    def save(self):
        self.session.execute(delete(InventoryDB).where(InventoryDB.player_id == self.player_id))
        for id, item in self.items.items():
            self.session.add(InventoryDB(player_id=self.player_id, item_id=id, count=item['count']))
        self.session.commit()

    def load(self):
        items = self.session.scalars(select(InventoryDB).where(InventoryDB.player_id == self.player_id)).fetchall()
        self.items = {}
        for item in items:
            self.items[item.item_id] = {
                'item': {
                    'name': item.item.name,
                    'item_id': item.item.item_id,
                    'power': item.item.heal_power
                },
                'count': item.count
            }

    def look_inv(self):
        s = 'В инвентаре пусто!'
        if self.items:
            s = 'Инвентарь игрока: \n'

        for id, item in self.items.items():
            # s += "- {} (ID:{}) кол-во: {}".format(item['item']['name'], id, item['count'])
            s += f"{item['item']['name']} - {item['count']}шт. \n"
            print(f'ID{id}')
        return s


class Protagonist:  # you may decide to add some parent class here, e.g. ORM Model
    def __init__(self, name, id, session):  # add more parameters if you need
        self.session = session
        self.id = id  # player id
        self.name = name
        self.hp = 10
        self.inventory = Inventory(player_id=id, session=self.session)
        if not self.load():
            print('## Новый игрок {}'.format(self.name))

    # загружает состояние персонажа
    def load(self):
        prt = self.session.get(ProtagonistDB, self.id)
        if not prt:
            return False

        self.name = prt.name
        self.hp = prt.hp
        print('## Загрузка игрока {} (жизни {})'.format(self.name, self.hp))

        self.inventory.load()
        return True

    def save(self):
        print('## Сохранение игрока {} (жизни {})'.format(self.name, self.hp))
        prt = self.session.get(ProtagonistDB, self.id)
        if prt:
            prt.hp = self.hp
        else:
            prt = ProtagonistDB(id=self.id, name=self.name, hp=self.hp)
        self.session.add(prt)
        self.session.commit()

        self.inventory.save()

    def talk_to(self, npc, phase=None):
        # print('>>> Разговор игрока {} c NPC {}'.format(self.name, npc.name))
        text = npc.say_smth(phase=phase)
        return '{} говорит: {}'.format(npc.name, text)
        # print('NPC {} говорит: {}'.format(npc.name, text))

    def restart(self):
        self.hp = 10
        self.inventory.clear()
        print(">>> Игрок {} воскрес и потерял весь инвентарь! <<<".format(self.name))

    # def attack_0(self, enemy):
    #     is_won = True
    #     take_dd = 0
    #
    #     print('>>>>> Бой игрока {} c {}'.format(self.name, enemy.name))
    #     while self.hp > 0:
    #         att = random.randint(1, 6)
    #         e_att = enemy.attack()
    #         print(
    #             "> Игрок {} бросок кубика {} | Противник {} бросок кубика {}".format(self.name, att, enemy.name, e_att))
    #         if att < e_att:
    #             self.hp -= enemy.damage
    #             take_dd += 1
    #         elif att == e_att:
    #             continue
    #         else:
    #             print("> Игрок {} победил {}!".format(self.name, enemy.name))
    #             drop = enemy.get_drop()
    #             self.inventory.put(drop)
    #             print('> Игрок {} получает {}'.format(self.name, drop['name']))
    #             break
    #
    #     if self.hp <= 0:
    #         print("> Игрок {} мертв".format(self.name))
    #         self.restart()
    #         is_won = False
    #
    #     print('<<<<< Бой окончен!')
    #     return [is_won, take_dd]

    def attack(self, enemy):
        is_won = 0

        # print('>>>>> Бой игрока {} c {}'.format(self.name, enemy.name))
        att = random.randint(1, 6)
        e_att = enemy.attack()
        print(f"> Игрок {self.name} бросок кубика {att} | Противник {enemy.name} бросок кубика {e_att}")
        if att < e_att:
            self.hp -= enemy.damage
            is_won = 1  # ранен
        elif att == e_att:
            is_won == 2  # все промахнулись
        else:
            drop = enemy.get_drop()
            self.inventory.put(drop)
            print(f'> Игрок {self.name} получает {drop["name"]}')

        if self.hp <= 0:
            print("> Игрок {} мертв".format(self.name))
            self.restart()
            is_won = 3  # мертв
        # print('<<<<< Бой окончен!')
        return is_won

    def flask(self, item):
        if self.inventory.get(item):
            # print("Ой, нашли")
            if item == 1:
                self.hp += 2
            if item == 2:
                self.hp += 3
            if self.hp > 10:
                self.hp = 10
            s = "Здоровье восполнилось!"

        else:
            s = "В инвентаре зелья не оказалось"
        return s

    def go(self, direction: Direction):
        pass  # вам нужно будет реализовать это в другом упражнении

    def whereami(self):
        pass  # возвращает описание текущего местоположения

    def take(self, item):
        self.inventory[item] += 1

    def give(self, npc, item):
        self.inventory[item] -= 1
        if self.inventory[item] == 0:
            del self.inventory[item]
        npc.receive(item)


def res_battle(pl, npc, is_won):
    if is_won != 3:
        pl.talk_to(npc, PHASES_DESC.winner)
    else:
        pl.talk_to(npc, PHASES_DESC.game_over)


if __name__ == "__main__":
    engine = create_engine("sqlite:///test.sqlite", echo=False)
    with Session(engine) as session:
        pl = Protagonist("July", 1, session)
        pl.inventory.look_inv()

        # npc  говорит
        npc = NPC(1, session)
        pl.talk_to(npc, PHASES_DESC.start_game)

        # бой
        en = Enemy(1, session)
        is_won = pl.attack(en)
        res_battle(pl, npc, is_won)

        # npc говорит
        pl.talk_to(npc, PHASES_DESC.in_game)

        en = Enemy(2, session)
        is_won = pl.attack(en)
        res_battle(pl, npc, is_won)

        pl.talk_to(npc, PHASES_DESC.in_game)

        en = Enemy(3, session)
        is_won = pl.attack(en)
        res_battle(pl, npc, is_won)

        pl.save()
