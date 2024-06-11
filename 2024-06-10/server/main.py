"""
Coding challenge -- playing with APIs.
I built this half, and Spencer wrote functions to communicate
to the various endpoints on this API.
- SAM 2024-06-10
"""

import json
import os
import inspect
import uuid

from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter(prefix="/api")

USERS = "users.txt"


def read_users() -> dict:
    """
    Reads users from the 'database', a file on the local machine.
    It's really just a JSON object blob keyed by user IDs and valued
    by blobs with user data ( e.g. name, email, etc ).
    If the file doesn't exist, returns an empty dictionary.
    If we fail to load the JSON, we return an empty dictionary.
    If we successfully load the blob from the file, we return it.
    """
    if not os.path.isfile(USERS):
        return {}
    with open(USERS, "r") as file_handle:
        try:
            users = json.load(file_handle)
        except Exception as exc:
            print(f"FAILED TO LOAD USERS: {exc}")
            users = {}
    return users


@router.post("/users/add")
def add_user(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    address: str | None = None,
) -> int:
    """
    Attempts to add a user to the 'database' given the provided input
    arguments. Returns 200 if the addition was successful.
    """
    users = read_users()
    with open(USERS, "w") as file_handle:
        user_id = str(uuid.uuid4())
        users[user_id] = {
            "id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
        }
        json.dump(users, file_handle, indent=4)
    return 200


@router.delete("/user/delete")
def delete_user(user_id: str) -> int:
    """
    Attempts to delete a user with the given ID from the 'database'.
    Returns 404 if no such user is found.
    Returns 200 if the deletion was successful.
    """
    users = read_users()
    user = users.get(user_id)
    if not user:
        return 404
    del users[user_id]

    with open(USERS, "w") as file_handle:
        json.dump(users, file_handle, indent=4)
    return 200


@router.post("/user/update")
def update_user(
    user_id: str,
    user_name: str | None = None,
    user_address: str | None = None,
    user_email: str | None = None,
    user_phone: str | None = None,
) -> dict:
    """
    Given input arguments, attempts to update a user with the given input
    ID. This will overwrite data: fields left null are assumed to be desired
    to be null on the target user.
    If no user with the provided ID is found, returns a dictionary with a
    description of the error.
    """
    users = read_users()
    user = users.get(user_id)
    if not user:
        return {"error": "No such user"}

    users[user_id] = {
        "id": user_id,
        "name": user_name,
        "address": user_address,
        "email": user_email,
        "phone": user_phone,
    }

    with open(USERS, "w") as file_handle:
        json.dump(users, file_handle, indent=4)
    return user


@router.get("/user/get")
def get_user(
    user_name: str | None = None,
    user_id: str | None = None,
    user_address: str | None = None,
    user_email: str | None = None,
    user_phone: str | None = None,
) -> dict:
    """
    Given input arguments, attempt to retrieve a user that matches
    all non-null arguments. If no such user is found, returns a
    dictionary with a description of the error.
    """
    args_map = {
        "name": user_name,
        "id": user_id,
        "address": user_address,
        "email": user_email,
        "phone": user_phone,
    }

    if not any(args_map.values()):
        return {
            "error": f"You must provide at least one of {', '.join(args_map.keys())}"
        }
    data = read_users().values()
    # Filter the arguments to the function to only include the ones that aren't null.
    non_null_args = {
        arg_name: arg for arg_name, arg in args_map.items() if arg is not None
    }
    # For every user,
    for entry in data:
        # if every input argument matches the corresponding value on the user,
        if all(
            [
                entry[arg_name] == arg_value
                for arg_name, arg_value in non_null_args.items()
            ]
        ):
            # then we've found the user we're looking for, because all of our query
            # terms matched this user.
            return entry

    # If we reach here, it means that no user matched all of our input query terms.
    return {"error": f"No such user given args: {non_null_args}"}


@router.get("/users/get")
def list_users(limit: int = 0) -> list[dict]:
    """
    List all of the users from the 'database'.
    """
    data = read_users()
    if not data:
        return []
    if limit:
        return list(data.values())[:limit]
    return list(data.values())


@router.get("/docs")
def get_documentation() -> list[dict]:
    """
    Get docs. The most important endpoint!
    """

    return [
        {
            "path": route.path,
            "methods": route.methods,
            "response_type": str(route.response_model),
            "parameters": [
                {"name": parameter.name, "parameter_type": str(parameter.annotation)}
                for parameter in inspect.signature(route.endpoint).parameters.values()
            ],
        }
        for route in router.routes
    ]


app.include_router(router=router)
