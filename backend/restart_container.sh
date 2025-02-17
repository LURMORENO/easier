#!/bin/bash

# Stop and delete the container if it exists
docker stop easier-api && docker rm -f easier-api

# Build docker image
docker build -t easier-backend .

# Run a new container
docker run -d -p 5000:5000 --name easier-api easier-backend

# Show real time logs
docker logs -f easier-api