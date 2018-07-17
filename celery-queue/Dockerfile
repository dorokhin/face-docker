FROM python:3.6-alpine

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
ENV UPLOAD_FOLDER /uploads/

ENV SERVICE_URL https://castor.dorokhin.moscow

COPY . /queue
WORKDIR /queue

RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

RUN pip install -r requirements.txt

ENTRYPOINT celery -A tasks worker --loglevel=info