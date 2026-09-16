import pytest
from app.tools.send_email import SendEmailInput, send_email

def test_sends_mock_email():
    result = send_email(SendEmailInput(to="test@example.com", subject="Hi", body="Hello"))
    assert result.status == "mocked"
    assert result.to == "test@example.com"

def test_rejects_empty_subject():
    with pytest.raises(ValueError):
        send_email(SendEmailInput(to="test@example.com", subject="  ", body="Hello"))

def test_rejects_empty_body():
    with pytest.raises(ValueError):
        send_email(SendEmailInput(to="test@example.com", subject="Hi", body="  "))

def test_rejects_invalid_email():
    with pytest.raises(Exception):
        send_email(SendEmailInput(to="not-an-email", subject="Hi", body="Hello"))