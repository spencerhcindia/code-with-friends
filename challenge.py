import requests
import json

URL = 'http://192.168.68.59:8000/api'



def docs():
    """
    This function retrieves the dox from Vidovich's code challenge
    It prints an array of dicts
    """
    r = requests.get(f'{URL}/docs')
    print(json.dumps(r.json()))

def get():
    """
    This function retrieves all users
    It prints an array of dicts
    """

    r = requests.get(f'{URL}/users/get')
    print(json.dumps(r.json()))

def get_by_attr(name=None, id=None, email=None, address=None, phone=None):
    """
    This function retrieves a user by attribute
    It returns a dict
    """

    attr = {'user_name': name, 'user_id': id, 'user_address': address, 'user_email': email, 'user_phone': phone}
    r = requests.get(f'{URL}/user/get', params=attr)
    return r.json()


def add_user(name, email=None, phone=None, address=None):
    """
    This funtion adds a user
    Name attr is mandatory
    It printds the respoing from server (josh)
    """

    attr = {'name': name, 'email': email, 'phone': phone, 'address': address}

    r = requests.post(f'{URL}/users/add', params = attr)
    print(json.dumps(r.json()))

# A func that attempts to make user, but if the user wth the requested name exists we throw a ValueError

def create_if_not_exists(name, email=None, phone=None, address=None):
    """
    Thus funtion create user if not there
    otherwise it there
    It print the guy
    """
    response = get_by_attr(name, email, phone, address)

    if response.get('error'):
        add_user(name, email, phone, address)
    else:
        print(response)

def update(id, name=None, email=None, phone=None, address=None):
    """
    This guy make a change to a guy that already there, but maybe? need make a change
    It dont return or print nothin, but it can ;))
    """
    user = get_by_attr(id=id)
    if name is not None:
        user['name'] = name
    if email is not None:
        user['email'] = email
    if phone is not None:
        user['phone'] = phone
    if address is not None:
        user['address'] = address

    attr = {'user_name': user['name'], 'user_id': id, 'user_address': user['address'], 'user_email': user['email'], 'user_phone': user['phone']}
    r = requests.post(f'{URL}/user/update', params=attr)

def delete_user(id):
    """
    This make a man go away :(
    It print the response guy
    """

    r = requests.delete(f'{URL}/user/delete', params={'user_id': id})
    print(r.status_code)

delete_user('6ffcc958-7ee2-4c6c-a273-7d71eecc5b7a')
