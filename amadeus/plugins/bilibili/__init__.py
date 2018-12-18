import math
import re

from none import CommandGroup, CommandSession

from amadeus import dt
from amadeus.aio import requests

bilibili_anime = CommandGroup('bilibili_anime')

INDEX_API_URL = 'https://bangumi.bilibili.com/media/web_api/search/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month={month}&pub_date={year}&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=20'
INDEX_WEB_URL = 'https://www.bilibili.com/anime/index/#season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month={month}&pub_date={year}&style_id=-1&order=3&st=1&sort=0&page=1'


@bilibili_anime.command('index', aliases={'番剧索引', '番剧', '新番'})
async def index(session: CommandSession):
    now = dt.beijing_now()
    year = session.get_optional('year', now.year)
    month = session.get_optional('month', math.ceil(now.month / 3) * 3 - 3 + 1)

    api_url = INDEX_API_URL.format(year=year, month=month)
    resp = await requests.get(api_url)
    payload = await resp.json()
    if not payload or payload.get('code') != 0:
        await session.send('查询失败了……')
        return

    anime_list = payload['result']['data']
    if not anime_list:
        await session.send('没有查询到相关番剧……')
        return

    reply = f'{year}年{month}月番剧\n按追番人数排序，前20部如下：\n\n'
    for anime in anime_list:
        title = anime.get('title')
        index_show = anime.get('index_show', '不详')
        if not title:
            continue

        reply += f'{title}  {index_show}\n'

    web_url = INDEX_WEB_URL.format(year=year, month=month)
    reply += f'\n更多详细资料见BiliBili官网 {web_url}'

    await session.send(reply)


@index.args_parser
async def _(session: CommandSession):
    argv = session.current_arg_text.split()

    year = None
    month = None
    if len(argv) == 2 and \
            re.fullmatch(r'(?:20)?\d{2}', argv[0]) and \
            re.fullmatch(r'\d{1,2}', argv[1]):
        year = int(argv[0]) if len(argv[0]) > 2 else 2000 + int(argv[0])
        month = int(argv[1])
    elif len(argv) == 1 and re.fullmatch(r'\d{1,2}', argv[0]):
        month = int(argv[0])
    elif len(argv) == 1 and re.fullmatch(r'(?:20)?\d{2}-\d{1,2}', argv[0]):
        year, month = [int(x) for x in argv[0].split('-')]
        year = 2000 + year if year < 100 else year
    elif len(argv):
        await session.send('抱歉无法识别输入的参数，下面将给出本季度的番剧～')

    if year is not None:
        session.args['year'] = year
    if month is not None:
        session.args['month'] = month
