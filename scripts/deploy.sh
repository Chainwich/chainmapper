#!/usr/bin/env bash

echo "[+] Starting the deployment script"

! command -v docker &> /dev/null && echo "[!] Docker could not be found, exiting..." && exit 1

# Building with '--no-cache' ensures a fresh build will always be used
echo -e "\n[+] Building the Docker image without caching..."
docker build --no-cache -t chainmapper .

[ ! -d "./data" ] && mkdir data && echo -e "\n[+] Created the default volume directory 'data'"

OLD_ID=$(docker ps -a -q -f name="chainmapper-prod")

if [ "$OLD_ID" ]
then
    read -p "[?] Existing container found with id '$OLD_ID', do you want to remove it? " -n 1 -r
    [[ "$REPLY" =~ ^[Yy]$ ]] || (echo "[!] Exiting..." && exit 0)
    docker rm "$OLD_ID" &> /dev/null
fi

echo -e "\n[+] Deploying the container with 'docker run' ('data' as the volume)..."
docker run -it --restart unless-stopped -v ./data:/app/data --name chainmapper-prod -d chainmapper
