import io

import nonebot.permission as perm
from nonebot import CommandSession, CQHttpError

from aki import dt
from aki.aio import requests
from aki.command import allow_cancellation
from . import dao, cg


@cg.command('start', aliases=['发起报名'])
async def signup_start(session: CommandSession):
    title = session.get('title', prompt='你想发起报名的活动名称是？')
    fields = session.get('fields', prompt='你需要参与者填写的信息是？')
    max_signups = session.get('max_signups',
                              prompt='活动的报名人数上限是多少？\n'
                                     '（如果不限制报名人数，请发送 0）')

    event = await dao.start_event(session.ctx, title, fields, max_signups)
    if event:
        await session.send(f'你已成功发起「{title}」活动报名\n'
                           f'请让参与者给我发送「报名 {event.code}」来报名此活动～\n'
                           f'\n即：')
        await session.send(f'报名 {event.code}')
    else:
        await session.send(f'发起活动报名失败，请稍后再试')


@signup_start.args_parser
@allow_cancellation
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run and stripped_arg:
        session.state['title'] = stripped_arg
        return

    if not session.current_key:
        return

    if not stripped_arg:
        session.pause('请发送正确的内容哦')
        return

    if session.current_key == 'title':
        if len(stripped_arg) > 100:
            session.pause('活动名称太长啦，换个短一点的吧')
        session.state[session.current_key] = stripped_arg
        return
    elif session.current_key == 'fields':
        # e.g.
        # 姓名||?||你的名字叫？||regex||\w{3,}
        # 年级||?||是哪个年级的呢？||choice||18;17;16;15;其他

        fields = []
        for line in filter(lambda l: l.strip(), stripped_arg.splitlines()):
            field = {
                'name': None,
                'question': None,
                'validator': None
            }

            field['name'], *others = line.strip().split('||')
            if not field['name']:
                continue

            try:
                it = iter(others)
                while True:
                    op = next(it).strip()
                    if op == '?':
                        field['question'] = next(it).strip()
                    elif op == 'regex':
                        field['validator'] = {
                            'type': op,
                            'value': next(it)
                        }
                    elif op == 'choice':
                        choices = list(
                            filter(lambda x: x,
                                   [x.strip() for x in next(it).split(';')])
                        )
                        field['validator'] = {
                            'type': op,
                            'value': choices
                        }
            except StopIteration:
                pass

            field['question'] = field['question'] or f'{field["name"]}？'
            fields.append(field)

        if fields:
            session.state['fields'] = fields
    elif session.current_key == 'max_signups':
        try:
            session.state['max_signups'] = max(0, int(stripped_arg))
        except ValueError:
            session.pause('报名人数上限必须是数字哦，如果不限制报名人数，请发送 0')


@cg.command('show', aliases=['查看报名'])
async def signup_show(session: CommandSession):
    code = session.state.get('code')
    if code:
        # show one
        event = await dao.get_event(code)
        if not event:
            session.finish(f'没有找到你输入的活动码对应的活动哦')

        if event.context_id != dao.ctx_id_by_user(session.ctx):
            session.finish(f'此活动不是由你发起的哦，无法查看报名信息')

        qq_group = event.qq_group_number or '未绑定'
        start_date = dt.beijing_from_timestamp(
            event.start_time).strftime('%Y-%m-%d')
        end_date = dt.beijing_from_timestamp(
            event.end_time).strftime('%Y-%m-%d') if event.end_time else '未结束'
        signup_count = await dao.get_signup_count(event)
        if signup_count is None:
            signup_count = '查询失败'
        if event.max_signups > 0:
            signup_count = f'{signup_count}/{event.max_signups}'
        info = f'活动名称：{event.title}\n' \
            f'活动码：{event.code}\n' \
            f'活动官方群：{qq_group}\n' \
            f'报名开始日期：{start_date}\n' \
            f'报名结束日期：{end_date}\n' \
            f'报名人数：{signup_count}'
        await session.send(info)
    else:
        # show all
        show_ended = session.state.get('show_ended', False)
        events = list(filter(lambda e: bool(e.end_time) == show_ended,
                             await dao.get_all_events(session.ctx)))

        p = '已结束的' if show_ended else '正在进行中的'
        if not events:
            session.finish(f'你目前没有{p}活动报名')

        await session.send(f'你发起的{p}活动报名有：')
        await session.send('\n\n'.join(
            map(lambda e: f'活动名称：{e.title}\n活动码：{e.code}', events)
        ))


@signup_show.args_parser
@allow_cancellation
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg == '-e':
            session.state['show_ended'] = True
        else:
            session.state['code'] = stripped_arg


@cg.command('export', aliases=['导出报名', '导出报名信息', '导出报名表'])
async def signup_export(session: CommandSession):
    code = session.get('code', prompt='你要导出报名信息的活动码是？')
    event = await dao.get_event(code)
    if not event:
        session.finish(f'没有找到你输入的活动码对应的活动哦')

    if event.context_id != dao.ctx_id_by_user(session.ctx):
        session.finish(f'此活动不是由你发起的哦，无法导出报名信息')

    signups = await dao.get_all_signups(event)
    if not signups:
        session.finish('当前还没有人报名，无法导出报名信息哦')

    await session.send(f'共有 {len(signups)} 条报名信息，'
                       f'正在上传到文件发送服务，请稍等……')

    csv_content = ','.join([f['name'] for f in event.fields] + ['QQ']) + '\r\n'
    csv_content += '\r\n'.join(','.join(s.field_values + [str(s.qq_number)])
                               for s in signups)
    csv_file = io.BytesIO(csv_content.encode('utf-8-sig'))
    resp = await requests.post(
        'http://tmp.link/openapi/v1',
        files={'file': (f'a.csv', csv_file)},
        data={'model': '0', 'action': 'upload'}
    )
    payload = await resp.json()
    if payload.get('status') != 0:
        await session.send('上传失败，请稍后再试')
    else:
        url = payload["data"]["url"]
        if session.ctx['message_type'] == 'group':
            await session.send(f'「{event.title}」报名表链接：{url}',
                               ensure_private=True)
            await session.send('上传成功，链接已私聊发送，请查收')
        else:
            await session.send(f'上传成功，链接：{url}')


@cg.command('end', aliases=['结束报名'])
async def signup_end(session: CommandSession):
    code = session.get('code', prompt='你要结束报名的活动码是？')
    event = await dao.get_event(code)
    if not event:
        session.finish(f'没有找到你输入的活动码对应的活动哦')

    if event.context_id != dao.ctx_id_by_user(session.ctx):
        session.finish(f'此活动不是由你发起的哦，无法结束报名')

    if await dao.end_event(event):
        await session.send('结束报名成功')
    else:
        await session.send('结束报名失败，请稍后再试')


@cg.command('bind_group', aliases=['绑定报名'], permission=perm.GROUP_ADMIN)
async def signup_bind_group(session: CommandSession):
    code = session.get('code', prompt='你要绑定到本群的活动码是？')
    event = await dao.get_event(code)
    if not event:
        session.finish(f'没有找到你输入的活动码对应的活动哦')

    if event.context_id != dao.ctx_id_by_user(session.ctx):
        session.finish(f'此活动不是由你发起的哦，无法绑定报名')

    group_id = session.ctx.get('group_id')
    if not group_id:
        # superuser may accidentally call this command, should skip
        session.finish('当前聊天不是群聊，无法绑定报名')

    try:
        # check my sole in the current group
        role = (await session.bot.get_group_member_info(
            group_id=group_id,
            user_id=session.ctx['self_id']
        ))['role']
    except CQHttpError:
        role = None

    if role not in ['admin', 'owner']:
        # not admin
        session.finish('要先把我设置为管理员才可以绑定报名哦～')

    if group_id and await dao.bind_event_with_qq_group(event, group_id):
        await session.send(f'已成功将本群绑定为「{event.title}」活动官方群，'
                           f'请将加群方式设置为「需要验证消息」，'
                           f'我会自动同意已经报名的人的加群请求')
    else:
        await session.send('绑定报名失败，请稍后再试')


@signup_export.args_parser
@signup_end.args_parser
@signup_bind_group.args_parser
@allow_cancellation
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['code'] = stripped_arg
    elif stripped_arg:
        session.state[session.current_key] = stripped_arg
    else:
        session.pause('请发送正确的内容哦')
