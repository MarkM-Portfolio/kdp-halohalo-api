#!/usr/bin/env bash
docker rm api-halohalo || true

# if apple m1 chip
if [[ `uname -m` == 'arm64' ]]; then
    docker build --platform linux/x86_64 -t api-halohalo:latest .
else
    docker build -t api-halohalo:latest .
fi
