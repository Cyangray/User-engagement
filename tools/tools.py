from uuid import uuid4


def short_uuid4_generator(bits: int = 30) -> int:
    return uuid4().int >> (128 - bits)
