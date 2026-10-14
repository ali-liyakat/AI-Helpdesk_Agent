
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



def create_ticket(title: str, priority: str = "Medium") -> dict:
    """Create a fictional helpdesk ticket in memory."""

    # Validate the ticket title.
    title = title.strip()

    if not title:
        return {
            "success": False,
            "error": "Ticket title cannot be empty.",
        }

    # Validate priority.
    priority = priority.strip().capitalize()

    if priority not in {"Low", "Medium", "High"}:
        return {
            "success": False,
            "error": "Priority must be Low, Medium, or High.",
        }

    # Generate the next ticket ID.
    ticket_number = max(
        int(ticket_id.split("-")[1])
        for ticket_id in TICKETS
    ) + 1

    ticket_id = f"HD-{ticket_number}"

    # Save the new ticket.
    TICKETS[ticket_id] = {
        "title": title,
        "status": "Open",
        "priority": priority,
        "assigned_to": "Unassigned",
    }

    return {
        "success": True,
        "ticket_id": ticket_id,
        **TICKETS[ticket_id],
    }


def list_tickets(status: str | None = None) -> dict:
    """List fictional helpdesk tickets, optionally filtered by status."""

    valid_statuses = {"Open", "In Progress", "Resolved"}

    if status is not None:
        status = status.strip().title()

        if status not in valid_statuses:
            return {
                "success": False,
                "error": (
                    "Status must be Open, In Progress, or Resolved."
                ),
            }

    tickets = []

    for ticket_id, ticket in TICKETS.items():
        if status is None or ticket["status"] == status:
            tickets.append({
                "ticket_id": ticket_id,
                **ticket,
            })

    return {
        "success": True,
        "count": len(tickets),
        "tickets": tickets,
    }


def update_ticket(
    ticket_id: str,
    status: str | None = None,
    priority: str | None = None,
) -> dict:
    """Update the status or priority of a fictional helpdesk ticket."""

    ticket_id = ticket_id.strip().upper()
    ticket = TICKETS.get(ticket_id)

    if ticket is None:
        return {
            "success": False,
            "error": f"Ticket {ticket_id} was not found.",
        }

    if status is None and priority is None:
        return {
            "success": False,
            "error": "Provide a status or priority to update.",
        }

    valid_statuses = {"Open", "In Progress", "Resolved"}
    valid_priorities = {"Low", "Medium", "High"}

    if status is not None:
        status = status.strip().title()
        if status not in valid_statuses:
            return {
                "success": False,
                "error": "Status must be Open, In Progress, or Resolved.",
            }

    if priority is not None:
        priority = priority.strip().capitalize()
        if priority not in valid_priorities:
            return {
                "success": False,
                "error": "Priority must be Low, Medium, or High.",
            }

    if status is not None:
        ticket["status"] = status

    if priority is not None:
        ticket["priority"] = priority

    return {
        "success": True,
        "ticket_id": ticket_id,
        **ticket,
    }


if __name__ == "__main__":
    result = get_ticket_status("HD-1001")
    print(result)
