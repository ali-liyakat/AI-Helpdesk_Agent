
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import database
import ticket_tools


def test_created_ticket_survives_database_reopening(tmp_path, monkeypatch):
    db_path = tmp_path / "persistence.db"

    monkeypatch.setattr(ticket_tools, "DATABASE_PATH", db_path)

    database.initialize_database(db_path)
    database.seed_initial_tickets(db_path)

    created = ticket_tools.create_ticket(
        "Persistence test ticket",
        "High",
    )

    # Simulate reopening the database in a separate connection.
    with database.get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (created["ticket_id"],),
        ).fetchone()

    assert row is not None
    assert row["title"] == "Persistence test ticket"
    assert row["priority"] == "High"


def test_ticket_update_survives_database_reopening(tmp_path, monkeypatch):
    db_path = tmp_path / "persistence.db"

    monkeypatch.setattr(ticket_tools, "DATABASE_PATH", db_path)

    database.initialize_database(db_path)
    database.seed_initial_tickets(db_path)

    result = ticket_tools.update_ticket(
        "HD-1001",
        status="Resolved",
        priority="Low",
    )

    assert result["success"] is True

    with database.get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT status, priority
            FROM tickets
            WHERE ticket_id = ?
            """,
            ("HD-1001",),
        ).fetchone()

    assert row["status"] == "Resolved"
    assert row["priority"] == "Low"


def test_seeding_does_not_overwrite_existing_ticket(tmp_path):
    db_path = tmp_path / "persistence.db"

    database.initialize_database(db_path)
    database.seed_initial_tickets(db_path)

    with database.get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE tickets
            SET status = ?
            WHERE ticket_id = ?
            """,
            ("Resolved", "HD-1001"),
        )

    # Re-running initialization and seeding must preserve the update.
    database.initialize_database(db_path)
    database.seed_initial_tickets(db_path)

    with database.get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT status FROM tickets WHERE ticket_id = ?",
            ("HD-1001",),
        ).fetchone()

    assert row["status"] == "Resolved"
