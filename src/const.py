import json

WS_ADDR = "wss://ws.blockchain.info/coins"
SUB_MSG = json.dumps({"coin": "eth", "command": "subscribe", "entity": "confirmed_transaction"})
WS_RECONNECT_PAUSE = 2  # Seconds

DEFAULT_EXPORT_PATH = "./data/export.json"
