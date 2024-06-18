import unittest
import sqlite3
import uuid
from pprint import pprint
from fastapi import FastAPI, APIRouter, HTTPException

db = sqlite3.connect("file::memory:?cache=shared", check_same_thread=False)
cur = db.cursor()


def createDB():
    cur.execute("CREATE TABLE users(id, name, address, email, phone)")


createDB()

app = FastAPI()
router = APIRouter(prefix="/api")


@router.post("/add/user")
def add_user(name, address=None, email=None, phone=None) -> dict:
    id = insertUser(name, address, email, phone)
    return getUser(id)


@router.get("/get/all")
def get_all_users(limit=10) -> list[dict]:
    return getAllUsers(limit)


@router.get("/get/user")
def get_user(id) -> dict:
    return getUser(id)


@router.patch("/update/user")
def update_user(id, name=None, address=None, email=None, phone=None):
    user = getUser(id)
    if user:
        return updateUser(
            id,
            user[id]["user_name"] if name is None else name,
            user[id]["user_address"] if address is None else address,
            user[id]["user_email"] if email is None else email,
            user[id]["user_phone"] if phone is None else phone,
        )
    else:
        raise HTTPException(status_code=404, detail="No such user.")


@router.delete("/delete/user")
def delete_user(id) -> str:
    return deleteUser(id)


def insertUser(name, address, email, phone) -> str:
    user_id = uuid.uuid4().hex
    params = (user_id, name, address, email, phone)
    cur.execute(
        "INSERT INTO users(id, name, address, email, phone) VALUES(?, ?, ?, ?, ?)",
        params,
    )
    return user_id


def getAllUsers(limit=10) -> list[dict]:
    res = cur.execute("SELECT * FROM users LIMIT ?", (limit,))
    users = res.fetchall()
    if users is not None:
        all_users = []
        for user in users:
            all_users.append(
                {
                    "user_id": user[0],
                    "user_name": user[1],
                    "user_address": user[2],
                    "user_email": user[3],
                    "user_phone": user[4],
                }
            )
        return all_users
    else:
        return []


def getUser(id) -> dict:
    res = cur.execute("SELECT * from users WHERE id = ?", (id,))
    user = res.fetchone()
    if user is not None:
        return_user = {
            user[0]: {
                "user_id": user[0],
                "user_name": user[1],
                "user_address": user[2],
                "user_email": user[3],
                "user_phone": user[4],
            }
        }
        return return_user
    else:
        return None


def updateUser(id, user_name, user_add, user_email, user_phone) -> dict:

    res = cur.execute(
        "UPDATE users SET name = ?, email = ?, address = ?, phone = ? WHERE id = ?",
        (user_name, user_email, user_add, user_phone, id),
    )
    db.commit()

    return getUser(id)


def deleteUser(id) -> str:
    res = cur.execute("DELETE FROM users WHERE id = ?", (id,))
    db.commit()
    return f"User {id} deleted"


class MyTests(unittest.TestCase):
    def test_getUser(self):
        # Starting values for user
        user_name = "Tim"
        user_add = "123 Main St"
        user_email = "email@test.clom"
        user_phone = "12345678"

        # Create the DB
        createDB()
        user_id = insertUser(user_name, user_add, user_email, user_phone)
        user = getUser(user_id)

        # Set check values to assert
        chk_user_name = user[user_id]["user_name"]
        chk_user_add = user[user_id]["user_address"]
        chk_user_phone = user[user_id]["user_phone"]
        chk_user_email = user[user_id]["user_email"]

        # Define assertions
        assert user_name == chk_user_name, "test failed, username wrong"
        assert user_email == chk_user_email, "test failed, email wrong"
        assert user_add == chk_user_add, "test failed, address wrong"
        assert (
            user_phone == chk_user_phone
        ), "test failed, phone wrong, but this time you are also GAY"

        # Set new values for user
        new_name = "Tim"
        new_add = "moms house"
        new_email = "email@test.clom"
        new_phone = None

        # Update the user with new stuff
        updated_user = updateUser(user_id, new_name, new_add, new_email, new_phone)

        # Set NEW check values to assert
        chk_new_name = updated_user[user_id]["user_name"]
        chk_new_add = updated_user[user_id]["user_address"]
        chk_new_phone = updated_user[user_id]["user_phone"]
        chk_new_email = updated_user[user_id]["user_email"]

        # Define assertions for NEW USER
        assert new_name == chk_new_name, "test failed, username wrong"
        assert new_email == chk_new_email, "test failed, email wrong"
        assert new_add == chk_new_add, "test failed, address wrong"
        assert (
            new_phone == chk_new_phone
        ), "test failed, phone wrong, but this time you are also GAY"

        deleteUser(user_id)
        result = getUser(user_id)

        assert (
            result == None
        ), "you fucking suckm, pussy, your code doesn't get or delete or something, it/s all fucked honetsly -/ thend"

        insertUser("Sam", "home!", None, None)
        insertUser("Harrison", None, "email2test.com", None)

        users = getAllUsers()

        assert len(users) == 2, "bad length"


app.include_router(router=router)
