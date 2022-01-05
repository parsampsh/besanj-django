# Besanj - Backend API

## Getting Started
To setup the development environment for this project, you have 2 options:

- Using Docker Compose
- Manual Setup

#### Manual setup
You need to have installed Python, Pip and Virtualenv.

1. create a virtual environment:

```shell
$ virtualenv .venv
```

2. install requirements:

```shell
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

3. run the migrations:

```shell
$ python manage.py migrate
```

4. run the server:

```shell
$ python manage.py runserver 8000
```

#### Using docker-compose
You need to have installed Docker and Docker-Compose.

Then you can run:

```shell
$ docker-compose up
```

then the server is accessible on `http://localhost:8000`.

### Running the tests
For running project tests:

```shell
$ python3 manage.py test
```

or if you use docker compose for development:

```shell
$ sudo docker exec <app-container> python manage.py test
```

## Frontend
The frontend app for this project is available at [here](https://github.com/parsampsh/besanj-frontend)

