import json

WS_ADDR = "wss://ws.blockchain.info/coins"
SUB_MSG = json.dumps({"coin": "eth", "command": "subscribe", "entity": "confirmed_transaction"})

# EXPORT_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
EXPORT_INTERVAL = 30
