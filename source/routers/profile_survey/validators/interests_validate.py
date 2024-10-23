import re


def check_comma_separated_text(text: str) -> bool:
    pattern = r"^[^,]+(,[^,]+)*$"
    return bool(re.match(pattern, text.strip()))
