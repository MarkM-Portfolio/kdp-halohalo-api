#!/usr/bin/env bash

set -e

if [[ "$KUBJUSTSLEEP" == "yes" ]]; then
  sleep 1000000d
fi

#echo "[Entrypoint] Install halohalo dependencies..."
#pip install -r requirements.txt

echo "[Entrypoint] halohalo flask api..."

ddtrace-run flask run --host=0.0.0.0 --port=$FLASK_RUN_PORT
