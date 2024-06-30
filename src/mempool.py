import asyncio
import json
import threading
import websocket

from const import WS_ADDR

# FIFO queue for cross-thread communications
tx_queue = asyncio.Queue()
tx_count = 0


async def process_queue():
    """Handles emptying the transaction queue and calling the database module with the received data."""
    while True:
        # TODO: handle graceful shutdown
        tx_sender = tx_queue.get()
        # TODO: send `tx_sender` to the db module
        tx_count += 1
        tx_queue.task_done()


def on_message(_, msg, loop):
    msg_json = json.loads(msg)

    try:
        tx_sender = msg_json["transaction"]["from"]
    except KeyError as e:
        # TODO: log the seen KeyError `e` & handle what happens next (i.e. proper error handling)?
        return

    future = asyncio.run_coroutine_threadsafe(tx_queue.put(tx_sender), loop)
    future.result()  # Won't timeout


def on_error(_, err):
    # TODO: error handling
    exit(1)


def on_close(_, status_code, msg):
    # TODO: log `status_code` & `msg`
    pass


def on_open(ws):
    # TODO: log "Connection opened"

    # Subscribed entity could also be `pending_transactions` to receive the transactions directly
    # from the mempool.
    ws.send(json.dumps({"coin": "eth", "command": "subscribe", "entity": "confirmed_transaction"}))

    # TODO: log "Subscription message sent"


async def start_monitor():
    """Connects to the WebSocket feed of mined Ethereum transactions"""
    queue_processor = asyncio.create_task(process_queue())
    loop = asyncio.get_event_loop()
    ws = websocket.WebSocketApp(
        WS_ADDR,
        on_open=on_open,
        on_message=lambda ws, msg: on_message(ws, msg, loop),
        on_error=on_error,
        on_close=on_close,
    )

    # Run the WebSocket client in a separate thread
    # TODO: replace `run_forever` with something that can be signaled to shutdown gracefully
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    # Wait for the processor to finish cleaning up the queue before shutting down
    await queue_processor()
