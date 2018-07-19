FROM python:3.6-alpine

COPY . /queue
WORKDIR /queue

RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev postgresql-dev
ENV LIBRARY_PATH=/lib:/usr/lib

RUN pip install -r requirements.txt

ENTRYPOINT celery -A tasks worker --loglevel=info