import os
import telebot
import logging
import random
import mysql.connector
from telebot import types
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

mydb = mysql.connector.connect(
    host = os.environ.get('MYSQLHOST'),
    port = os.environ.get('MYSQLPORT'),
    user = os.environ.get('MYSQLUSER'),
    password = os.environ.get('MYSQLPASSWORD'),
    database = os.environ.get('MYSQLDATABASE')
)
mycursor = mydb.cursor()

def add_queue(chat_id):
    mycursor.execute(f"INSERT INTO queue(teleid) VALUES({chat_id})")
    mydb.commit()
def delete_queue(chat_id):
    mycursor.execute(f"DELETE FROM queue WHERE teleid = {chat_id}")
    mydb.commit()
def get_chat():
    result = mycursor.execute(f"SELECT * FROM queue").fetchmany(1)
    if(bool(len(result))):
        for row in result:
            return(row[1])
    else:
        return False
def create_chat(chat_one, chat_two):
    if chat_two != 0:
        mycursor.execute(f"DELETE FROM queue WHERE teleid = {chat_two}")
        mycursor.execute(f"INSERT INTO chats(chat_one, chat_two) VALUES({chat_one}, {chat_two})")
        return True
    else:
        return False

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

            chat_two = get_chat()

            if(create_chat(message.chat.id, chat_two) == False):
                add_queue(message.chat.id)
                bot.send_message(message.chat.id, 'Идет поиск', reply_markup = service)
            else:
                service = telebot.types.ReplyKeyboardMarkup(True, True)
                service.row('/stop')
                mess = 'Собеседник найден! Нажмите /stop чтоб закончить диалог'
                bot.send_message(message.chat.id, mess, reply_markup = service)
                bot.send_message(chat_two, mess, reply_markup = service)

        if message.text == 'Остановить поиск':
            delete_queue(message.chat.id)
            bot.send_message(message.chat.id, 'Поиск остановлен! Нажмите /menu')


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
