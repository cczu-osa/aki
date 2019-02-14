from nonebot import CommandSession, MessageSegment
from nonebot.typing import Context_T

from . import cg
from .helpers import inject_account
from .models import Account


@cg.command('account', aliases=['我的账号', '我的账户', '小金库', '我的财富'],
            only_to_me=False)
@inject_account
async def _(session: CommandSession):
    account = session.state['account']
    session.finish(format_account(session.ctx, account))


def format_account(ctx: Context_T, account: Account) -> str:
    return (MessageSegment.image(account.avatar_url) +
            f'\n'
            f'昵称：{ctx["sender"]["nickname"]}\n'
            f'小金库：{account.total_coins} 金币\n'
            f'累计签到：{account.total_sign_in} 次')
