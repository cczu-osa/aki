from nonebot import on_natural_language, NLPSession, NLPResult
from nonebot import permission as perm


@on_natural_language(keywords={'打个招呼', '打招呼'}, permission=perm.SUPERUSER)
async def _(session: NLPSession):
    if '大家' in session.msg_text:
        return NLPResult(100.0, 'echo', {'message': '大家好～'})
