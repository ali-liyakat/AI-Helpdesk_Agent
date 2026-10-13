
# Fictional helpdesk tickets for development and testing.
TICKETS = {
    "HD-1001": {
        "title": "Unable to connect to office Wi-Fi",
        "status": "In Progress",
        "priority": "High",
        "assigned_to": "Alex Morgan",
    },
    "HD-1002": {
        "title": "Request access to the reporting dashboard",
        "status": "Open",
        "priority": "Medium",
        "assigned_to": "Jamie Lee",
    },
    "HD-1003": {
        "title": "Laptop running slowly",
        "status": "Resolved",
        "priority": "Low",
        "assigned_to": "Taylor Chen",
    },
}


def get_ticket_status(ticket_id: str) -> dict:
    """Return details for a fictional helpdesk ticket."""

    ticket = TICKETS.get(ticket_id.upper())

    if ticket is None:
        return {
            "success": False,
            "error": f"Ticket {ticket_id} was not found.",
        }

    return {
        "success": True,
        "ticket_id": ticket_id.upper(),
        **ticket,
    }


if __name__ == "__main__":
    result = get_ticket_status("HD-1001")
    print(result)
