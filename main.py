#!/usr/bin/env python3

import os
import sys
import asyncio
import threading
import logging
import signal
from collections import namedtuple
import sqlite3
import aioprocessing
import websockets
from dotenv import load_dotenv

from src.const import DEFAULT_MODE, DEFAULT_EXPORT_INTERVAL, DEFAULT_IS_EXPORT, VERSION
from src.mempool import WebSocketThread, QueueProcessor
from src.db import Handler, periodic_export

Config = namedtuple("Config", ["mode", "export_interval", "is_export"])


async def shutdown(loop, signal=None):
    """Run cleanup tasks tied to the service's shutdown."""
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
    """Parse configuration from environment variables located in `dotenv_path` or from defaults."""
    load_dotenv(dotenv_path)
    print(f"[+] Environment variables loaded from '{dotenv_path}'\n---")

    mode = os.getenv("MODE", DEFAULT_MODE).lower()
    export_interval = int(os.getenv("EXPORT_INTERVAL", DEFAULT_EXPORT_INTERVAL))
    is_export = os.getenv("IS_EXPORT", DEFAULT_IS_EXPORT).lower() in ("true", "1", "t")

    cfg = Config(mode, export_interval, is_export)

    return cfg


def main():
    cfg = load_cfg()

    if cfg.mode == "production":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=log_level)
    logging.info("Logger initialized")
    logging.info("Currently running version %s", VERSION)
    logging.info("MODE: %s", cfg.mode)
    logging.info("EXPORT_INTERVAL: %d (seconds)", cfg.export_interval)
    logging.info("IS_EXPORT: %r", cfg.is_export)

    # Information for debugging issues caused by potential version differences
    logging.info("Python version: %s", sys.version)
    logging.info("aioprocessing version: %s", aioprocessing.__version__)
    logging.info("websockets version: %s", websockets.__version__)
    logging.info("sqlite3 version: %s", sqlite3.version)

    # FIFO queue for cross-thread communications
    q = aioprocessing.AioQueue()
    handler = Handler()
    shutdown_event = threading.Event()

    shutdown_loop = asyncio.new_event_loop()
    export_loop = asyncio.new_event_loop()

    ws_thread = WebSocketThread(q, shutdown_event)
    qp_thread = QueueProcessor(q, shutdown_event, handler)

    export_thread = threading.Thread(
        target=periodic_export,
        args=(
            export_loop,
            handler,
            cfg.export_interval,
            cfg.is_export,
            shutdown_event,
        ),
    )

    ws_thread.start()
    qp_thread.start()
    export_thread.start()

    def handle_exit():
        logging.info("Shutdown procedure initialized")

        shutdown_event.set()
        shutdown_loop.run_until_complete(shutdown(shutdown_loop))

        # NOTE: It's vital to close the queue processor first so that it doesn't halt the shutdown
        qp_thread.join()
        ws_thread.join()
        export_thread.join()

    def handle_signal(signal, _frame):
        logging.info("Received signal '%s', shutting down...", signal)
        handle_exit()

    # SIGINT and SIGTERM signal handler (mainly for Docker)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        qp_thread.join()
        ws_thread.join()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down threads")
        handle_exit()
    finally:
        export_loop.stop()
        export_loop.close()
        logging.info("Export loop shut down")

        shutdown_loop.stop()
        shutdown_loop.close()
        logging.info("Shutdown loop shut down")

        logging.info("Shutdown sequence completed successfully!")


if __name__ == "__main__":
    main()
