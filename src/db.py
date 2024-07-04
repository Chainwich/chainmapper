import sqlite3
import json
import logging
import asyncio


class Handler:
    """Handle all SQLite connections required to create, update, and export the stored addresses."""

    def __init__(self, database="chainmapper.sqlite3"):
        self.database = database
        # Notably `connect` automatically creates the database if it doesn't already exist
        self.con = sqlite3.connect(self.database, check_same_thread=False)
        self.cursor = self.con.cursor()

        # Initialize the table if necessary
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS AddressMapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                address TEXT NOT NULL UNIQUE, 
                total_tx_count INTEGER NOT NULL DEFAULT 1, 
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )

        self.con.commit()

    async def store(self, address):
        """Store a new address into the SQLite database, or increments the counter by one if the given address already exists in the database."""
        await asyncio.to_thread(self._store, address)

    def _store(self, address):
        self.cursor.execute(
            """
            INSERT INTO AddressMapping (address) 
            VALUES 
                (?) ON CONFLICT(address) DO 
            UPDATE 
            SET 
                total_tx_count = total_tx_count + 1, 
                last_updated = CURRENT_TIMESTAMP;
        """,
            (address,),
        )
        self.con.commit()

    async def export(self, filename="export.json"):
        """Export the addresses from the SQLite database in descending order based on the transaction counts."""
        await asyncio.to_thread(self._export, filename)

    def _export(self, filename="export.json"):
        self.cursor.execute(
            """
            SELECT address, total_tx_count
            FROM AddressMapping
            ORDER BY total_tx_count DESC;
        """
        )
        records = self.cursor.fetchall()
        data = [{"address": record[0], "tx_count": record[1]} for record in records]
        data_json = json.dumps(data, indent=4)

        logging.info("Exporting the database's current state to '%s' (overwriting if an old copy exists)...", filename)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(data_json)

        logging.info("Data exported to '%s'", filename)


async def periodic_export(handler, interval):
    logging.info("Scheduled export task created")

    while True:
        await asyncio.sleep(interval)
        await handler.export()
