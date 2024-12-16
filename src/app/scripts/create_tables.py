import sqlite3
import src.app.config.db_config as config

# Open connection and enable foreign key support explicitly for SQLite
conn = sqlite3.connect(config.DB)
conn.execute("PRAGMA foreign_keys = ON;")  # Enabling foreign key support for SQLite

with conn:
    # Creating the users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT,
            role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
        );
    ''')

    # Creating the assets table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            serial_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL CHECK(status IN ('available', 'assigned'))
        );
    ''')

    # Creating the issues table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            issue_id TEXT PRIMARY KEY,
            report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES assets(serial_number) ON DELETE CASCADE
        );
    ''')

    # Creating the assets assigned table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assets_assigned (
            asset_assigned_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES assets(serial_number) ON DELETE CASCADE
        );
    ''')
