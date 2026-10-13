
import sys
from pathlib import Path

# Make the src directory importable during testing.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from ticket_tools import get_ticket_status


def test_existing_ticket_returns_correct_details():
    result = get_ticket_status("HD-1001")

    assert result["success"] is True
    assert result["ticket_id"] == "HD-1001"
    assert result["status"] == "In Progress"
    assert result["priority"] == "High"
    assert result["assigned_to"] == "Alex Morgan"


def test_unknown_ticket_returns_error():
    result = get_ticket_status("HD-9999")

    assert result["success"] is False
    assert result["error"] == "Ticket HD-9999 was not found."


def test_ticket_id_is_case_insensitive():
    result = get_ticket_status("hd-1002")

    assert result["success"] is True
    assert result["ticket_id"] == "HD-1002"
    assert result["assigned_to"] == "Jamie Lee"


def test_ticket_details_include_title():
    result = get_ticket_status("HD-1003")

    assert result["success"] is True
    assert result["title"] == "Laptop running slowly"
