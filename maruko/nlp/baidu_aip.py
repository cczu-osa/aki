"""
Baidu AIP package wrapper.
"""

from typing import Optional, List, Dict, Any

from aip import AipNlp
from none import get_bot

from maruko import aio

_nlp: Optional[AipNlp] = None


def get_nlp_client() -> AipNlp:
    global _nlp
    if _nlp is None:
        bot_ = get_bot()
        _nlp = AipNlp(bot_.config.BAIDU_AIP_APP_ID,
                      bot_.config.BAIDU_AIP_API_KEY,
                      bot_.config.BAIDU_AIP_SECRET_KEY)
    return _nlp


async def simnet(text1: str, text2: str) -> float:
    nlp = get_nlp_client()

    score = 0.00
    try:
        nlp_res = await aio.run_sync_func(nlp.simnet, text1, text2)
        score = nlp_res.get('score', score)
    except:
        # internal request of baidu aip may failed, ignore it
        pass
    return score


async def lexer(text: str) -> List[Dict[str, Any]]:
    nlp = get_nlp_client()
    try:
        nlp_res = await aio.run_sync_func(nlp.lexer, text)
        return nlp_res.get('items', [])
    except:
        # internal request of baidu aip may failed, ignore it
        return []
