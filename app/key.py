from secrets import token_bytes


def _key(filename: str, length: int) -> bytes:
    try:
        with open(filename, mode="rb") as reader:
            key = reader.read()

        if len(key) != length:
            raise ValueError
    except (FileNotFoundError, ValueError):
        key = token_bytes(length)
        with open(filename, mode="wb") as writer:
            writer.write(key)

    return key


def secret_key() -> bytes:
    return _key(
        filename=".SECRET_KEY",
        length=32
    )
