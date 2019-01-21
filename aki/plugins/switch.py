import asyncio

from nonebot import on_command, CommandSession
from nonebot.argparse import ArgumentParser
from nonebot.command import kill_current_session
from nonebot.message import Message, handle_message


@on_command('switch', privileged=True, shell_like=True)
async def switch(session: CommandSession):
    parser = ArgumentParser(session=session, usage=USAGE)
    parser.add_argument('-r', '--repeat-message',
                        action='store_true', default=False)
    parser.add_argument('message')
    args = parser.parse_args(session.argv)

    kill_current_session(session.ctx)

    msg = Message(args.message)
    if args.repeat_message:
        await session.send(msg)

    ctx = session.ctx.copy()
    ctx['message'] = msg
    ctx['to_me'] = True  # ensure to_me
    asyncio.ensure_future(handle_message(session.bot, ctx))


USAGE = r"""
切换到新的消息上下文（让机器人假装收到一段消息，然后进行正常的消息处理逻辑）

使用方法：
    switch [OPTIONS] MESSAGE

OPTIONS：
    -h, --help  显示本使用帮助
    -r, --repeat-message  重复发送 MESSAGE 参数内容

MESSAGE：
    新的消息内容
""".strip()
