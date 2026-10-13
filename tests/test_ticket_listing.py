
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from ticket_tools import list_tickets


def test_list_all_tickets():
    result = list_tickets()

    assert result["success"] is True
    assert result["count"] == len(result["tickets"])
    assert result["count"] >= 3


def test_list_open_tickets():
    result = list_tickets("Open")

    assert result["success"] is True
    assert all(
        ticket["status"] == "Open"
        for ticket in result["tickets"]
    )


def test_list_tickets_ignores_status_case():
    result = list_tickets("open")

    assert result["success"] is True
    assert all(
        ticket["status"] == "Open"
        for ticket in result["tickets"]
    )


def test_list_tickets_rejects_invalid_status():
    result = list_tickets("Waiting")

    assert result["success"] is False
    assert "Status must be" in result["error"]
