import re
from urllib.parse import quote_plus

from nonebot import MessageSegment
from nonebot import on_command, CommandSession

from amadeus.aio import requests

ZHIHU_TEX_SVG_URL = 'https://www.zhihu.com/equation?tex={tex}'
LATEX2PNG_API_URL = 'http://latex2png.com/'
LATEX2PNG_IMAGE_URL = 'http://latex2png.com/output//{name}'


@on_command('tex', aliases=['latex', 'equation', '公式'])
async def tex(session: CommandSession):
    tex_code = session.get('tex_code', prompt='请发送你想要生成图片的 TeX 公式')

    await session.send('正在生成，请稍后……')
    resp = await requests.post(LATEX2PNG_API_URL, data={
        'latex': tex_code,
        'res': '600',
        'color': '000000'
    })
    if not resp.ok:
        session.finish('服务暂时不可用，请稍后再试')

    html = await resp.text
    m = re.search(r'latex_[0-9a-z]+\.png', html)
    if not m:
        session.finish('生成公式图片失败，请稍后再试')

    session.finish(
        MessageSegment.image(LATEX2PNG_IMAGE_URL.format(name=m.group(0))) +
        '\n' + ZHIHU_TEX_SVG_URL.format(tex=quote_plus(tex_code))
    )


@tex.args_parser
async def _(session: CommandSession):
    striped_arg = session.current_arg_text.strip()
    if not session.is_first_run:
        session.args[session.current_key] = striped_arg
        return
    if striped_arg:
        session.args['tex_code'] = striped_arg
