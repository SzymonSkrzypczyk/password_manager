import pytest
# from typing import List

from src.password_encoding import generate_key, encode_password, decode_password, encode_all, decode_all


@pytest.fixture()
def test_password():
    key = generate_key()
    return encode_password("TEST", key), key


@pytest.fixture()
def encoded_password():
    key = generate_key()
    return encode_password("TEST", key), key


def test_generate_key_type():
    assert type(generate_key()) == bytes


def test_generate_key_return_not_none():
    assert generate_key() is not None


def test_encode_password_type(test_password):
    # klucz mozna zmienic na fixture
    print(*test_password)
    assert type(encode_password(*test_password)) == str


'''@pytest.raises(ValueError)
def test_encode_password_wrong_key():
    ...
'''


def test_encode_return_not_none(test_password):
    assert encode_password(*test_password) is not None


def test_decode_password_type(test_password):
    # fixtures!!!
    assert type(decode_password(*test_password)) == str


def test_decode_password_return_not_none(test_password):
    assert decode_password(*test_password) is not None


def test_encode_all_return_empty(test_password):
    assert not encode_all([], test_password[1])


def test_encode_all_type(test_password):
    assert type(encode_all(["TEST"], test_password[1])) == list


def test_decode_all_type(encoded_password):
    assert type(decode_all([encoded_password[0]], encoded_password[1])) == list


def test_decode_all_return_empty(encoded_password):
    assert not decode_all([], encoded_password[1])
