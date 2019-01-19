from jieba_fast import posseg
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult

from .data_source import get_info_of_word


@on_command('idiom', aliases=['查成语', '成语', '成语词典'])
async def idiom(session: CommandSession):
    word = session.get('word',
                       prompt='请输入你想查询的成语，每次查询仅限输入一个成语'
                              '（发送空格退出查询）')
    word = word.strip()

    if not word:  # 如果用户发送空格，那么就退出查询
        await session.send('成功退出成语查询')
        return

    word_info = await get_info_of_word(session.bot, word)
    await session.send(word_info)


@idiom.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run and stripped_arg:
        session.args['word'] = stripped_arg
        return

    if not session.current_key:
        return

    session.args[session.current_key] = stripped_arg


@on_natural_language(keywords=['成语', '词典', '字典'])
async def _(session: NLPSession):
    stripped_msg_text = session.msg_text.strip()
    for word in posseg.lcut(stripped_msg_text):
        if word.flag in ('i', 'l'):  # i 表示成语，l 表示习惯用语（可能是成语）
            return NLPResult(90.0, 'idiom', {'word': word.word})
