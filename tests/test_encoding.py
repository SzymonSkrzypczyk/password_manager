import pytest
# from typing import List

from src.password_encoding import generate_key, encode_password, decode_password, encode_all, decode_all

# in next commit add fixtures
TEST_PASSWORD = "TEST"
key = None
encoded_password = None


def setup_module(_module):
    global key, encoded_password
    key = generate_key()
    encoded_password = encode_password(TEST_PASSWORD, key)


def test_generate_key_type():
    assert type(generate_key()) == bytes


def test_generate_key_return_not_none():
    assert generate_key() is not None


def test_encode_password_not_none():
    assert encoded_password is not None


def test_encode_password_type():
    assert type(encoded_password) == str


def test_decode_password_not_none():
    decoded_password = decode_password(encoded_password, key)
    assert decoded_password is not None
    assert decoded_password == TEST_PASSWORD


def test_decode_password_type():
    decoded_password = decode_password(encoded_password, key)
    assert type(decoded_password) == str


def test_encode_all_passwords_not_none():
    assert encode_all([encoded_password], key) is not None


def test_encode_all_passwords_type():
    assert type(encode_all([TEST_PASSWORD], key)) == list


def test_decode_all_passwords_not_null():
    decoded = decode_all([encoded_password], key)
    assert decoded is not None
    assert decoded[0] == TEST_PASSWORD


def test_decode_all_passwords_type():
    assert type(decode_all([encoded_password], key)) == list


def teardown_module(_module):
    global key, encoded_password
    key = None
    encoded_password = None
