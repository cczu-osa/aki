"""
LTP Cloud API wrapper.

For API docs, see https://www.ltp-cloud.com/document/.
"""

from typing import List, Dict, Any

import requests
from none import get_bot

from maruko import aio

LTPCloudResult_T = List[List[List[Dict[str, Any]]]]


async def analysis(text: str,
                   pattern: str) -> LTPCloudResult_T:
    bot = get_bot()
    try:
        # use requests here to avoid certification error raised by aiohttp
        resp = await aio.run_sync_func(
            requests.post,
            'https://api.ltp-cloud.com/analysis/',
            data={
                'api_key': bot.config.LTP_CLOUD_API_KEY,
                'text': text,
                'pattern': pattern,
                'format': 'json',
            }
        )
        return await aio.run_sync_func(resp.json)
    except requests.RequestException:
        return []


async def lexer(text: str) -> LTPCloudResult_T:
    # pattern "ner" will do word segmentation, pos tagging, and ner
    return await analysis(text=text, pattern='ner')
