import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from aiocache import cached
from nonebot import CommandSession

from aki.aio import requests
from . import cg

API_URL = 'http://bangumi.bilibili.com/web_api/timeline_v4'


@cached(ttl=5 * 60)
async def get_timeline_list() -> Optional[List[Dict[str, Any]]]:
    resp = await requests.get(API_URL)
    payload = await resp.json()
    if not isinstance(payload, dict) or payload.get('code') != 0:
        return None
    return payload['result'] or []


@cg.command('timeline', aliases={'番剧时间表', '新番时间表'}, only_to_me=False)
async def index(session: CommandSession):
    timeline_list = await get_timeline_list()
    if timeline_list is None:
        session.finish('查询失败了……')

    date = session.state.get('date')
    name = session.state.get('name')

    if date:
        timeline_list = filter(lambda x: x.get('pub_date', '').endswith(date),
                               timeline_list)
    if name:
        name = name.strip()
        timeline_list = list(filter(
            lambda x: name.lower() in x.get('title', '').lower(),
            timeline_list
        ))
        if len(set(map(lambda x: x['title'], timeline_list))) > 1:
            timeline_list = filter(
                lambda x: len(name) > len(x['title']) / 4,
                timeline_list
            )

    if not isinstance(timeline_list, list):
        timeline_list = list(timeline_list)

    if date and name:
        if not timeline_list:
            reply = '没更新'
        else:
            reply = '\n'.join(
                ('更新了' if item['is_published']
                 else f'将在{item["ontime"]}更新') +
                (f'第{item["ep_index"]}话' if item['ep_index'].isdigit()
                 else item['ep_index'])
                for item in timeline_list
            )
        session.finish(reply)

    if not timeline_list:
        session.finish('没有找到符合条件的时间表……')

    if date:
        month, day = [int(x) for x in date.split('-')]
        reply = f'在{month}月{day}日更新的番剧有：\n\n'
        reply += '\n'.join(f'{item["title"] or "未知动画"}  '
                           f'{item["ontime"] or "未知时间"}  ' +
                           (f'第{item["ep_index"]}话'
                            if item['ep_index'].isdigit()
                            else item['ep_index'])
                           for item in timeline_list)
        session.finish(reply)

    if name:
        anime_dict = defaultdict(list)
        for item in timeline_list:
            anime_dict[item['title']].append(item)

        for name, items in anime_dict.items():
            reply = f'{name}\n'
            for item in items:
                _, month, day = [int(x) for x in item['pub_date'].split('-')]
                reply += '\n' + ('已' if item['is_published'] else '将') + \
                         f'在{month}月{day}日{item["ontime"]}更新' + \
                         (f'第{item["ep_index"]}话'
                          if item['ep_index'].isdigit()
                          else item['ep_index'])
            await session.send(reply)


@index.args_parser
async def _(session: CommandSession):
    if session.state:
        return

    m = re.search(r'(?:(-?\d{1,2})(?:-(\d{1,2}))?)?\s*(.+)?',
                  session.current_arg_text.strip())
    if not m:
        session.finish(USAGE)

    num1 = m.group(1)
    num2 = m.group(2)
    name = m.group(3)

    if num1 is None and name is None:
        session.finish(USAGE)

    if num1 is not None and num2 is not None:
        date = f'%02d-%02d' % (int(num1), int(num2))
    elif num1 is not None:
        date = (datetime.now() + timedelta(days=int(num1))).strftime('%m-%d')
    else:
        date = None

    session.state['date'] = date
    session.state['name'] = name


USAGE = r"""
你可以这样使用这个命令（括号内为说明，不用发）：

新番时间表 12-25（查看12月25日更新的番剧）
新番时间表 0（查看今天更新的番剧，1表示明天，2表示后天，-1表示昨天）
新番时间表 刀剑神域（查看刀剑神域今天是否更新）
新番时间表 12-25 刀剑神域（查看刀剑神域12月25日是否更新）
""".strip()
