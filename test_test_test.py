import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.TOKEN)


# декоратор отслеживания команды
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Hello, <b>{message.from_user.first_name}</b>'
    # mess = f'Hello, <b>{message.from_user.first_name} {message.from_user.last_name}</b>'
    # 1 bot.send_message(message.chat.id, '<b>Hello, July!</b>', parse_mode="html")
    bot.send_message(message.chat.id, mess, parse_mode="html")


# отслеживать весь текст конфликтует с website
# @bot.message_handler(content_types=['text'])
# def get_user_text(message):
#     if message.text == "Hello!":
#         bot.send_message(message.chat.id, "И тебе привет!", parse_mode="html")
#     elif message.text == "id":
#         bot.send_message(message.chat.id, f"Твой ID:{message.from_user.id}", parse_mode="html")
#     elif message.text == "photo":
#         photo = open('icon.jpg', 'rb')
#         bot.send_photo(message.chat.id, photo)
#     else:
#         bot.send_message(message.chat.id, "Непонятно", parse_mode="html")


# отслеживание фото документов и прочее
@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    bot.send_message(message.chat.id, "Good photo!")


@bot.message_handler(commands=['website'])
def website(message):
    markup = types.InlineKeyboardMarkup()  # кнопки встроенные в сообщение

    markup.add(types.InlineKeyboardButton("Go to website", url="https://jut.su/anime/"))
    bot.send_message(message.chat.id, "Интересный сайт", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # внешние кнопки

    a = types.KeyboardButton('a')
    b = types.KeyboardButton('b')

    markup.add(a, b)
    bot.send_message(message.chat.id, "ого", reply_markup=markup)


bot.polling(none_stop=True)


--------------------------------------
 Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Если нажали на одну из  кнопок — просим ввести переменные
    if call.data == "figure":
       a = kr(call.message) # если kr() возвращает площадь круга
       bot.send_message(call.message.from_user.id, "Найдем площадь круга:{}".format(a))
       # bot.send_message(call.message.from_user.id, "Найдем площадь круга:{}".format(kr(call.message)))
