FROM python:3.6-alpine

ADD . /api
WORKDIR /api

RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev postgresql
ENV LIBRARY_PATH=/lib:/usr/lib

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5000

RUN pip install gunicorn

# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]