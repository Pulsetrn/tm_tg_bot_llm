from email_validator import validate_email
from aiogram import types


def email_validate_and_filter(msg: types.Message) -> dict[str, str] | None:
    try:
        email = validate_email(msg.text)
    except ValueError:
        return None

    return {"email": email.normalized}
