ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.19
FROM $BUILD_FROM

ENV LANG C.UTF-8

WORKDIR /app
COPY server.py /app/server.py
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
