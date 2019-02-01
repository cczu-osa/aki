import json
from typing import Any, Dict, List

from nonebot import get_bot

from aki.aio import requests
from aki.cache import cached

API_URL = 'https://free-api.heweather.net/s6/weather'


@cached(ttl=1 * 60 * 60)  # cache for 1 hours
async def get_weather(location: str) -> List[Dict[str, Any]]:
    """
    Example output:

    [{'basic': {'admin_area': '江苏',
                # ...
                'tz': '+8.00'},
      'daily_forecast': [{'cond_code_d': '101',
                          # ...
                          'wind_spd': '2'},
                         {'cond_code_d': '305',
                          # ...
                          'wind_spd': '13'},
                         # ...
                         {'cond_code_d': '305',
                          # ...
                          'wind_spd': '10'}],
      'hourly': [{'cloud': '0',
                  # ...
                  'wind_spd': '5'},
                 # ...
                 {'cloud': '95',
                  # ...
                  'wind_spd': '10'}],
      'lifestyle': [{'brf': '较舒适',
                     'txt': '白天虽然天气晴好，但早晚会感觉偏凉，午后舒适、宜人。',
                     'type': 'comf'},
                    # ...],
      'now': {'cloud': '6',
              # ...
              'wind_spd': '18'},
      'status': 'ok',
      'update': {'loc': '2019-02-01 12:58', 'utc': '2019-02-01 04:58'}}]

    :param location: heweather-compatible location like 南京,江苏 or 武进 or 武进,常州
    :return: weathers of a list of possible locations
    """
    form = {
        'location': location,
        'key': get_bot().config.HEWEATHER_KEY,
    }

    try:
        resp = await requests.post(API_URL, data=form)
        if resp.ok:
            results = (await resp.json())['HeWeather6']
            return list(filter(lambda x: x['status'] == 'ok', results))
    except (requests.RequestException, json.JSONDecodeError,
            TypeError, KeyError):
        pass
    return []
