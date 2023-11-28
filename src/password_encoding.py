from typing import Iterable, List
from cryptography.fernet import Fernet


def generate_key() -> bytes:
    """Generates a key for Fernet encryption

    :return: The generated key
    :rtype: bytes
    """
    return Fernet.generate_key()


def encode_password(password: str, key: bytes) -> str:
    """Encoded password for a given key

    :param password: a password to be encoded
    :type password: str
    :param key: a key for the current encryption
    :type key: bytes
    :return: The encoded password
    :rtype: str
    """
    f = Fernet(key)
    return f.encrypt(bytes(password, "utf-8")).decode("utf-8")


def decode_password(encoded_password: str, key: bytes) -> str:
    """Decodes given password for a given key

    :param encoded_password: an encoded password
    :type encoded_password: str
    :param key: a key for the current encryption
    :type key: bytes
    :return: decoded password
    :rtype: str
    """
    f = Fernet(key)
    return f.decrypt(encoded_password).decode("utf-8")


def encode_all(passwords: Iterable[str], key: bytes) -> List[str]:
    """Encodes a set of passwords for a given key

    :param passwords: passwords to be encoded
    :type passwords: Iterable[str]
    :param key: key to be used in encoding
    :type key: bytes
    :return: list of encoded passwords
    :rtype: List[str]
    """
    result = []
    f = Fernet(key)
    for password in passwords:
        result.append(f.encrypt(bytes(password, "utf-8")).decode("utf-8"))
    return result


def decode_all(encoded_passwords: Iterable[str], key: bytes) -> List[str]:
    """Decodes a set of encoded passwords for a given key

    :param encoded_passwords: a list of encoded passwords
    :type encoded_passwords: Iterable[str]
    :param key: a key for decoding
    :type key: bytes
    :return: list of decoded passwords
    :rtype: List[str]
    """
    result = []
    f = Fernet(key)
    for password in encoded_passwords:
        result.append(f.decrypt(password).decode("utf-8"))
    return result


if __name__ == "__main__":
    _k = generate_key()
    print(encode_password('XD', _k))
