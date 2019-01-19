from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult
from jieba import posseg

from .joke_data_source import get_info_of_joke


@on_command('joke', aliases=['讲笑话', '讲个笑话', '来个段子'])
async def look_up_date(session: CommandSession):
    jokes = await get_info_of_joke()
    await session.send(jokes)


@on_natural_language(keywords=['笑话', '段子'])
async def _(session: NLPSession):
    stripped_msg_text = session.msg_text.strip()
    words = posseg.lcut(stripped_msg_text)
    joke_words = None

    for word in words:
        if word.flag == 'ns':
            joke_words = word.word

    return NLPResult(90.0, 'joke', {'joke_words': joke_words})
