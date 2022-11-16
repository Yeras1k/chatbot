import os
import telebot
import logging
import random
from database import Database
from telebot import types
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

@bot.message_handler(commands=["start"])
def start(message):
    user_name = message.from_user.username
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Поиск собеседника')
    bot.send_message(message.chat.id, f"Привет, {user_name}! Это анонимный чат бот. Нажмите кнопку ниже, чтоб начать поиск собеседника", reply_markup = service)

@bot.message_handler(commands=["menu"])
def menu(message):
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Поиск собеседника')
    bot.send_message(message.chat.id, 'Меню'.format(message.from_user), reply_markup = service)

@bot.message_handler(content_types=["text"])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Поиск собеседника':
            service = telebot.types.ReplyKeyboardMarkup(True, True)
            service.row('Остановить поиск')

            add_queue(message.chat.id)
            bot.send_message(message.chat.id, 'Идет поиск', reply_markup = service)

@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
