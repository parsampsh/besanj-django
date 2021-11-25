# Deployment
You can deploy this project using docker-compose.

To make the needed containers, first copy this file:

```shell
$ cp .docker-compose-dotenv-example .env
```

then, run the docker compose:

```shell
$ sudo docker-compose --file docker-compose-deploy.yml up
```

after that, run the migrations:

```shell
$ sudo docker ps # run this and find id of the app container
$ sudo docker exec <app-container-id> python manage.py migrate
```

Now, app is ready on http://localhost:8080

Also if you want change default port `8080` to something else, you can update file `.env` and change this line:

```
...
PRODUCTION_PORT=80 # or whatever you want
...
```

And re-run docker compose command.

