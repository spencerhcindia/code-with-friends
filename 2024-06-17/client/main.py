"""
The client for this experiment!
"""

# pylint: skip-file
import requests
import random
import string

ADDRESS = "192.168.68.53"
base = f"http://{ADDRESS}:8000/api"

CREATE_USER = f"{base}/add/user"
DELETE_USER = f"{base}/delete/user"
GET_ALL_USERS = f"{base}/get/all"
GET_USER = f"{base}/get"
UPDATE_USER = f"{base}/update/user"


def randstring(n: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def main() -> None:
    """
    Run the tests!
    """
    user_name = "Donald"
    user_address = "111 Waltham SW"
    user_phone = "3306169901"
    user_email = "donnie@sbcglobal.net"

    # Step 1: Create Donnie.
    res = requests.post(
        CREATE_USER,
        params={
            "name": user_name,
            "address": user_address,
            "phone": user_phone,
            "email": user_email,
        },
    )

    # Step 2: Create a user; get its information
    created_user_data = next(iter(res.json().values()))
    assert user_name == created_user_data["user_name"]
    assert user_address == created_user_data["user_address"]
    assert user_phone == created_user_data["user_phone"]
    assert user_email == created_user_data["user_email"]

    length = 6

    counter = 0
    # Step 3: Create and randomly update 1,000 users
    while True:
        create_result = requests.post(
            CREATE_USER,
            params={
                "name": randstring(length),
                "address": randstring(length),
                "phone": randstring(length),
                "email": randstring(length),
            },
        )
        user_data = next(iter(create_result.json().values()))
        updated_field = random.choice(
            [
                "name",
                "address",
                "phone",
                "email",
            ]
        )

        requests.patch(
            UPDATE_USER,
            params={
                "id": user_data["user_id"],
                updated_field: randstring(length),
            },
        )

        counter += 1
        if counter % 100 == 0:
            print(f"Wrote {counter} records.")
        if counter % 1000 == 0:
            break

    # Step 4: Delete ( up to ) 2000 users.
    counter = 0
    for user in requests.get(GET_ALL_USERS, params={"limit": 2000}).json():
        user_id = user["user_id"]
        requests.delete(DELETE_USER, params={"id": user_id})
        counter += 1
        if counter % 25 == 0:
            print(f"Deleted user with id {user_id}!")


if __name__ == "__main__":
    main()
