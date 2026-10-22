#!/usr/bin/with-contenv bashio

WEB_PORT=$(bashio::config 'web_port')
TOKEN=$(bashio::config 'token')

bashio::log.info "Starting LG-Plug device server on port 10086 and web port ${WEB_PORT}..."

if bashio::config.has_value 'token'; then
    exec python3 /app/server.py serve --port 10086 --web-port "${WEB_PORT}" --token "${TOKEN}"
else
    exec python3 /app/server.py serve --port 10086 --web-port "${WEB_PORT}"
fi
