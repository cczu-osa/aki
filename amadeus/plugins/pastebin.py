from nonebot import on_command, CommandSession

from amadeus.aio import requests
from amadeus.command import allow_cancellation

API_URL = 'https://paste.cczu.org/'
ABOUT_PAGE_URL = 'https://paste.cczu.org/static/about.html'


@on_command(('pastebin', 'paste'), aliases=['paste', '粘贴'])
async def paste(session: CommandSession):
    syntax = session.get('syntax',
                         prompt=f'你想粘贴的语法是？\n'
                         f'请在 {ABOUT_PAGE_URL} 查看支持的语法列表')
    content = session.get('content', prompt='你想要粘贴的内容是？')
    expire = 30 * 24 * 60  # 30 days
    poster = ''
    secret = 'False'
    resp = await requests.post(API_URL, allow_redirects=False, data={
        'poster': poster,
        'expire': expire,
        'secret': secret,
        'syntax': syntax,
        'content': content
    })
    if resp.raw_response.status_code == 302:
        location = resp.raw_response.headers['Location']
        session.finish(f'粘贴成功，链接 {location}')
    else:
        session.finish(f'粘贴失败，PasteBin 服务可能暂时不可用，请稍后再试')


@paste.args_parser
@allow_cancellation
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.rstrip()
    if not session.is_first_run:
        if not stripped_arg:
            session.pause('请输入有效内容')
        session.args[session.current_key] = stripped_arg
        return

    if not stripped_arg:
        return

    # first argument is not empty
    syntax, *remains = stripped_arg.split('\n', maxsplit=1)
    syntax = syntax.strip()
    session.args['syntax'] = syntax if syntax != '-' else 'Plains Text'

    if remains:
        content = remains[0].strip()
        if content:
            session.args['content'] = content
