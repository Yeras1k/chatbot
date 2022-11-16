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

@bot.message_handler(commands=["start"])
def start(message):
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Начать', 'Отмена')
    user_id = message.from_user.id
    user_name = message.from_user.username
    mycursor.execute(f"SELECT teleid FROM users WHERE teleid = {user_id}")
    result = mycursor.fetchone()
    if not result:
        mycursor.execute(f"INSERT INTO users(teleid, username, isActive, isWant, chat, temp) VALUES ({user_id}, '{user_name}', False, False, 0, 0)")
        mydb.commit()
        bot.send_message(message.from_user.id, 'Плохо')
    else:
        mycursor.execute(f"UPDATE users SET isWant = False, chat = 0, temp = 0 WHERE teleid = {user_id}")
        mydb.commit()
        bot.send_message(message.from_user.id, 'Хорошо')
    send = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Нажмите Начать, чтоб начать общение", reply_markup=service)
    bot.register_next_step_handler(send, chatting)


def chatting(message):
    if message.text == "Начать":
        user_id = message.from_user.id
        bot.send_message(message.from_user.id, 'Ищем...')
        mycursor.execute(f"UPDATE users SET isWant = True WHERE teleid = {user_id}")
        mydb.commit()
        mycursor.execute(f"SELECT teleid FROM users WHERE teleid NOT IN ({user_id}) AND isActive = 0 AND isWant = 1 AND chat = 0")
        people = mycursor.fetchall()
        bot.send_message(message.from_user.id, f'{str(people)}')
        if not people:
            service = telebot.types.ReplyKeyboardMarkup(True, True)
            service.row('Начать')
            send = bot.send_message(message.chat.id, f"Собеседник не найден! Попробуйте снова", reply_markup=service)
            bot.register_next_step_handler(send, chatting)
        else:
            service = telebot.types.ReplyKeyboardMarkup(True, True)
            service.row('Закончить')
            global person
            person = random.choice(people[0])
            mycursor.execute(f"UPDATE users SET temp = {person} WHERE teleid = {user_id}")
            mydb.commit()
            mycursor.execute(f"SELECT temp FROM users WHERE teleid = {person}")
            second = mycursor.fetchone()
            if second != user_id:
                mycursor.execute(f"UPDATE users SET temp = {user_id} WHERE teleid = {person}")
                mycursor.execute(f"UPDATE users SET chat = {person} WHERE teleid = {user_id}")
                mycursor.execute(f"UPDATE users SET chat = {user_id} WHERE teleid = {person}")
                mydb.commit()
                send = bot.send_message(message.from_user.id, 'Можете писать')
                bot.register_next_step_handler(send, chat)
            else:
                mycursor.execute(f"UPDATE users SET chat = {person} WHERE teleid = {user_id}")
                mycursor.execute(f"UPDATE users SET chat = {user_id} WHERE teleid = {person}")
                mydb.commit()
                send = bot.send_message(message.from_user.id, 'Можете писать', reply_markup=service)
                bot.register_next_step_handler(send, chat)


def chat(message):
    if message.text == "Закончить":
        msg = bot.send_message(person, "Собеседник решил закончить разговор! Нажмите Закончить")
        bot.register_next_step_handler(msg, start)
    else:
        service = telebot.types.ReplyKeyboardMarkup(True, True)
        service.row('Закончить')
        msg = bot.send_message(person, message.text, reply_markup=service)
        bot.register_next_step_handler(msg, chat)


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
