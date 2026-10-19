
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "helpdesk.db"


def get_connection(database_path=None):
    """Connect to the selected SQLite database."""
    path = Path(database_path) if database_path else DATABASE_PATH

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path=None):
    """Create the tickets table if it does not exist."""
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                assigned_to TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def seed_initial_tickets(database_path=None):
    """Insert starter tickets without overwriting existing tickets."""
    initial_tickets = [
        ("HD-1001", "Unable to connect to office Wi-Fi",
         "In Progress", "High", "Alex Morgan"),
        ("HD-1002", "Request access to the reporting dashboard",
         "Open", "Medium", "Jamie Lee"),
        ("HD-1003", "Laptop running slowly",
         "Resolved", "Low", "Taylor Chen"),
    ]

    with get_connection(database_path) as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO tickets
                (ticket_id, title, status, priority, assigned_to)
            VALUES (?, ?, ?, ?, ?)
            """,
            initial_tickets,
        )


if __name__ == "__main__":
    initialize_database()
    seed_initial_tickets()
    print(f"Database initialized and seeded at: {DATABASE_PATH}")
