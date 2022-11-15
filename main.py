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
