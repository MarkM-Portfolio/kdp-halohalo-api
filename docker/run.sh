#!/usr/bin/env bash
docker rm api-halohalo || true

# if apple m1 chip
if [[ `uname -m` == 'arm64' ]]; then
    docker run --platform linux/x86_64 --publish 8000:8000 --env-file=docker/.env.example --name api-halohalo api-halohalo:latest
else
    docker run --publish 8000:8000 --env-file=docker/.env.example --name api-halohalo api-halohalo:latest
fi
