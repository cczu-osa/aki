from typing import Optional
import re

from nonebot import MessageSegment
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult

from aki.aio import requests
from aki.cache import cached

__plugin_name__ = '点歌'

QQ_MUSIC_SEARCH_URL_FORMAT = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?g_tk=5381&p=1&n=20&w={}&format=json&loginUin=0&hostUin=0&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&remoteplace=txt.yqq.song&t=0&aggr=1&cr=1&catZhida=1&flag_qc=0'


@cached(ttl=12 * 60 * 60)
async def search_song_id(keyword: str) -> Optional[int]:
    keyword = keyword.strip()
    if not keyword:
        return None
    resp = await requests.get(QQ_MUSIC_SEARCH_URL_FORMAT.format(keyword))
    payload = await resp.json()
    if not isinstance(payload, dict) or \
            payload.get('code') != 0 or \
            not payload.get('data'):
        return None

    try:
        return payload['data']['song']['list'][0]['songid']
    except (TypeError, KeyError, IndexError):
        return None


@on_command('music', aliases=['点歌', '音乐'], only_to_me=False)
async def music(session: CommandSession):
    keyword = session.get('keyword', prompt='你想点什么歌呢？')
    song_id = await search_song_id(keyword)
    if song_id is None:
        session.finish('没有找到这首歌呢')
    session.finish(MessageSegment.music('qq', song_id))


@music.args_parser
async def _(session: CommandSession):
    stripped_text = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_text:
            session.args['keyword'] = stripped_text
        return

    if not stripped_text:
        session.pause('请发送有效内容哦～')

    session.args[session.current_key] = stripped_text


CALLING_KEYWORDS = {'来一首', '点一首', '整一首', '播放', '点歌'}


@on_natural_language(keywords=CALLING_KEYWORDS)
async def _(session: NLPSession):
    sp = re.split('|'.join(CALLING_KEYWORDS), session.msg_text, maxsplit=1)
    if sp:
        print(sp[-1].strip(' 吧呗'))
        return NLPResult(90.0, 'music', {'keyword': sp[-1].strip(' 吧呗')})
