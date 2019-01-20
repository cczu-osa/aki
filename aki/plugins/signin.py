import random
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, Any

from nonebot import MessageSegment
from nonebot import on_command, CommandSession
from nonebot.helpers import context_id

__plugin_name__ = '签到'


def create_empty_item() -> Dict[str, Any]:
    return {
        'last_signin_date': None,  # 上次签到时间
        'signin_count': 0,  # 总签到次数
        'wealth': 0,  # 财富
    }


data = defaultdict(create_empty_item)

QQ_AVATAR_URL_FORMAT = 'https://q1.qlogo.cn/g?b=qq&nk={}&s=40'


@on_command(('signin', 'signin'), aliases=['签到', '打卡'], only_to_me=False)
async def sign_in(session: CommandSession):
    ctx_id = context_id(session.ctx, mode='user')
    my_data = data[ctx_id]

    today = date.today()
    if my_data['last_signin_date'] and \
            today - my_data['last_signin_date'] < timedelta(days=1):
        session.finish('你今天已经签过到啦\n明天再来吧～')

    my_data['last_signin_date'] = today
    my_data['signin_count'] += 1

    earned = random.randint(1, 100)
    data[ctx_id]['wealth'] += earned

    url = QQ_AVATAR_URL_FORMAT.format(session.ctx['user_id'])
    reply = str(MessageSegment.image(url))

    if session.ctx['message_type'] != 'private':
        reply += '\n' + str(MessageSegment.at(session.ctx['user_id']))

    reply += f'\n你已经累计签到了{my_data["signin_count"]}次\n' \
        f'本次签到获得了{earned}个金币～'
    session.finish(reply)


@on_command(('signin', 'wealth'), aliases=['我的财富', '我的金币', '小金库'])
async def my_wealth(session: CommandSession):
    ctx_id = context_id(session.ctx, mode='user')
    if data[ctx_id]['wealth'] == 0:
        await session.send('你还没有金币呢，快去签到吧')
    else:
        await session.send(f'你已经累积获得了{data[ctx_id]["wealth"]}个金币啦')
