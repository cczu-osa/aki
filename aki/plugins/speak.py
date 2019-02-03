from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm

__plugin_name__ = '跟我说'


@on_command(('speak', 'to_me'), aliases=['跟我说'])
async def speak_to_me(session: CommandSession):
    content = session.get('content', prompt='跟你说啥？')
    session.finish(content, at_sender=True)


@on_command(('speak', 'to_all'), aliases=['跟大家说'], permission=perm.GROUP)
async def speak_to_all(session: CommandSession):
    content = session.get('content', prompt='跟大家说啥？')
    session.finish(content)


@speak_to_me.args_parser
@speak_to_all.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['content'] = stripped_arg
        return

    if not stripped_arg:
        session.finish('你好奇怪呀，看不懂你的意思QAQ')
    session.state[session.current_key] = stripped_arg


@on_natural_language
async def _(session: NLPSession):
    stripped_msg = session.msg.strip()
    if stripped_msg.startswith('跟我说'):
        content = stripped_msg[len('跟我说'):].lstrip()
        return IntentCommand(65.0, ('speak', 'to_me'),
                             args={'content': content})
    if stripped_msg.startswith('跟大家说'):
        content = stripped_msg[len('跟大家说'):].lstrip()
        return IntentCommand(65.0, ('speak', 'to_all'),
                             args={'content': content})
