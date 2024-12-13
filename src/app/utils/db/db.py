import sqlite3
import AssetManagement.src.app.config.config as config


class DB:

    @staticmethod
    def get_connection():
        """Return the singleton DB connection."""
        conn = sqlite3.connect(config.DB)
        conn.row_factory = sqlite3.Row
        return conn