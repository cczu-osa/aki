import random
from collections import Counter

import none.permission as perm
from none import on_natural_language, NLPSession, NLPResult
from none.helpers import context_id

counter = Counter()
last_msgs = {}


@on_natural_language(only_to_me=False, permission=perm.GROUP)
async def _(session: NLPSession):
    ctx_id = context_id(session.ctx, mode='group')

    if last_msgs.get(ctx_id) != session.msg:
        counter[ctx_id] = 0
        last_msgs[ctx_id] = session.msg
    counter[ctx_id] += 1

    if counter[ctx_id] == 3:
        return NLPResult(90.0, ('delayed_echo',), {
            'delay': random.randint(5, 20) / 10,
            'message': session.msg
        })
