async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с тремя встроенными кнопками."""
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет, я July-bot!")
    keyboard = [
        [
            InlineKeyboardButton("Box 1", callback_data="пусто"),
            InlineKeyboardButton("Box 2", callback_data="пусто"),
        ],
        [InlineKeyboardButton("Box 3", callback_data="ПРИЗ!!!")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбирите кнопку:", reply_markup=reply_markup)

------------------------------------
Привет, я July-bot!
Выбирите кнопку:

[Box 1][Box 2]
[    Box 3   ]
--------------------------------------
        С ОБРАЩЕНИЕ К ПОЛЬЗОВАТЕЛЮ
async def start(update: Update, context: tele.ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с тремя встроенными кнопками."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, начнем игру?()",
        reply_markup=ForceReply(selective=True),
    )


-------------------------------------------------
        ПОВТОРЮШКА
async def echo(update: Update, context: tele.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=update.message.text)

if __name__ == '__main__':
    echo_handler = tele.MessageHandler(tele.filters.TEXT & ~tele.filters.COMMAND, echo)
    application.add_handler(echo_handler)
---------------------------------------------------------------------
        КАПСОМ
async def caps(update: Update, context: tele.ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text_caps)

if __name__ == '__main__':
    caps_handler = tele.CommandHandler('caps', caps)  # /caps hi == HI
    application.add_handler(caps_handler)

-------------------------------------------------------------------------
    От Дударя
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
def website(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # внешние кнопки

    a = types.KeyboardButton('a')
    b = types.KeyboardButton('b')

    markup.add(a, b)
    bot.send_message(message.chat.id, "ого", reply_markup=markup)

# запуск бота
bot.polling(none_stop=True)

