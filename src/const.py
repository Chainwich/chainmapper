import json

WS_ADDR = "wss://ws.blockchain.info/coins"
SUB_MSG = json.dumps({"coin": "eth", "command": "subscribe", "entity": "confirmed_transaction"})
