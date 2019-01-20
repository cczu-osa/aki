from nonebot import on_command, CommandSession
import random
import time
from nonebot import MessageSegment
from collections import defaultdict
# from nonebot.helpers import context_id

def create_empty_item():
    return {
        'last_signed': None,  # 上次签到时间
        'total_coins': 0,  # 总的签到次数
        'wealth': 0,    # 财富
    }
data = defaultdict(create_empty_item)
times = {}

@on_command('签到', aliases=['打卡'])
async def sign_in(session: CommandSession):
    FORMAT_URL = 'https://q1.qlogo.cn/g?b=qq&nk='
    URL_END = '&s=40'
    user_id = session.ctx['user_id']
    rank = 0
    user_id = str(user_id)
    url = FORMAT_URL + user_id + URL_END
    nickname = session.ctx['sender']['nickname']
    now = time.localtime(time.time())
    now = int(now[3])


    if data[user_id]['total_coins'] == 0:

        data[user_id]['last_signed'] = now
        data[user_id]['total_coins'] += 1
        money = random.randint(1, 100)
        data[user_id]['wealth'] += money

    else:
        if data[user_id]['last_signed'] != now:
            data[user_id]['last_signed'] = now
            data[user_id]['total_coins'] += 1
            money = random.randint(1, 100)
            data[user_id]['wealth'] += money

        else:
            await session.send('今天你已经签过到啦\n明天再来吧~')
            return
    await session.send(MessageSegment.image(url)+'\n@'+nickname+'\n你已经签到了'+\
            str(data[user_id]['total_coins'])+'次了\n签到获得'+str(money)+'个金币啦')


@on_command('我的财富', aliases=['我的金币', '小金库'])
async def my_wealth(session: CommandSession):
    user_id = session.ctx['user_id']
    user_id = str(user_id)
    if data[user_id]['wealth'] == 0:
        await session.send('你还没有金币呢，快去签到吧')
    else:
        await session.send('你已经获得了'+str(data[user_id]['wealth'])+'个金币啦')