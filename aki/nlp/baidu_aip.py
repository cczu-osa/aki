"""
Baidu AIP package wrapper.

For API docs, see http://ai.baidu.com/docs#/NLP-API/89828646.
"""

from typing import Optional, List, Dict, Any

from aip import AipNlp
from nonebot import get_bot

from aki import aio

_nlp: Optional[AipNlp] = None


def get_nlp_client() -> AipNlp:
    global _nlp
    if _nlp is None:
        bot = get_bot()
        _nlp = AipNlp(bot.config.BAIDU_AIP_APP_ID,
                      bot.config.BAIDU_AIP_API_KEY,
                      bot.config.BAIDU_AIP_SECRET_KEY)
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
