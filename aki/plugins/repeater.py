import random
from dataclasses import dataclass
from typing import Dict

import nonebot.permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.helpers import context_id

__plugin_name__ = '复读机'


@dataclass
class Record:
    last_msg: str
    last_user_id: int
    repeat_count: int = 0


records: Dict[str, Record] = {}


@on_natural_language(only_to_me=False, permission=perm.GROUP)
async def _(session: NLPSession):
    group_ctx_id = context_id(session.ctx, mode='group')
    user_id = session.ctx['user_id']
    msg = session.msg

    record = records.get(group_ctx_id)
    if record is None:
        record = Record(msg, user_id, repeat_count=1)
        records[group_ctx_id] = record
        return

    if record.last_msg != msg or record.last_user_id == user_id:
        return

    record.last_user_id = user_id
    record.repeat_count += 1
    if record.repeat_count == 3:
        return IntentCommand(
            random.randint(0, 1) * 90.0,
            'delayed_echo',
            args={'delay': random.randint(5, 20) / 10, 'message': msg}
        )
