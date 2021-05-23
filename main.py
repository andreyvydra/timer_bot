import datetime
import threading

import telebot

TOKEN = 'token:token'

bot = telebot.AsyncTeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который устанавливает таймер.',
                     reply_markup=get_keyboard())


@bot.callback_query_handler(func=lambda x: x.data == 'set timer')
def pre_set_timer(query):
    message = query.message
    bot.send_message(message.chat.id,
                     'Введите время для установки таймера.\n'
                     'Пример ввода: \n'
                     '1. 30 сек\n'
                     '2. 2 мин\n'
                     '3. 10 час')
    bot.register_next_step_handler(message, set_time)


def set_time(message):
    times = {
        'сек': 0,
        'мин': 0,
        'час': 0
    }

    quantity, type_time = message.text.split()

    if type_time not in times.keys():
        bot.send_message(message.chat.id,
                         'Вы ввели неправильный тип времени.')
        return

    if not quantity.isdigit():
        bot.send_message(message.chat.id,
                         'Вы ввели не число')

    times[type_time] = int(quantity)

    pre_set_text(message, times)


def pre_set_text(message, times):
    bot.send_message(message.chat.id,
                     'Введите текст, который придёт после'
                     ' истечения таймера.')
    bot.register_next_step_handler(message, set_text, times)


def set_text(message, times):
    cur_date = datetime.datetime.now()

    timedelta = datetime.timedelta(days=0, seconds=times['сек'],
                                   minutes=times['мин'], hours=times['час'])

    cur_date += timedelta

    users[message.chat.id] = (cur_date, message.text)
    bot.send_message(message.chat.id,
                     'Спасибо! Через заданное время вам'
                     ' придёт уведомление.')


def check_date():
    now_date = datetime.datetime.now()
    users_to_delete = []
    for chat_id, value in users.items():
        user_date = value[0]
        msg = value[1]
        if now_date >= user_date:
            bot.send_message(chat_id, msg)
            users_to_delete.append(chat_id)
    for user in users_to_delete:
        del users[user]
    threading.Timer(1, check_date).start()


def get_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Установить таймер', callback_data='set timer')
    keyboard.add(button)
    return keyboard


if __name__ == '__main__':
    users = {}
    while True:
        try:
            check_date()
            bot.polling()
        except:
            print('Что-то сломалось. Перезагрузка')
