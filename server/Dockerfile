FROM python:3.9-slim

RUN pip3 install mysql.connector 

RUN mkdir /data
COPY . .

EXPOSE 3306
EXPOSE 9999


CMD ["python3", "./server.py"]