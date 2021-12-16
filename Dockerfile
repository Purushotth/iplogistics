FROM python:3.9

MAINTAINER purush

ENV PYTHONUNBUFFERED 1

# RUN adduser purush
# USER purush

RUN mkdir /ipl
WORKDIR /ipl
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
WORKDIR /ipl

