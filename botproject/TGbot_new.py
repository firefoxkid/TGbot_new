# import json
# import logging
# import os
# import time
# from logging.handlers import RotatingFileHandler

# import requests
# import telegram
# from dotenv import load_dotenv


import datetime
import math
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)
STATE = None
BIRTH_YEAR = 1
BIRTH_MONTH = 2
BIRTH_DAY = 3

# function to handle the /start command
# def start(update, context):
#     first_name = update.message.chat.first_name
#     last_name = update.message.chat.first_name
#     update.message.reply_text(f"Привет, {first_name} {last_name}, рад познакомиться, я Бот-Валера!")
#     start_getting_birthday_info(update, context)

def start(update, context):
    # keyboard = [
    #     [
    #         InlineKeyboardButton("Старт", callback_data='/start'),
    #         InlineKeyboardButton("Помощь", callback_data='/help'),
    #     ],
    #     [InlineKeyboardButton("Сколько дней я живу", callback_data='/life_long')],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)
    first_name = update.message.chat.first_name
    last_name = update.message.chat.first_name
    update.message.reply_text(f"Привет, {first_name} {last_name}, рад познакомиться, я Бот-Валера!")
    start_getting_birthday_info(update, context)

def make_keyborad(update, _):
    keyboard = [
        [
            InlineKeyboardButton("Сколько дней я живу", callback_data='/life_long'),
            InlineKeyboardButton("Помощь", callback_data='/help'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)


def button(update, _):
    query = update.callback_query
    variant = query.data

    # `CallbackQueries` требует ответа, даже если 
    # уведомление для пользователя не требуется, в противном
    #  случае у некоторых клиентов могут возникнуть проблемы. 
    # смотри https://core.telegram.org/bots/api#callbackquery.
    query.answer()
    # редактируем сообщение, тем самым кнопки 
    # в чате заменятся на этот ответ.
    query.edit_message_text(text=f"Выбранный вариант: {variant}")

def start_getting_birthday_info(update, context):
    global STATE
    STATE = BIRTH_YEAR
    update.message.reply_text(
        f"Мне нужно понять дату твоего рождения, поэтому напиши в каком году ты родился:")

def received_birth_year(update, context):
    global STATE
    try:
        today = datetime.date.today()
        year = int(update.message.text)
        if year > today.year:
            raise ValueError("invalid value")
        context.user_data['birth_year'] = year
        update.message.reply_text(
            f"Супергут! Теперь мне нужно знать месяц (в виде числа от 1 до 12)...")
        STATE = BIRTH_MONTH
    except:
        update.message.reply_text(
            "забавно конечно, но кажется ты гонишь или ввел некорректные данные...")

def received_birth_month(update, context):
    global STATE
    try:
        today = datetime.date.today()
        month = int(update.message.text)
        if month > 12 or month < 1:
            raise ValueError("invalid value")
        context.user_data['birth_month'] = month
        update.message.reply_text(f"Отлично, а теперь число в котором родился...")
        STATE = BIRTH_DAY
    except:
        update.message.reply_text(
            "Прикольно, но возможно некорректно...")

def received_birth_day(update, context):
    global STATE
    try:
        today = datetime.date.today()
        dd = int(update.message.text)
        if dd > 31 or dd < 1:
            raise ValueError("invalid value")
        yyyy = context.user_data['birth_year']
        mm = context.user_data['birth_month']
        birthday = datetime.date(year=yyyy, month=mm, day=dd)
        if today - birthday < datetime.timedelta(days=0):
            raise ValueError("invalid value")
        context.user_data['birthday'] = birthday
        STATE = None
        update.message.reply_text(f'ОК, вы родились: {birthday}')
        make_keyborad(update, context)
    except:
        update.message.reply_text(
            "Прикольно, но возможно некорректно...")

# function to handle the /help command
def help(update, context):
    update.message.reply_text('Пока я умею выполнять только команду /life_long')
    update.message.reply_text('Введи эту команду или соответсвующую кнопку')

# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('чет не работает... ')
    update.message.reply_text(context)

# function to handle normal text
def text(update, context):
    global STATE
    if STATE == BIRTH_YEAR:
        return received_birth_year(update, context)
    if STATE == BIRTH_MONTH:
        return received_birth_month(update, context)
    if STATE == BIRTH_DAY:
        return received_birth_day(update, context)

# This function is called when the /life_long command is issued
def life_long(update, context):
    print("ok")
    user_life = calculate_life(
        context.user_data['birthday'])
    # update.message.reply_text(f"Лет: {user_life['years']}")
    # update.message.reply_text(f"Месяцев: {user_life['months']}")
    update.message.reply_text(f"Прикинь, твоя жизнь длится {user_life['days']} дней!")

def calculate_life(birthdate):
    today = datetime.date.today()
    delta = today - birthdate
    long_life = {}
    # long_life['years'] = 11
    # long_life['months'] = 12
    long_life['days'] = delta.days
    return long_life


def main():
    """alex_long_life_bot"""
    TOKEN = '5762211771:AAFTXEqBHWcND43kTxPRrXF6R6a8Xz0JEB8'
    # TOKEN = os.getenv('TELEGRAM_TOKEN_LIFEBOT')
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # add an handler for our biorhythm command
    dispatcher.add_handler(CommandHandler("life_long", life_long))
    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # add an handler for errors
    dispatcher.add_error_handler(error)
    # start your shiny new bot
    updater.start_polling()
    # run the bot until Ctrl-C
    updater.idle()
if __name__ == '__main__':
    main()