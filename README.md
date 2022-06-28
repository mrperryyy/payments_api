# Payment API

TODO: Add short description describing this app

## Set up environment

Create Python virtual enviroment and and activate it

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install application requirements

```bash
$ make install
```

## Developing

Run unit tests

```bash
$ make test
```

To start the server locally, run

```bash
$ make run
```

Clean up

```bash
$ make clean
```

## .env

```bash
FLASK_APP=api/app.py
FLASK_ENV=development
```