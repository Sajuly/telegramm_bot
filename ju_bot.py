import config
from models import PHASES_DESC, Items
from protogonist import Protagonist, NPC, Enemy, res_battle
import telebot
from telebot import types
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, delete

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(mess):
    u_name = f'<b>Приветствую Вас в "July\'s game-bot!"</b>'
    bot.send_message(mess.chat.id, u_name, parse_mode="html")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    a = types.KeyboardButton('/help')

    markup.add(a)
    bot.send_message(mess.chat.id, "/help тебе поможет!", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_(message):
    bot.send_message(message.chat.id,
                     "/game - меню игры\n"
                     "/start - выйти из меню игры\n"
                     "/help - помощь\n"
                     "Цель игры собрать 5 Драконьих хвостов\n"
                     "Из врага крыса выпадает малое зелье - восполняет 2 HP\n"
                     "Из врага Волк выпадает большое зелье - восполняет 3 HP"
                     )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    a = types.KeyboardButton('/game')
    b = types.KeyboardButton('/start')

    markup.add(a, b)
    bot.send_message(message.chat.id, 'Для удобства используй кнопки', reply_markup=markup)


@bot.message_handler(commands=['game'])
def game(message):
    markup = types.InlineKeyboardMarkup(row_width=1)  # кнопки встроенные в сообщение

    start_gm = types.InlineKeyboardButton("Новая игра", callback_data="new game")
    load = types.InlineKeyboardButton("Продолжить", callback_data="load")
    exit_gm = types.InlineKeyboardButton("Выход", callback_data="exit_gm")

    markup.add(start_gm, load, exit_gm)

    bot.send_message(message.chat.id, '<b><i>KILL FIVE DRAGONS!</i></b>', reply_markup=markup, parse_mode="html")


def move_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=1)

    battle = types.InlineKeyboardButton("Вступить в бой", callback_data="battle")
    inventory = types.InlineKeyboardButton("Посмотреть инвентарь", callback_data="inventory")
    save_exit = types.InlineKeyboardButton("Выход в главное меню", callback_data="exit_to_menu")
    drink = types.InlineKeyboardButton("Выпить лечебное зелье", callback_data="drink")

    markup.add(battle, inventory, drink, save_exit)
    bot.send_message(call.message.chat.id, "<b><i>ваши действия:</i></b>", reply_markup=markup, parse_mode="html")


def enemy_meny(call):
    markup = types.InlineKeyboardMarkup(row_width=1)

    enemy_rat = types.InlineKeyboardButton("Крыса", callback_data="rat")
    enemy_wolf = types.InlineKeyboardButton("Волк", callback_data="wolf")
    enemy_dragon = types.InlineKeyboardButton("Дракон", callback_data="dragon")

    markup.add(enemy_rat, enemy_wolf, enemy_dragon)
    bot.send_message(call.message.chat.id, "<b><i>выберите врага:</i></b>", reply_markup=markup, parse_mode="html")


def flack_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=1)

    big = types.InlineKeyboardButton("Большое исцеление", callback_data="big")
    small = types.InlineKeyboardButton("Малое исцеление", callback_data="small")

    markup.add(small, big)
    bot.send_message(call.message.chat.id, "<b><i>выберите зелье:</i></b>", reply_markup=markup, parse_mode="html")


def player_hp(call, u_name, hp):
    bot.send_message(call.message.chat.id, f'<i>игрок</i> <b>{u_name.upper()}</b> ({hp} HP)', parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    u_name = call.from_user.first_name
    u_id = call.from_user.id

    engine = create_engine("sqlite:///test.sqlite", echo=False)
    with Session(engine) as session:
        pl = Protagonist(u_name, u_id, session)
        st = pl.inventory.look_inv()

        npc = NPC(1, session)

        if call.data == "new game" or call.data == "load":
            if call.data == "new game":
                pl.restart()
            # npc говорит
            # npc_talk = pl.talk_to(npc, PHASES_DESC.start_game)
            # bot.send_message(call.message.chat.id, npc_talk)

            player_hp(call, u_name, pl.hp)
            move_menu(call)

        if call.data == "battle":
            enemy_meny(call)

        # Выбор противника и бой с ним
        if call.data in ["rat", "wolf", "dragon"]:
            if call.data == "rat":
                en_name = 1
            if call.data == "wolf":
                en_name = 2
            if call.data == "dragon":
                en_name = 3

            en = Enemy(en_name, session)
            is_won = pl.attack(en)
            bot.send_message(call.message.chat.id, f"Ваш противник - <b>{en.name}</b>. Берегитесь!", parse_mode="html")

            # -------------- игрок победил---------------------
            if is_won == 0:
                drop = en.get_drop()
                bot.send_message(call.message.chat.id,
                                 "Вы наносите мощный удар. Враг повержен!\n"
                                 f"<i>Вы получаете:</i> <b><i>{drop['name']}</i></b>", parse_mode="html")
                player_hp(call, u_name, pl.hp)
                move_menu(call)
            # --------------- игрок получил урон---------------------
            elif is_won == 1:
                bot.send_message(call.message.chat.id, f"<b>{en.name}</b> уворачивается и кусает вас! \U0001F494",
                                 parse_mode="html")

                player_hp(call, u_name, pl.hp)
                move_menu(call)
            # ------------------никто не получил урон----------------------
            elif is_won == 2:
                bot.send_message(call.message.chat.id, "Враг парировал атаку")
                player_hp(call, u_name, pl.hp)
                move_menu(call)
            # -------------- игрок мертв ---------------------
            else:
                emoji = "\U0001F62D"
                bot.send_message(call.message.chat.id, f"{en.name} побеждает!\n <b>Вы мертвы!</b>{emoji}",
                                 parse_mode="html")
                pl.restart()
                game(call.message)

                # ----------- npc talk--------------------------
                # res_battle(pl, npc, is_won)
                # if is_won == 0:
                #     npc_talk = pl.talk_to(npc, PHASES_DESC.in_game)
                #     bot.send_message(call.message.chat.id, npc_talk)
                #     player_hp(call, u_name, pl.hp)
                # move_menu(call)

            # print("*****", pl.inventory.items[3]['count'])
            # print(pl.inventory.items)
            if 3 in pl.inventory.items:
                if pl.inventory.items[3]['count'] == 5:
                    bot.send_message(call.message.chat.id, f'<b>ПОЗДРАВЛЯЮ ВЫ ПОБЕДИЛИ ВСЕХ ДРАКОНОВ!</b>',
                                     parse_mode="html")
                    print(f"{u_name}, победил!")
                    game(call.message)
                    pl.restart()

        # Сохранение сессии
        pl.save()

        if call.data == "inventory":
            bot.send_message(call.message.chat.id, f"<i>{st}</i>", parse_mode="html")
            move_menu(call)
            print(st)

        if call.data == "drink":
            flack_menu(call)

        if call.data in ["big", "small"]:
            if call.data == "small":
                ask = pl.flask(1)
                bot.send_message(call.message.chat.id, f'<i>{ask}</i>', parse_mode="html")
                player_hp(call, u_name, pl.hp)
                move_menu(call)
            if call.data == "big":
                ask = pl.flask(2)
                bot.send_message(call.message.chat.id, f'<i>{ask}</i>', parse_mode="html")
                player_hp(call, u_name, pl.hp)
                move_menu(call)

            pl.save()

        if call.data == "exit_to_menu":
            game(call.message)

        if call.data == "exit_gm":
            start(call.message)


bot.polling(none_stop=True)
