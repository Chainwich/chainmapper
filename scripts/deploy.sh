#!/usr/bin/env bash

AUTOREMOVE=false
VOLUME_PATH="./data" # Local path to the volume's mount point

while getopts ":hy" opt
do
    case "$opt" in
        h)
            echo "Usage: $0 [-y]"
            exit 0
            ;;
        y)
            echo -e "[+] Automatically removing all containers with the same tag (if any)\n"
            AUTOREMOVE=true
            ;;
        *)
            exit 1
            ;;
    esac
done

! command -v docker &> /dev/null && echo "[!] Docker could not be found, exiting..." && exit 1

# Building with '--no-cache' ensures a fresh build will always be used
echo -e "[+] Building the Docker image without caching...\n"
docker build --no-cache -t chainmapper .

[ ! -d "./data" ] && mkdir data && echo -e "\n[+] Created the default volume directory 'data'"

OLD_ID=$(docker ps -a -q -f name="chainmapper-prod")

if [ "$OLD_ID" ] && [ "$AUTOREMOVE" = true ]
then
    echo -e "\n[+] Removing existing container with the same tag ($OLD_ID)"
    docker rm "$OLD_ID" &> /dev/null
elif [ "$OLD_ID" ]
then
    read -p "[?] Existing container found with id '$OLD_ID', do you want to remove it? " -n 1 -r
    [[ "$REPLY" =~ ^[Yy]$ ]] || (echo "[!] Exiting..." && exit 0)
    docker rm "$OLD_ID" &> /dev/null
fi

echo -e "\n[+] Deploying the container with 'docker run' ('data' as the volume)..."
docker run -it --restart unless-stopped -v $VOLUME_PATH:/app/data --name chainmapper-prod -d chainmapper
