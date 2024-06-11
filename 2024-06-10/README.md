A simple client / server experiment using `requests` and `FastAPI`

## Client Portion

You need to change URL to the host running the server portion. Then, you can attempt to run the functions in challenge.py

## Server portion

To run the server, make sure that you've installed the requirements, and then run

```shell
cd server/
uvicorn --host 0.0.0.0 --reload main:app
```
