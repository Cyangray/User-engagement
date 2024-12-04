from uuid import uuid4

CURRENT_ID = 0


def short_uuid4_generator(bits: int = 30) -> int:
    """
    Small function generating UUID4 short enough to be saved in the SQL database.
    """
    return uuid4().int >> (128 - bits)


def long_uuid4_generator():
    return uuid4()
