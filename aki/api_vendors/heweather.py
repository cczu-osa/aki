import json
from typing import Any, Optional, Dict

from aiocache import cached
from nonebot import get_bot

from aki.aio import requests


@cached(10 * 60)
async def find(location: str) -> Optional[Dict[str, Any]]:
    try:
        resp = await requests.get(
            'https://search.heweather.com/find',
            params={
                'location': location,
                'key': get_bot().config.HEWEATHER_KEY,
                'group': 'cn',
            }
        )
        if resp.ok:
            results = (await resp.json()).get('HeWeather6', [])
            assert isinstance(results[0], dict)
            return results[0]
    except (requests.RequestException, json.JSONDecodeError,
            AttributeError, IndexError, AssertionError):
        pass
