FROM python:3.9

MAINTAINER purush

ENV PYTHONUNBUFFERED 1

RUN mkdir /ipl
WORKDIR /ipl
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


# RUN adduser -D purush
# USER purush
