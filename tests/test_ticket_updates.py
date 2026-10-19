
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from ticket_tools import get_ticket_status, update_ticket


def test_update_ticket_status():
    result = update_ticket("HD-1001", status="Resolved")

    assert result["success"] is True
    assert result["status"] == "Resolved"


def test_update_ticket_priority():
    result = update_ticket("HD-1001", priority="Low")

    assert result["success"] is True
    assert result["priority"] == "Low"


def test_update_ticket_rejects_unknown_ticket():
    result = update_ticket("HD-9999", status="Resolved")

    assert result["success"] is False
    assert "was not found" in result["error"]


def test_update_ticket_rejects_invalid_status():
    result = update_ticket("HD-1001", status="Waiting")

    assert result["success"] is False
    assert "Status must be" in result["error"]


def test_update_ticket_rejects_invalid_priority():
    result = update_ticket("HD-1001", priority="Urgent")

    assert result["success"] is False
    assert "Priority must be" in result["error"]


def test_update_ticket_requires_a_field():
    result = update_ticket("HD-1001")

    assert result["success"] is False
    assert "Provide a status or priority" in result["error"]


def test_update_ticket_can_change_both_fields():
    result = update_ticket(
        "HD-1001",
        status="Resolved",
        priority="Low",
    )

    assert result["success"] is True
    assert result["status"] == "Resolved"
    assert result["priority"] == "Low"


def test_updated_ticket_can_be_retrieved():
    update_ticket("HD-1001", status="Resolved")

    retrieved = get_ticket_status("HD-1001")

    assert retrieved["success"] is True
    assert retrieved["status"] == "Resolved"
