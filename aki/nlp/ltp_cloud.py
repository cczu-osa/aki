"""
LTP Cloud API wrapper.

For API docs, see https://www.ltp-cloud.com/document/.
"""

import json
from typing import List, Dict, Any

from nonebot import get_bot

from aki.aio import requests

LTPCloudResult_T = List[List[List[Dict[str, Any]]]]


async def analysis(text: str,
                   pattern: str) -> LTPCloudResult_T:
    bot = get_bot()
    try:
        resp = await requests.post(
            'https://api.ltp-cloud.com/analysis/',
            data={
                'api_key': bot.config.LTP_CLOUD_API_KEY,
                'text': text,
                'pattern': pattern,
                'format': 'json',
            }
        )
        return await resp.json() if resp.ok else []
    except (requests.RequestException, json.JSONDecodeError):
        return []


async def lexer(text: str) -> LTPCloudResult_T:
    # pattern "ner" will do word segmentation, pos tagging, and ner
    return await analysis(text=text, pattern='ner')
