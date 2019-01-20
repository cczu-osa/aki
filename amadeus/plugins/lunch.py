from nonebot import on_command, CommandSession
import asyncio
import random


@on_command('lunch', aliases=['今天吃啥', '吃啥啊', '吃什么呢', '吃啥', '饭'])
async def lunch(session: CommandSession):
    prb = ['当真', '必须的', '嗯', '那是', '好', '当然', '可以', '行', '对', '不懂', '不知道', '你说呢', 'yeah']
    kind = ['面条', '饭', '炒饭', '早点', '砂锅']
    where = ['一食堂', '二食堂', '日夜食堂', '点外卖']

    wait = ['等会儿，让奶茶先想想去哪儿吃', '等等啊，容奶茶思考片刻，去哪儿呢🙄']
    fail = ['那好吧，小主你终究不爱奶茶😭', '😔哎，小主你还是信不过我', '唔，你竟然不要奶茶了😭']
    requ = ['需要我帮你决定吃点什么吗', '你知道要吃点什么吗']
    yea = ['可否', '可还行', '怎样']
    pic = ['🥙 🌮 🌯 🥗 🥘', '🍤 🍙 🍚 🍘 🍥', '🍰 🎂 🍮 🍭 🍬', ' 🍇 🍗 🍖 🌭 🍔 ', '🥂 🍷 🥃 🍸 🍹']

    next1 = session.get_optional('next1')
    next2 = session.get_optional('next2')

    if next1 is None:
        await session.send(random.choice(wait))
        await asyncio.sleep(3)
        chance = random.choice(where)
        await session.send('ののの,那就去' + chance + '吧')
        await asyncio.sleep(2)
        next1 = session.get('next1', prompt=random.choice(yea))

    elif next1 in prb and next2 is None:
        next2 = session.get('next2', prompt=random.choice(requ))

    elif next2 in prb:
        await session.send('经奶茶精选，' + random.choice(kind) + '与你更配哦🤔')
        await asyncio.sleep(1)
        await session.send(random.choice(pic))

    elif next1 in ['算了']:
        await session.send(random.choice(fail))

    elif next2 in ['算了']:
        await session.send(random.choice(fail))


@lunch.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return

    session.args[session.current_key] = session.current_arg_text
