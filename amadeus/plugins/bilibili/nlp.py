import re
from datetime import datetime, timedelta

from none import on_natural_language, NLPSession, NLPResult


@on_natural_language(keywords=['番', '动漫', '动画'])
async def _(session: NLPSession):
    m = re.search(r'(?:(?P<year>\d{2})\s*年\s*)?(?P<month>\d{1,2})\s*月',
                  session.msg_text)
    year, month = None, None
    if m:
        year = m.group('year')
        month = m.group('month')

    args = {}
    if year:
        args['year'] = int(year)
        if args['year'] < 100:
            args['year'] += 2000
    if month:
        args['month'] = int(month)

    possibility = 90
    if '哪些' in session.msg_text or '什么' in session.msg_text:
        possibility += 3
    if not re.search(r'b\s*站', session.msg_text, re.IGNORECASE):
        possibility -= 10

    return NLPResult(possibility, ('bilibili_anime', 'index'), args)


@on_natural_language(keywords=['更新'])
async def _(session: NLPSession):
    m = re.match(r'(?:b\s*站)?(?P<day_str>(?:前|昨|今|明|大?后)天)?(?P<name>.+?)'
                 r'(?P<day_str2>(?:前|昨|今|明|大?后)天)?[会有]?更(?:不更)?新',
                 session.msg_text, re.IGNORECASE)
    day_str, name = None, None
    if m:
        day_str = m.group('day_str') or m.group('day_str2')
        name = m.group('name')

    if not name:
        return None

    possibility = 92
    if not day_str:
        possibility -= 5
    if '吗' in session.msg_text:
        possibility += 3
    if not re.search(r'b\s*站', session.msg_text, re.IGNORECASE):
        possibility -= 10

    delta_day_dict = {'前天': -2, '昨天': -1, '今天': 0,
                      '明天': 1, '后天': 2, '大后天': 3}
    delta_day = delta_day_dict.get(day_str, 0)
    date = (datetime.now() + timedelta(days=delta_day)).strftime('%m-%d')

    return NLPResult(possibility, ('bilibili_anime', 'timeline'),
                     {'date': date, 'name': name})


@on_natural_language(keywords=['更新'])
async def _(session: NLPSession):
    m = re.match(r'(?:b\s*站)?(?P<name>.+?)(?:(?:什么|啥)时候)?[会有]?更新',
                 session.msg_text, re.IGNORECASE)
    name = m.group('name') if m else None

    if not name:
        return None

    possibility = 90
    if not re.search(r'b\s*站', session.msg_text, re.IGNORECASE):
        possibility -= 10

    return NLPResult(possibility, ('bilibili_anime', 'timeline'),
                     {'name': name})
