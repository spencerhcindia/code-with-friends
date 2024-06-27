import unittest
import sqlite3
import uuid
from pprint import pprint

db = sqlite3.connect("file::memory:?cache=shared")
cur = db.cursor()

def createDB():
    cur.execute("CREATE TABLE users(id, name, address, email, phone)")

def insertUser(name, address, email, phone):
    user_id = uuid.uuid4().hex
    params = (user_id, name, address, email, phone)
    cur.execute("INSERT INTO users(id, name, address, email, phone) VALUES(?, ?, ?, ?, ?)", params)
    return user_id

def getUser(id):
    res = cur.execute("SELECT * from users WHERE id = ?", (id,))
    user = res.fetchone()
    return_user = {user[0]:{
        "user_id": user[0],
        "user_name": user[1],
        "user_address": user[2],
        "user_email": user[3],
        "user_phone": user[4]
    }
        }
    pprint(return_user)

createDB()
id = insertUser("Dave", "123 Main", "email@d.com", "1234567")
getUser(id)
