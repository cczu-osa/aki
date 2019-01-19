from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult
from jieba import posseg

from .dictionary_data_source import get_info_of_words


@on_command('look up dictionary', aliases=['查成语', '成语字典', '查成语字典'])
async def look_up_dictionary(session: CommandSession):
    words = session.get('words', prompt='请输入你想查询的成语，每次查询仅限输入一个成语'
                                        '(发送空格退出成语查询)')
    words = words.strip()

    if not words:  # 如果用户发送空格，那么就退出查询
        await session.send('成功退出成语查询')
        return

    words_info = await get_info_of_words(words)
    await session.send('你查询的成语是：' + words)
    await session.send(words_info)


@look_up_dictionary.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return

    session.args[session.current_key] = session.current_arg_text.strip()


@on_natural_language(keywords=['成语', '字典'])
async def _(session: NLPSession):
    stripped_msg_text = session.msg_text.strip()
    words = posseg.lcut(stripped_msg_text)
    words_resp = None

    for word in words:
        if word.flag == 'ns':
            words_resp = word.word

    return NLPResult(90.0, 'look up dictionary', {'words': words_resp})
