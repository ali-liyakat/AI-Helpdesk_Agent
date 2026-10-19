
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import database
import ticket_tools


@pytest.fixture(autouse=True)
def isolated_ticket_database(tmp_path, monkeypatch):
    """Give every test its own clean SQLite database."""

    test_database = tmp_path / "test_helpdesk.db"

    monkeypatch.setattr(
        ticket_tools,
        "DATABASE_PATH",
        test_database,
    )

    database.initialize_database(test_database)
    database.seed_initial_tickets(test_database)
