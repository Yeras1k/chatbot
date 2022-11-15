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
    host = "containers-us-west-103.railway.app",
    port = "6293",
    user = "root",
    password = "IOeQHj8jE6io4OQYTh3T",
    database = "railway"
)
mycursor = mydb.cursor()

@bot.message_handler(commands=["start"])
def start(message):
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Начать')
    user_id = message.from_user.id
    user_name = message.from_user.username
    mycursor.execute(f"SELECT teleid FROM users WHERE teleid = {user_id}")
    result = mycursor.fetchone()
    if not result:
        mycursor.execute(f"INSERT INTO users(teleid, username, isActive, isWant) VALUES ({user_id}, '{user_name}', False, False)")
        mydb.commit()
    else:
        pass
    send = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Нажмите Начать, чтоб начать общение", reply_markup=service)
    bot.register_next_step_handler(send, chatting)

def chatting(message):
    if message.text == "Начать":
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Ищем...', reply_markup=a)
        mycursor.execute(f"SELECT teleid FROM users")
        people = mycursor.fetchall
        person = random.choice(people)


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
