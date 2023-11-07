from pathlib import Path
import pytest

from src.face_rec_easier import encode_known, _get_face, new_face, _recognize, validate_face, recognize_gui


def test_encode_exists():
    encode_known()
    assert (Path(__file__).parent.parent / 'data' / 'encoding.pkl').exists()


def test_encode_adds():
    ...


def test_get_face_not_null():
    ...


def test_get_face_not_dark():
    ...


def test_new_face_reads():
    ...
