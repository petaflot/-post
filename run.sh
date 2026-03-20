#!/bin/bash

HOST=0.0.0.0	# 127.0.0.1 is fine in most cases
PORT=12345

mkdir -p data

echo "Starting Quart app..."
quart --app app.main run --host ${HOST} --port ${PORT} &

sleep 1

echo "Starting mitmproxy..."
mitmdump -s proxy/gather.py &
wait
