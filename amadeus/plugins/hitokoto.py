from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult

from amadeus.aio import requests

__plugin_name__ = '一言'

API_URL = 'https://v1.hitokoto.cn?encode=text'


@on_command('hitokoto', aliases=['一言'])
async def _(session: CommandSession):
    resp = await requests.get(API_URL)
    if not resp.ok:
        session.finish('获取一言失败，请稍后再试哦')
    session.finish(await resp.text)


@on_natural_language({'一言', '骚话'})
async def _(session: NLPSession):
    non_keywords = {'君子一言', '一言不合', '一言不发', '一言为定'}
    if any(map(lambda kw: kw in session.msg_text, non_keywords)):
        return
    return NLPResult(80.0, ('hitokoto',))
