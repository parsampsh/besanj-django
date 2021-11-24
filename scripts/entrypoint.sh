#!/bin/sh

set -e

python3 manage.py migrate

uwsgi --socket :8000 --master --enable-threads --module besanj_backend.wsgi
