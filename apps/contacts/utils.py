import re


def normalize_phone(raw):
    """
    Normalize a Tanzanian phone number to the 255XXXXXXXXX format.
    Accepts formats like 0712345678, +255712345678, 255712345678, 712345678.
    Returns None if the number cannot be normalized to a valid TZ number.
    """
    if not raw:
        return None
    digits = re.sub(r'\D', '', raw)

    if digits.startswith('255') and len(digits) == 12:
        national = digits[3:]
    elif digits.startswith('0') and len(digits) == 10:
        national = digits[1:]
    elif len(digits) == 9:
        national = digits
    else:
        return None

    if not re.match(r'^[67]\d{8}$', national):
        return None

    return f'255{national}'
