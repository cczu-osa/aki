from typing import Callable

from nonebot import CommandSession

from . import da


def inject_account(func: Callable) -> Callable:
    async def wrapper(session: CommandSession):
        account = await da.get_or_create_account(session.ctx)
        if account is None:
            session.finish('账户数据访问失败，请稍后重试～')
        session.state['account'] = account
        return await func(session)

    return wrapper
