#!/usr/bin/env python3

import os
import asyncio
import threading
import logging
import aioprocessing
from dotenv import load_dotenv

from src.mempool import WebSocketThread, QueueProcessor
from src.db import Handler, periodic_export


async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logging.info("Received exit signal %s", signal.name)

    logging.info("Napping for a bit before shutting down...")
    await asyncio.sleep(2)

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for t in tasks:
        t.cancel()

    logging.info("Cancelling %d outstanding tasks", len(tasks))
    await asyncio.gather(*tasks, return_exceptions=True)

    logging.info("Flushing metrics")
    loop.stop()


def load_cfg(dotenv_path=".env"):
    load_dotenv(dotenv_path)
    cfg = {}

    print(f"[+] Environment variables loaded from '{dotenv_path}'\n---")

    cfg["MODE"] = os.getenv("MODE")
    cfg["EXPORT_INTERVAL"] = os.getenv("EXPORT_INTERVAL")

    if cfg["MODE"] is None:
        cfg["MODE"] = "production"

    if cfg["EXPORT_INTERVAL"] is None:
        cfg["EXPORT_INTERVAL"] = 24 * 60 * 60  # 24 hours in seconds
    else:
        cfg["EXPORT_INTERVAL"] = int(cfg["EXPORT_INTERVAL"])

    return cfg


def main():
    cfg = load_cfg()
    mode = cfg["MODE"]

    if mode.lower() == "production":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=log_level)
    logging.info("Logger initialized")
    logging.info("MODE: %s", cfg["MODE"])
    logging.info("EXPORT_INTERVAL: %d (seconds)", cfg["EXPORT_INTERVAL"])

    # FIFO queue for crosst-thread communications
    q = aioprocessing.AioQueue()
    handler = Handler()
    shutdown_event = threading.Event()

    shutdown_loop = asyncio.new_event_loop()
    export_loop = asyncio.new_event_loop()

    export_thread = threading.Thread(
        target=periodic_export,
        args=(
            export_loop,
            handler,
            cfg["EXPORT_INTERVAL"],
            shutdown_event,
        ),
    )
    export_thread.start()

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
        shutdown_loop.run_until_complete(shutdown(shutdown_loop))
        ws_thread.join()
        qp_thread.join()
        export_thread.join()
    finally:
        export_loop.stop()
        export_loop.close()
        shutdown_loop.stop()
        shutdown_loop.close()


if __name__ == "__main__":
    main()
