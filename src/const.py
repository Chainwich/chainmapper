import json

# Blockchain.com endpoint and the subscription message which initializes the "transaction stream"
WS_ADDR = "wss://ws.blockchain.info/coins"
# Optionally `confirmed_transaction` can be used (bursts of data instead of a steady stream, which is worse for the overall performance)
SUB_MSG = json.dumps({"coin": "eth", "command": "subscribe", "entity": "pending_transaction"})

# Pause before reconnecting after the WebSocket connection is accidentally dropped by either party
WS_RECONNECT_PAUSE = 2

# Timeout for asynchronous WebSocket reading (seconds)
WS_INTERMSG_TIMEOUT = 1

# Timeout for asynchronous queue operations (`coro_get` and `coro_put`, seconds)
QUEUE_OP_TIMEOUT = 1

# Paths inside the Docker container where data is stored/exported (should match with the mounted volume in `deploy.sh`)
DEFAULT_DB_PATH = "./data/chainmapper.sqlite3"
DEFAULT_EXPORT_PATH = "./data/export.json"

# Defaults to environment variables (must be strings for this reason, interval in seconds)
DEFAULT_MODE = "production"
DEFAULT_EXPORT_INTERVAL = "10800"
DEFAULT_IS_EXPORT = "False"
