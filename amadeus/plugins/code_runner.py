from nonebot import on_command, CommandSession

from amadeus.aio import requests
from amadeus.command import allow_cancellation

GLOT_RUN_API_URL = 'https://glot.io/run/{language}?version=latest'
GLOT_SUPPORTED_LANGUAGES = {
    'assembly': {'ext': 'asm'},
    'bash': {'ext': 'sh'},
    'c': {'ext': 'c'},
    'clojure': {'ext': 'clj'},
    'coffeescript': {'ext': 'coffe'},
    'cpp': {'ext': 'cpp'},
    'csharp': {'ext': 'cs'},
    'erlang': {'ext': 'erl'},
    'fsharp': {'ext': 'fs'},
    'go': {'ext': 'go'},
    'groovy': {'ext': 'groovy'},
    'haskell': {'ext': 'hs'},
    'java': {'ext': 'java', 'name': 'Main'},
    'javascript': {'ext': 'js'},
    'julia': {'ext': 'jl'},
    'kotlin': {'ext': 'kt'},
    'lua': {'ext': 'lua'},
    'perl': {'ext': 'pl'},
    'php': {'ext': 'php'},
    'python': {'ext': 'py'},
    'ruby': {'ext': 'rb'},
    'rust': {'ext': 'rs'},
    'scala': {'ext': 'scala'},
    'swift': {'ext': 'swift'},
    'typescript': {'ext': 'ts'},
}


@on_command(('code_runner', 'run'), aliases=['运行代码', '运行'])
async def run(session: CommandSession):
    supported_languages = ", ".join(sorted(GLOT_SUPPORTED_LANGUAGES.keys()))
    language = session.get('language',
                           prompt='你想运行的代码是什么语言？\n'
                           f'目前支持 {supported_languages}')
    code = session.get('code', prompt='你想运行的代码是？')
    await session.send('正在运行，请稍等……')
    resp = await requests.post(
        GLOT_RUN_API_URL.format(language=language),
        json={
            'files': [{
                'name': (GLOT_SUPPORTED_LANGUAGES[language].get('name',
                                                                'main') +
                         f'.{GLOT_SUPPORTED_LANGUAGES[language]["ext"]}'),
                "content": code
            }],
            'stdin': '',
            'command': ''
        }
    )
    if not resp.ok:
        session.finish('运行失败，服务可能暂时不可用，请稍后再试')

    payload = await resp.json()
    got_result = False
    if isinstance(payload, dict):
        for k in ['stdout', 'stderr', 'error']:
            v = payload.get(k)
            if v:
                await session.send(f'{k}:\n\n{v}')
                got_result = True
    if not got_result:
        session.finish('运行失败，服务可能暂时不可用，请稍后再试')


@run.args_parser
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
    language, *remains = stripped_arg.split('\n', maxsplit=1)
    language = language.strip()
    if language not in GLOT_SUPPORTED_LANGUAGES:
        session.finish('暂时不支持运行你输入的编程语言')
    session.args['language'] = language

    if remains:
        code = remains[0].strip()
        if code:
            session.args['code'] = code
