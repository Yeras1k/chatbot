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
    host = HOST,
    port = "6293",
    user = USER,
    password = PASS,
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
    result = db_object.fetchone()
    if not result:
        mycursor.execute(f"INSERT INTO users(teleid, name, isActive, isWant) VALUES (%i, %s, %s, %s)", (user_id, user_name, "False", "False")
        mydb.commit()
