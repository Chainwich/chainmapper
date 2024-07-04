import asyncio
import json
import threading
import logging
import websockets

from src.const import WS_ADDR, SUB_MSG


class WebSocketThread(threading.Thread):
    """Handle connection, subscription, and message parsing for the Blockchain.com WebSocket."""

    def __init__(self, q, shutdown_event, sub_msg=SUB_MSG):
        super().__init__()
        self.name = "WebSocketThread"
        self.q = q
        self.shutdown_event = shutdown_event
        self.sub_msg = sub_msg
        self.tx_count = 0

    async def connect(self):
        async with websockets.connect(WS_ADDR) as ws:
            logging.info("WebSocket connection established successfully")
            await ws.send(self.sub_msg)
            logging.info("Subscription message sent")

            # Ignores the confirmation message, as it can't be parsed with the same template
            _ = await ws.recv()

            while not self.shutdown_event.is_set():
                try:
                    msg = await ws.recv()
                    data = self.handle_msg(msg)

                    if data is None:
                        continue

                    await self.q.coro_put(data)
                except websockets.exceptions.ConnectionClosed:
                    logging.info("WebSocket connection closed")
                    self.shutdown_event.set()
                    break
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logging.error("WebSocket error: %s", str(e))
                    self.shutdown_event.set()
                    break

    def handle_msg(self, msg):
        msg_json = json.loads(msg)

        try:
            tx_sender = msg_json["transaction"]["from"]
        except KeyError as e:
            logging.error("Error parsing a WebSocket message: %s", str(e))
            return None

        self.tx_count += 1

        if self.tx_count % 1000 == 0:
            logging.info("Currently at %d received transactions", self.tx_count)

        return tx_sender

    def run(self):
        """Start the WebSocket thread that'll run until it receives a shutdown message or crashes."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.connect())
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("WebSocket thread crashed: %s", str(e))
            self.shutdown_event.set()
        finally:
            loop.close()


class QueueProcessor(threading.Thread):
    """Handle processing of items from the cross-thread queue where the WebSocket thread feeds data into."""

    def __init__(self, q, shutdown_event, handler):
        super().__init__()
        self.name = "QueueProcessor"
        self.q = q
        self.shutdown_event = shutdown_event
        self.handler = handler

    async def process_queue(self):
        while not self.shutdown_event.is_set():
            try:
                tx_sender = await self.q.coro_get()  # Waits here until new msg is available
                await self.handler.store(tx_sender)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                logging.error("QueueProcessor thread crashed: %s", str(e))
                self.shutdown_event.set()
                break

    def run(self):
        """Start the queue processing thread that'll run until it receives a shutdown message or crashes."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.process_queue())
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("QueueProcessor thread crashed: %s", str(e))
            self.shutdown_event.set()
        finally:
            loop.close()
