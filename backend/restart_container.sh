#!/bin/bash

# Stop and delete the container if it exists
docker stop easier-api 2>/dev/null
docker rm easier-api 2>/dev/null

# Remove previous image
docker rmi easier-backend 2>/dev/null

# Build image
docker build -t easier-backend .

# Create container (do not start yet)
docker create -p 5000:5000 --name easier-api easier-backend

# Copy models/resources into container
docker cp resources/. easier-api:/app/resources/

# Start container
docker start easier-api

# Show logs
docker logs -f easier-api