
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from ticket_tools import create_ticket, get_ticket_status


def test_create_ticket_successfully():
    result = create_ticket(
        "Email application is not opening",
        "High",
    )

    assert result["success"] is True
    assert result["ticket_id"].startswith("HD-")
    assert result["title"] == "Email application is not opening"
    assert result["status"] == "Open"
    assert result["priority"] == "High"
    assert result["assigned_to"] == "Unassigned"


def test_created_ticket_can_be_retrieved():
    result = create_ticket("Cannot access the intranet")

    ticket_id = result["ticket_id"]
    retrieved = get_ticket_status(ticket_id)

    assert retrieved["success"] is True
    assert retrieved["title"] == "Cannot access the intranet"


def test_empty_title_is_rejected():
    result = create_ticket("   ")

    assert result["success"] is False
    assert result["error"] == "Ticket title cannot be empty."


def test_invalid_priority_is_rejected():
    result = create_ticket("Printer issue", "Urgent")

    assert result["success"] is False
    assert "Priority must be" in result["error"]
