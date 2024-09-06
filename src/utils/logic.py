import uuid


def equal_uuids(uuid1: uuid.UUID | str, uuid2: uuid.UUID | str) -> bool:
    return str(uuid1) == str(uuid2)
