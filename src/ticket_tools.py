
"""SQLite-backed tools for the fictional helpdesk."""

from database import (
    DATABASE_PATH,
    get_connection,
    initialize_database,
    seed_initial_tickets,
)

# Ensure a fresh checkout can initialize its database automatically.
initialize_database()
seed_initial_tickets()


def get_ticket_status(ticket_id: str) -> dict:
    """Return details for a helpdesk ticket."""

    ticket_id = ticket_id.strip().upper()

    with get_connection(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT ticket_id, title, status, priority, assigned_to
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

    if row is None:
        return {
            "success": False,
            "error": f"Ticket {ticket_id} was not found.",
        }

    return {
        "success": True,
        **dict(row),
    }


def create_ticket(title: str, priority: str = "Medium") -> dict:
    """Create and persist a helpdesk ticket."""

    title = title.strip()

    if not title:
        return {
            "success": False,
            "error": "Ticket title cannot be empty.",
        }

    priority = priority.strip().capitalize()

    if priority not in {"Low", "Medium", "High"}:
        return {
            "success": False,
            "error": "Priority must be Low, Medium, or High.",
        }

    with get_connection(DATABASE_PATH) as connection:
        # Lock the database for this transaction while generating an ID.
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute(
            """
            SELECT MAX(CAST(SUBSTR(ticket_id, 4) AS INTEGER))
            FROM tickets
            WHERE ticket_id GLOB 'HD-[0-9]*'
            """
        ).fetchone()

        next_number = (row[0] or 1000) + 1
        ticket_id = f"HD-{next_number}"

        connection.execute(
            """
            INSERT INTO tickets
                (ticket_id, title, status, priority, assigned_to)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticket_id, title, "Open", priority, "Unassigned"),
        )

        ticket = connection.execute(
            """
            SELECT ticket_id, title, status, priority, assigned_to
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

    return {
        "success": True,
        **dict(ticket),
    }


def list_tickets(status: str | None = None) -> dict:
    """List tickets, optionally filtering by status."""

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

    query = """
        SELECT ticket_id, title, status, priority, assigned_to
        FROM tickets
    """
    parameters = ()

    if status is not None:
        query += " WHERE status = ?"
        parameters = (status,)

    query += " ORDER BY CAST(SUBSTR(ticket_id, 4) AS INTEGER)"

    with get_connection(DATABASE_PATH) as connection:
        rows = connection.execute(query, parameters).fetchall()

    tickets = [dict(row) for row in rows]

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
    """Update and persist a ticket's status or priority."""

    ticket_id = ticket_id.strip().upper()

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

    with get_connection(DATABASE_PATH) as connection:
        existing = connection.execute(
            "SELECT 1 FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

        if existing is None:
            return {
                "success": False,
                "error": f"Ticket {ticket_id} was not found.",
            }

        if status is not None:
            connection.execute(
                "UPDATE tickets SET status = ? WHERE ticket_id = ?",
                (status, ticket_id),
            )

        if priority is not None:
            connection.execute(
                "UPDATE tickets SET priority = ? WHERE ticket_id = ?",
                (priority, ticket_id),
            )

    return get_ticket_status(ticket_id)


if __name__ == "__main__":
    print(get_ticket_status("HD-1001"))
    print(list_tickets())
