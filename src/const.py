import json

DEFAULT_MODE = "production"

WS_ADDR = "wss://ws.blockchain.info/coins"
# Optionally `confirmed_transaction` can be used (bursts of data instead of a steady stream, which is worse for the overall performance)
SUB_MSG = json.dumps({"coin": "eth", "command": "subscribe", "entity": "pending_transaction"})
WS_RECONNECT_PAUSE = 2  # Seconds
WS_INTERMSG_TIMEOUT = 1  # Seconds

DEFAULT_EXPORT_PATH = "./data/export.json"
DEFAULT_EXPORT_INTERVAL = 10800  # 3 hours
