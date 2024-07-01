#!/usr/bin/env python3

import asyncio
import threading
import logging

from src.mempool import WebSocketThread, QueueProcessor
from src.db import Handler


def main():
    # FIFO queue for cross-thread communications
    q = asyncio.Queue()
    shutdown_event = threading.Event()
    handler = Handler()

    ws_thread = WebSocketThread(q, shutdown_event)
    qp_thread = QueueProcessor(q, shutdown_event, handler)

    ws_thread.start()
    qp_thread.start()

    try:
        ws_thread.join()
        qp_thread.join()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down threads.")
        shutdown_event.set()
        ws_thread.join()
        qp_thread.join()


if __name__ == "__main__":
    main()
