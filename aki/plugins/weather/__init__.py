import re

from nonebot import CommandSession, CommandGroup
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.helpers import render_expression as expr

from aki import nlp, logger
from aki.command import allow_cancellation
from aki.plugins.weather.data_source import get_weather
from . import expressions as e

w = CommandGroup('weather')


@w.command('weather', aliases=('weather', '天气', '天气预报', '查天气'))
async def weather_command(session: CommandSession):
    location = session.get('location', prompt=expr(e.WHERE))
    if location.province and not location.city and not location.district:
        # there is no city or district, ask the user for more info!
        if 'location_more' in session.state:
            del session.state['location_more']
        session.get('location_more', prompt=expr(e.WHERE_IN_PROVINCE,
                                                 location.province))

    logger.debug(f'Location: {location}')
    final_loc = location.heweather_format()
    weathers = await get_weather(final_loc)
    if len(weathers) > 1:
        await session.send(f'查询到 {len(weathers)} 个同名地区')
    elif len(weathers) == 0:
        session.finish(f'没有查询到{location.short_format()}的天气哦')

    for weather in weathers:
        basic = weather['basic']
        location_name = basic['admin_area'] + basic['parent_city']
        if basic['parent_city'] != basic['location']:
            location_name += basic['location']
        report_now = expr(e.REPORT_NOW, **weather['now'])
        report_tomorrow = expr(
            e.REPORT_FUTURE_DAY,
            '明天',
            **weather['daily_forecast'][1]
        )
        report_after_tomorrow = expr(
            e.REPORT_FUTURE_DAY,
            '后天',
            **weather['daily_forecast'][2]
        )
        await session.send(f'{location_name}\n\n'
                           f'{report_now}\n\n'
                           f'{report_tomorrow}\n\n'
                           f'{report_after_tomorrow}')


@weather_command.args_parser
@allow_cancellation
async def _(session: CommandSession):
    striped_text_arg = session.current_arg_text.strip()
    if not striped_text_arg:
        # ignore empty argument
        return

    if session.is_first_run:
        session.current_key = 'location'

    if session.current_key == 'location':
        location = await nlp.parse_location(striped_text_arg)
        if any([location.province, location.city, location.district]):
            session.state['location'] = location
    elif session.current_key == 'location_more':
        patched_loc = await nlp.parse_location(striped_text_arg)
        location: nlp.Location = session.state.get('location')
        assert location
        # merge location
        location.province = location.province or patched_loc.province
        location.city = location.city or patched_loc.city
        location.district = location.district or patched_loc.district
        session.state['location'] = location
    else:
        session.state[session.current_key] = striped_text_arg


@on_natural_language({'天气'})
async def _(session: NLPSession):
    text = re.sub(r'\s+', '', session.msg_text.strip())
    if not text:
        return

    confidence = 70.0

    if re.match(r'(?:怎么|咋)样\S{0,5}$', text) or \
            re.search(r'查(?:一?下|查看?)', text):
        confidence += 10.0
    if text.endswith('？') or text.endswith('?'):
        confidence += 5.0

    args = {}

    seg_paragraphs = await nlp.lexer(text)
    if seg_paragraphs:
        words = seg_paragraphs[0]
        for word in words:
            if word['ne'] == 'LOC':
                location = await nlp.parse_location(word['basic_words'])
                if any((location.province, location.city, location.district)):
                    args['location'] = location
            elif word['ne'] == 'TIME':
                args['time'] = word['item']

    confidence += len(args) * 5 if args else 0.0
    return IntentCommand(min(confidence, 100.0), ('weather', 'weather'),
                         args=args)

# @on_natural_language({'雨', '雪', '晴', '阴', '冰雹', '雾'})
# async def _(session: NLPSession):
#     text = session.msg_text.strip()
#     from pprint import pprint
#     pprint(await nlp.lexer(text))
#
#     # if not ('?' in session.msg_text or '？' in session.msg_text):
#     #     return None
#     # return NLPResult(90.0, ('weather', 'weather'), {})
