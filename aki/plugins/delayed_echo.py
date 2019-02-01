import asyncio

from nonebot import on_command, CommandSession
from nonebot.command import call_command


@on_command('delayed_echo')
async def _(session: CommandSession):
    try:
        delay = float(session.state.get('delay', 1))
    except ValueError:
        delay = 1
    delay = min(delay, 10)
    delay = max(delay, 0.1)
    await asyncio.sleep(delay)
    await call_command(session.bot, session.ctx, 'echo',
                       current_arg=session.current_arg,
                       args=session.state)
