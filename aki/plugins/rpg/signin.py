import random
from datetime import date, timedelta

from nonebot import CommandSession, MessageSegment

from . import cg
from . import da
from .helpers import inject_account


@cg.command('signin', aliases=['签到'], only_to_me=False)
@inject_account
async def _(session: CommandSession):
    account = session.state['account']

    today = date.today()
    if account.last_sign_in_date and \
            today - account.last_sign_in_date < timedelta(days=1):
        session.finish('你今天已经签过到啦\n明天再来吧～')

    last_sign_in_date = today
    total_sign_in = account.total_sign_in + 1
    earned = random.randint(1, 100)
    total_coins = account.total_coins + earned
    succeeded = await da.update(
        account,
        last_sign_in_date=last_sign_in_date,
        total_sign_in=total_sign_in,
        total_coins=total_coins,
    )
    if not succeeded:
        session.finish('签到失败，请稍后再试～')

    reply = str(MessageSegment.image(account.avatar_url))
    if session.ctx['message_type'] != 'private':
        reply += '\n' + str(MessageSegment.at(session.ctx['user_id']))

    reply += f'\n你已经累计签到了 {total_sign_in} 次\n' \
        f'本次签到获得了 {earned} 个金币～'
    session.finish(reply)
