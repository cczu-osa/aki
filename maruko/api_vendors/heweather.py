import json
from typing import Any, Optional, Dict

from none import get_bot

from maruko.aio import requests
from maruko.cache import cached


@cached()
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
            return (await resp.json()).get('HeWeather6', [])[0]
    except (requests.RequestException, json.JSONDecodeError,
            AttributeError, IndexError):
        pass
