# syntax=docker/dockerfile:1

FROM python:3-alpine3.16
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 3000
<<<<<<< HEAD
CMD python3 ./main.py
=======
CMD python ./main.py

>>>>>>> parent of ba66be1 ( Dockerfile Changes)
