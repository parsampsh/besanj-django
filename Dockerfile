FROM python:3.8-alpine

ENV PATH="/app/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r /requirements.txt
RUN apk del .tmp

COPY . /app
WORKDIR /app
RUN chmod +x /app/scripts/*

RUN adduser -D user
USER user

RUN python3 manage.py migrate

CMD ["entrypoint.sh"]
