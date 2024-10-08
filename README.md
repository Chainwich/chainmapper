# Ethereum network sender address mapper

This script, designed for deployment in a Docker container, monitors the Ethereum network's mempool via a WebSocket connection. It tracks sender addresses and their transaction counts, generating a list of the most active addresses. This data can be used to black-/whitelist addresses in other research projects, ensuring targeting is done based on up-to-date information.

## Configuration

A list of the possible environment variables and their purpose:

- `MODE`: Either `development` or `production`, the logging level is set based on this
- `EXPORT_INTERVAL`: The interval of how often the SQLite database is exported as a JSON file, does nothing if `IS_EXPORT` is not true
  - Notably set as a string (similar to all environment variables)
- `IS_EXPORT`: Boolean that indicates whether the aforementioned export task is enabled or not
  - Possible values that are interpreted as `True` (case insensitive): `true`, `1`, and `t`

## Development

```shell
mkvirtualenv chainmapper # OR 'workon chainmapper'
pip3 install -r requirements.txt
touch .env # Optional, see the previous section
```

## Usage

The included `deploy.sh` shellscript should be used for any kind of (development or production) deployment. It builds a new Docker image without caching, prompts for removal of any possible conflicting containers, and finally deploys the newly built image as a container with the `data/` local directory mounted as a volume.

```shell
chmod +x ./scripts/deploy.sh
# Add `-y` flag to automatically overwrite existing containers with the same name
./scripts/deploy.sh
```

Use the following command if you wish to proxy the WebSocket connection:

```shell
# Proxy format: <protocol>://<ip>:<port>
./scripts/deploy.sh -p <proxy>
```
