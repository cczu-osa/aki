import string
import random


def random_string(length: int,
                  chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.choices(chars, k=length))
