import re

from none import CommandSession, CommandGroup
from none import on_natural_language, NLPSession, NLPResult
from none.expression import render

from maruko import nlp
from maruko.command import allow_cancellation

from . import expressions as expr

w = CommandGroup('weather')


@w.command('weather', aliases=('weather', '天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    location = session.get('location', prompt_expr=expr.WHERE)
    # time = session.get_optional('time')

    province = location.province or session.get_optional('loc_province')
    city = location.city or session.get_optional('loc_city')
    district = location.district or session.get_optional('loc_district')

    if province and not city and not district:
        city = session.get(
            'loc_city',
            prompt=render(expr.WHERE_IN_PROVINCE, province=province))

    final_loc = district or city
    await session.send(f'位置：{final_loc}')


@weather.args_parser
@allow_cancellation
async def _(session: CommandSession):
    striped_text_arg = session.current_arg_text.strip()
    if not striped_text_arg:
        # ignore empty argument
        return

    if not session.current_key:
        session.current_key = 'location'

    if session.current_key == 'location':
        location = await nlp.parse_location(striped_text_arg)
        if any((location.province, location.city, location.district)):
            session.args['location'] = location
    elif session.current_key.startswith('loc_'):
        patched_loc = await nlp.parse_location(striped_text_arg)
        location: nlp.Location = session.args.get('location')
        assert location
        location.province = location.province or patched_loc.province
        location.city = location.city or patched_loc.city
        location.district = location.district or patched_loc.district
        session.args['location'] = location
    else:
        session.args[session.current_key] = striped_text_arg


@on_natural_language({'天气'})
async def _(session: NLPSession):
    text = re.sub(r'\s+', '', session.msg_text.strip())
    if not text:
        return

    confidence = 59.0

    if re.match(r'(?:怎么|咋)样\S{0,5}$', text) or \
            re.search(r'查(?:一?下|查看?)', text):
        confidence += 15.0
    if text.endswith('？') or text.endswith('?'):
        confidence += 5.0

    args = {}

    words = (await nlp.lexer(text))[0]
    for word in words:
        if word['ne'] == 'LOC':
            location = await nlp.parse_location(word['basic_words'])
            if any((location.province, location.city, location.district)):
                args['location'] = location
        elif word['ne'] == 'TIME':
            args['time'] = word['item']

    confidence += len(args) * 10.0 / 2.0 + 10.0 if args else 0.0
    return NLPResult(min(confidence, 100.0), ('weather', 'weather'), args)


@on_natural_language({'雨', '雪', '晴', '阴', '冰雹', '雾'})
async def _(session: NLPSession):
    text = session.msg_text.strip()
    from pprint import pprint
    pprint(await nlp.lexer(text))

    # if not ('?' in session.msg_text or '？' in session.msg_text):
    #     return None
    # return NLPResult(90.0, ('weather', 'weather'), {})
