import re
from django.core.exceptions import ValidationError



def normalize_phone(phone):

    if phone is None:
        return None
    
    phone = re.sub(r'\D', '', str(phone))

    if len(phone) != 11:
        raise ValidationError("Phone number must have exactly 11 digits")

    return phone

