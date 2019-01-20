from nonebot import on_command, CommandSession
import random
from datetime import *
from nonebot import MessageSegment
num = {
    'ccl': 1,       # 储存用户打卡次数
       }
money = {}          # 用户金币数量
user_value = {}     # 用户今日是否打卡
t = {}              # 日期
number = {'rank': 0}    # 排名
@on_command('签到', aliases=['打卡'])
async def sign_in(session: CommandSession):
    FORMAT_URL = 'https://q1.qlogo.cn/g?b=qq&nk='
    URL_END = '&s=40'
    value = 0
    user_name = session.ctx['user_id']

    user_name = str(user_name)
    url = FORMAT_URL+user_name+URL_END
    nickname = session.ctx['sender']['nickname']
    t = date.today()

    for key in num:
        if not key == user_name:
            value = 0
        else:
            value = 1
    if value == 0:
        mone = random.randint(1, 100)
        user_value[user_name] = 1
        num[user_name] = 1
        money[user_name] = mone
        number['rank'] += 1
    elif value == 1:
        if user_value[user_name] == 1:
            await session.send('你已经签到过啦~\n明天再来吧')
            return
        else:
            mone = random.randint(1, 100)
            num[user_name] += 1
            money[user_name] += mone
            user_value[user_name] = 1
            number['rank'] += 1
    if t != date.today():
        number['rank'] = 0
        for key in user_value:
            user_value[key] = 0

    await session.send(MessageSegment.image(url)+'\n@'+nickname+'\n你是本群第'+str(number['rank'])+'位签到成功'+'\n你已经签到了'\
            +str(num[user_name])+'次了\n签到获得'+str(+mone)+'个金币啦')


@on_command('查询金币数量', aliases=['我的财富'])
async def my_money(session: CommandSession):
    vaule = 0
    user_name = session.ctx['user_id']
    user_name = str(user_name)
    for key in money:
        if not key == user_name:
            vaule = 0
        else:
            vaule = 1
    if vaule == 1:
        await session.send('你已经获得了'+str(money[user_name])+'个金币啦')
    elif vaule == 0:
        await session.send('你暂时还没有获得金币呢')