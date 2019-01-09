from typing import Optional, List, Dict, Any

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult

from amadeus.aio import requests
from amadeus.cache import cached

__plugin_name__ = '知乎'

DAILY_LATEST_API_URL = 'https://news-at.zhihu.com/api/4/news/latest'
DAILY_STORY_URL = 'https://daily.zhihu.com/story/{id}'


@cached(ttl=5 * 60)
async def get_latest_news() -> Optional[List[Dict[str, Any]]]:
    resp = await requests.get(DAILY_LATEST_API_URL, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    })
    payload = await resp.json()
    if not isinstance(payload, dict) or 'stories' not in payload:
        return None
    return payload.get('stories') or []


@on_command(('zhihu', 'daily'), aliases=['知乎日报'])
async def _(session: CommandSession):
    stories = await get_latest_news()
    if stories is None:
        session.finish('查询失败了……')
    elif not stories:
        session.finish('暂时还没有内容哦')

    reply = ('最新的知乎日报内容如下：\n\n' +
             '\n\n'.join(f'{story["title"]}\n'
                         f'{DAILY_STORY_URL.format(id=story["id"])}'
                         for story in stories))
    session.finish(reply)


@on_natural_language({'知乎日报'})
async def _(session: NLPSession):
    return NLPResult(80.0, ('zhihu', 'daily'))
