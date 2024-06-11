A simple client / server experiment using `requests` and `FastAPI`

## Installing

You can install the necessary dependencies by running the following commands, assuming you have Python 3 installed:

```shell
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Client Portion

Ensure that the virtual environment from the "Installing" section is active.
You will need to change URL to reflect the host running the server portion. Then, you can attempt to run the functions in challenge.py.

## Server portion

With the virtual environment from the "Installing" section active, run the server with the following commands:

```shell
cd server/
uvicorn --host 0.0.0.0 --reload main:app
```
