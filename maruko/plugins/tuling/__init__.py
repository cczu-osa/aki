import asyncio
import math
import json
import hashlib
from typing import List, Optional, Union

import aiohttp
from aiocqhttp.message import Message, escape
from none import on_command, CommandSession
from none import on_natural_language, NLPSession, NLPResult
from none import get_bot
from none.helpers import context_id

from maruko import baidu_aip

bot_ = get_bot()


# TODO: 处理一次性图灵调用之后可能需要交互的情况


@on_command('tuling', aliases=('聊天', '对话'))
async def tuling(session: CommandSession):
    message = session.get('message', prompt='我已经准备好啦，来跟我聊天吧~')

    tmp_msg = Message(message)
    text = tmp_msg.extract_plain_text()
    images = [s.data['url'] for s in tmp_msg
              if s.type == 'image' and 'url' in s.data]

    # call tuling api
    replies = await call_tuling123_api(context_id(session.ctx),
                                       text, images)

    if replies:
        for reply in replies:
            await session.send(escape(reply))
            await asyncio.sleep(0.8)
    else:
        await session.send('看不懂你在说什么呢')

    one_time = session.get_optional('one_time', False)
    if one_time:
        return
    else:
        session.pause()


@tuling.args_parser
async def _(session: CommandSession):
    if session.current_key == 'message':
        if session.current_arg_text.strip() in ('结束', '拜拜', '再见'):
            session.finish('拜拜啦，你忙吧，下次想聊天随时找我哦~')
            return
        session.args[session.current_key] = session.current_arg


@on_natural_language
async def _(session: NLPSession):
    return NLPResult(60.0, 'tuling', {
        'message': session.msg,
        'one_time': True
    })


@on_natural_language(keywords={'聊', '说话'})
async def _(session: NLPSession):
    text = session.msg_text.strip()
    confidence = 0.0
    match = len(text) <= 4 and '陪聊' in text
    if match:
        confidence = 100.0
    else:
        score = await baidu_aip.text_similarity('来陪我聊天', text)
        if score > 0.70:
            match = True
            confidence = math.ceil(score * 10) * 10  # 0.74 -> 80.0

    if match:
        return NLPResult(confidence, 'tuling', {})


async def call_tuling123_api(
        ctx_id: str,
        text: Optional[str],
        image: Optional[Union[List[str], str]]) -> List[str]:
    url = 'http://openapi.tuling123.com/openapi/api/v2'
    payload = {
        'reqType': 0,
        'perception': {},
        'userInfo': {
            'apiKey': bot_.config.TULING123_API_KEY,
            'userId': hashlib.md5(ctx_id.encode('ascii')).hexdigest()
        }
    }

    if image and not isinstance(image, str):
        image = image[0]

    if text:
        payload['perception']['inputText'] = {'text': text}
        payload['reqType'] = 0
    elif image:
        payload['perception']['inputImage'] = {'url': image}
        payload['reqType'] = 1
    else:
        return []

    try:
        async with aiohttp.request('POST', url, json=payload) as resp:
            if 200 <= resp.status < 300:
                resp_payload = json.loads(await resp.text())
                if resp_payload.get('results'):
                    return_list = []
                    for result in resp_payload['results']:
                        res_type = result.get('resultType')
                        if res_type in ('text', 'url'):
                            return_list.append(result['values'][res_type])
                    return return_list
            return []
    except aiohttp.ClientError:
        return []
