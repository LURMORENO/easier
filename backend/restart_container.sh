#!/bin/bash

# Stop and delete the container if it exists
docker stop easier-api 2>/dev/null
docker rm easier-api 2>/dev/null

# Remove previous image
docker rmi easier-backend 2>/dev/null

# Build image
docker build -t easier-backend .

# Create container (do not start yet)

docker create -p 5000:5000 \
    -v "$(pwd)/resources:/app/resources" \
    -e NGRAMS_BACKEND="sqlite" \
    --name easier-api easier-backend

# IMPORTANT: it is necessary to raise an independent container with nginx for https

# Start container
docker start easier-api

# Show logs
docker logs -f easier-api