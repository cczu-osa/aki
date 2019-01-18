from urllib.parse import quote_plus

from nonebot import MessageSegment
from nonebot import on_command, CommandSession, get_loaded_plugins
from nonebot import on_natural_language, NLPSession, NLPResult

KEYWORDS = ['帮助', '使用帮助', '使用方法', '使用手册', '帮助手册']


@on_command('man', aliases=['manual', 'help', 'usage', *KEYWORDS])
async def _(session: CommandSession):
    plugin_name = session.current_arg_text.strip()
    plugins = list(filter(lambda p: p.name, get_loaded_plugins()))

    if not plugin_name:
        await send_manual_image(session, 'index')
        return

    for plugin in filter(lambda x: x.name.lower() == plugin_name.lower(),
                         plugins):
        if plugin.usage:
            await session.send(plugin.usage)
        else:
            await send_manual_image(session, plugin.name)


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
    return NLPResult(100.0 - miss, ('man',))
