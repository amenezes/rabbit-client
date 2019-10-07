from enum import Enum, unique


@unique
class EventQueries(Enum):
    OLDEST_EVENT = (
        "SELECT id, body, status FROM event as e WHERE "
        "e.status = false ORDER BY created_at LIMIT 1"
    )
    INSERT_EVENT = (
        "INSERT INTO event (body, status, created_at, created_by) "
        "VALUES (:body, :status, :created_at, :created_by)"
    )
    UPDATE_EVENT_STATUS = (
        "UPDATE event as e SET status = True WHERE e.id = :identity"
    )
