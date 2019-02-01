from urllib.parse import quote_plus

from nonebot import MessageSegment
from nonebot import on_command, CommandSession, get_loaded_plugins
from nonebot import on_natural_language, NLPSession, IntentCommand

KEYWORDS = ['帮助', '使用帮助', '使用方法', '使用手册', '帮助手册', '功能', '查看功能']


@on_command('man', aliases=['manual', 'help', 'usage', *KEYWORDS],
            only_to_me=False)
async def _(session: CommandSession):
    plugin_name = session.current_arg_text.strip()
    plugins = list(filter(lambda p: p.name, get_loaded_plugins()))

    if not plugin_name:
        await send_manual_image(session, 'index')
        return

    found = False
    for plugin in filter(lambda x: x.name.lower() == plugin_name.lower(),
                         plugins):
        found = True
        if plugin.usage:
            await session.send(plugin.usage)
        else:
            await send_manual_image(session, plugin.name)

    if not found:
        await session.send(f'暂时没有 {plugin_name} 这个功能呢')


async def send_manual_image(session: CommandSession, plugin_name: str) -> None:
    url_format = session.bot.config.MANUAL_IMAGE_URL_FORMAT
    if url_format.startswith('file:'):
        url = url_format.format(plugin_name)
    else:
        url = url_format.format(quote_plus(plugin_name))
    await session.send(MessageSegment.image(url))


@on_natural_language(KEYWORDS)
async def _(session: NLPSession):
    miss = max(0, len(session.msg_text) - 4) * 5
    return IntentCommand(100.0 - miss, 'man')
