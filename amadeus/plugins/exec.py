import asyncio
import pprint
from typing import Awaitable, Callable

import nonebot.permission as perm
from nonebot import on_command, CommandSession
from nonebot.message import unescape


@on_command('exec', permission=perm.SUPERUSER)
async def _(session: CommandSession):
    code = unescape(session.current_arg)

    try:
        tmp_locals = {}
        exec(code, None, tmp_locals)
        await session.send(f'Locals:\n{pprint.pformat(tmp_locals, indent=2)}')

        if isinstance(tmp_locals.get('run'), Callable):
            res = tmp_locals['run'](session.bot, session.ctx)
            if isinstance(res, Awaitable):
                res = await asyncio.wait_for(res, 6)
            await session.send(f'执行成功\n'
                               f'返回：\n{pprint.pformat(res, indent=2)}')
    except Exception as e:
        await session.send(f'执行失败\n异常：\n{pprint.pformat(e, indent=2)}')
        return
