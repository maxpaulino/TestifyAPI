FROM python:3.8-slim-buster
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 3000

ENV OPEN_API_KEY=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
ENV MONGO_PASSWORD=7rpuXirwGWleZMjt
ENV JWT_SECRET_KEY=your-new-secret-key 
ENV USERNAME=maxpaulino
ENV PASSWORD=kevu9Gdb

CMD python3 ./main.py
