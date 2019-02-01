import re
from urllib.parse import quote_plus

from nonebot import MessageSegment
from nonebot import on_command, CommandSession
from nonebot.command.argfilter import extractors, validators

from aki.aio import requests

__plugin_name__ = '公式'

ZHIHU_TEX_SVG_URL_FORMAT = 'https://www.zhihu.com/equation?tex={}'
LATEX2PNG_API_URL = 'http://latex2png.com/'
LATEX2PNG_IMAGE_URL_FORMAT = 'http://latex2png.com/output//{}'


@on_command('tex', aliases=['latex', 'equation', '公式'])
async def tex(session: CommandSession):
    if session.is_first_run:
        stripped_text = session.current_arg_text.strip()
        if stripped_text:
            session.state['tex_code'] = stripped_text

    tex_code = session.get(
        'tex_code',
        prompt='请发送你想要生成图片的 TeX 公式',
        arg_filters=[
            extractors.extract_text,
            str.strip,
            validators.not_empty('公式不能为空，请重新发送～'),
        ]
    )

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
        MessageSegment.image(LATEX2PNG_IMAGE_URL_FORMAT.format(m.group(0))) +
        '\n' + ZHIHU_TEX_SVG_URL_FORMAT.format(quote_plus(tex_code))
    )
