
FROM python:3-alpine3.16
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 3000
CMD python3 ./main.py
