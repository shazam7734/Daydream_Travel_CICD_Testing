# tests/unit/test_utils.py

import re

def is_valid_email(email):
    """Basic email validation."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def check_password_strength(password):
    """
    A password is considered strong if it has at least:
    - 8 characters
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 number
    - 1 special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def test_is_valid_email():
    assert is_valid_email("user@example.com")
    assert not is_valid_email("userexample.com")
    assert not is_valid_email("user@.com")
    assert not is_valid_email("user@com")
    assert is_valid_email("u.ser+tag@domain.co.uk")


def test_check_password_strength():
    assert check_password_strength("Strong123!") is True
    assert check_password_strength("weak") is False
    assert check_password_strength("NoSpecial123") is False
    assert check_password_strength("nouppercase123!") is False
    assert check_password_strength("NOLOWERCASE123!") is False
    assert check_password_strength("NoDigits!!") is False
