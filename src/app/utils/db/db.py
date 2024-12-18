import sqlite3
import src.app.config.db_config as config


class DB:

    @staticmethod
    def get_connection():
        """Return the singleton DB connection."""
        conn = sqlite3.connect(config.DB)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
