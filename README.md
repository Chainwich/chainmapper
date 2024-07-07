# Ethereum network sender address mapper

Script that, once deployed in a Docker container, monitors a live feed of the Ethereum network via a WebSocket connection, stores the sender addresses with transaction counts, and creates statistics of the most active addresses.

## Development

```shell
mkvirtualenv chainmapper # OR 'workon chainmapper'
pip3 install -r requirements.txt
touch .env && echo -e "MODE=\"development\"\nEXPORT_INTERVAL=\"60\"" > .env # 60 seconds export period for testing
```

## Usage

```shell
chmod +x ./scripts/deploy.sh
./scripts/deploy.sh
```
