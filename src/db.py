import sqlite3


class Handler:
    """Handles all SQLite connections required to create, update, and export the stored addresses."""

    def __init__(self, database="chainmapper.sqlite3"):
        self.database = database
        # Notably `connect` automatically creates the database if it doesn't already exist
        self.con = sqlite3.connect(self.database)
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

    def store(self, address):
        self.cursor.execute(
            """
            INSERT INTO AddressTracking (address) 
            VALUES 
                (?) ON CONFLICT(address) DO 
            UPDATE 
            SET 
                total_tx_count = total_tx_count + 1, 
                last_updated = CURRENT_TIMESTAMP;
        """,
            address,
        )
        self.con.commit()

    def export(self):
        # TODO: handle exporting
        pass
