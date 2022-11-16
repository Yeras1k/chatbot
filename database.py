import mysql.connector
import os

mydb = mysql.connector.connect(
    host = os.environ.get('MYSQLHOST'),
    port = os.environ.get('MYSQLPORT'),
    user = os.environ.get('MYSQLUSER'),
    password = os.environ.get('MYSQLPASSWORD'),
    database = os.environ.get('MYSQLDATABASE')
)
mycursor = mydb.cursor()

class Database:
    def add_queue(self, chat_id):
        mycursor.execute(f"INSERT INTO users(teleid) VALUES (%i)", (chat_id))
        mydb.commit()
