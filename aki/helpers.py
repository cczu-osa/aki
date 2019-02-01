import functools
import random
import string

from nonebot import context_id


def random_string(length: int,
                  chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.choices(chars, k=length))


ctx_id_by_user = functools.partial(context_id, mode='user')
