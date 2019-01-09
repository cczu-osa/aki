from urllib.parse import quote_plus

from nonebot import MessageSegment
from nonebot import on_command, CommandSession, get_loaded_plugins

MANUAL_IMAGE_URL = 'https://raw.githubusercontent.com/cczu-osa/amadeus/master/assets/manuals/{plugin_name}.png'


@on_command('man', aliases=['manual', 'help', 'usage',
                            '帮助', '使用帮助', '使用方法', '使用手册', '帮助手册'])
async def _(session: CommandSession):
    plugin_name = session.current_arg_text.strip()
    plugins = list(filter(lambda p: p.name, get_loaded_plugins()))

    if not plugin_name:
        reply = (f'欢迎使用奶茶机器人～\n'
                 f'我现在支持下面这些功能，'
                 f'你可以给我发送「帮助+空格+功能名」获取使用帮助！\n\n' +
                 '\n'.join(map(lambda p: p.name, plugins)))
        session.finish(reply)

    for plugin in filter(lambda x: x.name.lower() == plugin_name.lower(),
                         plugins):
        if plugin.usage:
            await session.send(plugin.usage)
        else:
            usage = MessageSegment.image(MANUAL_IMAGE_URL.format(
                plugin_name=quote_plus(plugin_name)
            ))
            await session.send(usage)
