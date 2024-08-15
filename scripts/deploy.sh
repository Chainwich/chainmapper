#!/usr/bin/env bash

AUTOREMOVE=false
VOLUME_PATH="./data" # Local path to the volume's mount point
IS_PROXIED=false
PROXY=""

while getopts ":hyp:" opt
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
        p)
            IS_PROXIED=true
            PROXY=${OPTARG}
            echo -e "[+] Proxying enabled: $PROXY"
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

OLD_ID=$(docker ps -a -q -f name="chainmapper")

if [ "$OLD_ID" ] && [ "$AUTOREMOVE" = true ]
then
    echo -e "\n[+] Removing existing container with the same tag ($OLD_ID)"
    docker stop "$OLD_ID" &> /dev/null
    docker rm "$OLD_ID" &> /dev/null
elif [ "$OLD_ID" ]
then
    read -p "[?] Existing container found with id '$OLD_ID', do you want to remove it? " -n 1 -r
    [[ "$REPLY" =~ ^[Yy]$ ]] || (echo "[!] Exiting..." && exit 0)
    docker stop "$OLD_ID" &> /dev/null
    docker rm "$OLD_ID" &> /dev/null
fi

echo -e "\n[+] Deploying the container with 'docker run' ('data' as the volume)..."

if [ "$IS_PROXIED" = true ]
then
    # Override the default entrypoint to run the connections through the given proxy
    docker run -it --restart unless-stopped -v $VOLUME_PATH:/app/data --name chainmapper --entrypoint /bin/bash -d chainmapper -c "HTTPS_PROXY=$PROXY python main.py"
else
    docker run -it --restart unless-stopped -v $VOLUME_PATH:/app/data --name chainmapper -d chainmapper
fi
