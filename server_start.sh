#!/bin/bash
echo "Stopping and removing existing containers..."
docker stop svtdl watchtower
docker rm svtdl watchtower

echo "Pulling latest images..."
docker pull mathin/svtdl:latest
docker pull containrrr/watchtower

echo "Starting app container..."
# old line:
#docker run -d --name svtdl -p 8181:5000 -v /mnt/Filmer/!NYTT:/app/downloads --restart unless-stopped mathin/svtdl:latest
docker run -d --name svtdl --restart unless-stopped \
 -p 5000:5000 \
 -v /mnt/Filmer/!NYTT:/app/downloads \
 --name svtdl mathin/svtdl:latest

echo "Starting Watchtower..."
docker run -d --name watchtower --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower --cleanup --interval 3600 svtdl

echo "Setup complete. Containers running."