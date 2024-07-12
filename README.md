# Ethereum network sender address mapper

Script that, once deployed in a Docker container, monitors a live feed of the Ethereum network via a WebSocket connection, stores the sender addresses with transaction counts, and creates statistics of the most active addresses.

## Development

Most critically `MODE=development` should be specified, as it sets the logging level from `INFO` to `DEBUG`. Low `EXPORT_INTERVAL` should be used for testing the export functionality (obviously).

```shell
mkvirtualenv chainmapper # OR 'workon chainmapper'
pip3 install -r requirements.txt
touch .env && echo -e "MODE=\"development\"\nEXPORT_INTERVAL=\"60\"" > .env # 60 seconds export period for testing
```

## Usage

The included `usage.sh` shellscript should be used for any kind of (development or production) deployment. It builds a new Docker image without caching, prompts for removal of any possible conflicting containers, and finally deploys the newly built image as a container with the `data/` local directory mounted as a volume.

```shell
chmod +x ./scripts/deploy.sh
./scripts/deploy.sh
```
