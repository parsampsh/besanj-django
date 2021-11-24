FROM python:3.8-alpine

ENV PATH="/app/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers mariadb-dev python3-dev musl-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN apk add --update --no-cache mariadb-connector-c

COPY . /app
WORKDIR /app
RUN chmod +x /app/scripts/*

RUN rm *.sqlite3

RUN adduser -D user
USER user

CMD ["entrypoint.sh"]
