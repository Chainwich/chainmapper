#!/usr/bin/env python3

import asyncio
import threading
import logging
import aioprocessing
from dotenv import dotenv_values

from src.mempool import WebSocketThread, QueueProcessor
from src.db import Handler, periodic_export
from src.const import EXPORT_INTERVAL


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


def main(env_path=".env"):
    cfg = dotenv_values(env_path)
    mode = cfg["MODE"]

    if mode is None or mode.lower() == "production":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=log_level)

    # FIFO queue for crosst-thread communications
    q = aioprocessing.AioQueue()
    handler = Handler()

    loop = asyncio.new_event_loop()
    # TODO: handle scheduling of the export task
    # loop.create_task(periodic_export(handler, EXPORT_INTERVAL))
    # export_task_fut = asyncio.run_coroutine_threadsafe(periodic_export, loop)
    shutdown_event = threading.Event()

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
        loop.run_until_complete(shutdown(loop))
        ws_thread.join()
        qp_thread.join()
    finally:
        loop.stop()
        loop.close()


if __name__ == "__main__":
    main()
