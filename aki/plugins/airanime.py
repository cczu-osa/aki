from nonebot import on_command, CommandSession

from aki.aio import requests

__plugin_name__ = 'airAnime'

ANIME_SEARCH_API_FORMAT = 'http://airanime.applinzi.com/function/sonline.php?kt={}'

SITES = [
    ('bilibili', '哔哩哔哩'),
    ('dilidili', '嘀哩嘀哩'),
    ('anime1', 'Anime1'),
    ('calibur', 'Calibur'),
    ('qinmei', 'Qinmei'),
    ('iqiyi', '爱奇艺'),
    ('tencenttv', '腾讯视频'),
    ('fcdm', '风车动漫'),
    ('youku', '优酷'),
    # ('pptv', 'PPTV'),
    ('letv', '乐视'),
]


@on_command('airanime',
            aliases=['搜动漫', '搜索动漫', '动漫资源', '动漫搜索',
                     '搜番剧', '搜索番剧', '番剧资源', '番剧搜索'])
async def _(session: CommandSession):
    keyword = session.state.get('keyword') or session.current_arg
    keyword = keyword.strip()
    if not keyword:
        session.finish('关键词不能为空哦～')

    await session.send('奶茶卖力搜索中……')
    url = ANIME_SEARCH_API_FORMAT.format(keyword.strip())
    resp = await requests.get(url)
    if not resp.ok:
        session.finish('搜索失败了，请稍后再试吧')

    results = await resp.json()

    reply = ''
    for key, site_name in SITES:
        titles, links, count = results[key]
        if count == 0:
            continue

        reply += f'\n\n[[{site_name}]]\n\n' + '\n'.join(
            [f'{title}\n{link}' for title, link in zip(titles, links)]
        )

    reply = reply.strip()
    if not reply:
        session.finish('没有搜到你要的番剧哦')

    session.finish(f'{reply}\n\n'
                   f'数据来源：airAnime http://airanime.applinzi.com/')
