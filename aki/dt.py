from datetime import datetime
from typing import Optional

import pytz
from pandas import Timestamp

CST_TIMEZONE = 'Asia/Shanghai'


def beijing_now(freq: Optional[str] = None) -> datetime:
    now = datetime.now(pytz.timezone(CST_TIMEZONE))
    if freq is not None:
        now = Timestamp(now).round(freq)
    return now


def beijing_from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, pytz.timezone(CST_TIMEZONE))
