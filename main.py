import os
import telebot
import logging
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
    user_id = message.from_user.id
    user_name = message.from_user.username
    bot.reply_to(message, f"Hello, {message.from_user.first_name}!")
    bot.send_message(message.chat.id, 'Нажмите "Начать", чтоб начать общение')
    mycursor.execute(f"SELECT teleid FROM users WHERE teleid = {user_id}")
    result = mycursor.fetchone()
    if not result:
        mycursor.execute(f"INSERT INTO users(teleid, username, isActive, isWant) VALUES ({user_id}, {user_name}, False, False)")
        mydb.commit()

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
