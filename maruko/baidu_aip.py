from typing import Optional

from aip import AipNlp
from none import get_bot

_nlp: Optional[AipNlp] = None


def get_nlp_client() -> AipNlp:
    global _nlp
    if _nlp is None:
        bot_ = get_bot()
        _nlp = AipNlp(bot_.config.BAIDU_AIP_APP_ID,
                      bot_.config.BAIDU_AIP_API_KEY,
                      bot_.config.BAIDU_AIP_SECRET_KEY)
    return _nlp
