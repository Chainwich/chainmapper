import asyncio
import json
import threading
import logging
import websockets

from const import WS_ADDR


class WebSocketThread(threading.Thread):
    def __init__(self, q, shutdown_event):
        super().__init__()
        self.q = q
        self.shutdown_event = shutdown_event
        self.tx_count = 0

    async def connect(self):
        async with websockets.connect(WS_ADDR) as ws:
            while not self.shutdown_event.is_set():
                try:
                    msg = await ws.recv()
                    data = self.handle_msg(msg)

                    if data is None:
                        continue

                    self.q.put(data)
                except websockets.exceptions.ConnectionClosed:
                    logging.info("WebSocket connection closed")
                    self.shutdown_event.set()
                    break
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logging.error("WebSocket error: %s", e)
                    self.shutdown_event.set()
                    break

    def handle_msg(self, msg):
        msg_json = json.loads(msg)

        try:
            tx_sender = msg_json["transaction"]["from"]
        except KeyError as e:
            logging.error("Error parsing a WebSocket message: %s", e)
            return None

        self.tx_count += 1

        if self.tx_count % 1000 == 0:
            logging.info("Currently at %d received transactions", self.tx_count)

        return tx_sender

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.connect())
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("WebSocket thread crashed: %s", e)
            self.shutdown_event.set()
        finally:
            loop.close()


class QueueProcessor(threading.Thread):
    def __init__(self, q, shutdown_event, handler):
        super().__init__()
        self.q = q
        self.shutdown_event = shutdown_event
        self.handler = handler

    def run(self):
        while not self.shutdown_event.is_set():
            try:
                tx_sender = self.q.get()  # Waits here until new msg is available
                self.handler.store(tx_sender)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                logging.error("QueueProcessor thread crashed: %s", e)
                self.shutdown_event.set()
                break
