FROM python:3.11-alpine

WORKDIR /app

COPY server.py /app/server.py

EXPOSE 10086 7896

CMD ["python3", "/app/server.py", "serve", "--port", "10086", "--web-port", "7896"]
