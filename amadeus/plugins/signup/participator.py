import re

from none import CommandSession, on_request, RequestSession

from amadeus.command import allow_cancellation
from amadeus.db import db
from amadeus.log import logger
from . import dao, cg
from .models import Event, Signup


@cg.command('signup', aliases=['报名'])
@allow_cancellation
async def signup_signup(session: CommandSession):
    code = session.get('code', prompt='你想报名的活动的活动码是？\n'
                                      '（如果不知道，请询问活动发起人）')

    event = await dao.get_event(code)
    if not event:
        await session.finish('没有找到这个活动呢～')

    if event.end_time:
        await session.finish('该活动报名已经结束啦，请下次再来吧～')

    signup = await dao.get_signup(session.ctx, event)
    if signup:
        await session.finish('你已经报过名啦～')

    if session.is_first_run:
        await session.send(f'欢迎报名参加活动「{event.title}」\n'
                           f'下面我会问你一些问题，以采集必要信息')

    fields = event.fields
    field_values = session.get_optional('field_values', [])

    for curr_idx in range(len(field_values), len(fields)):
        curr_field = fields[curr_idx]
        validator = curr_field.get('validator')
        if not validator:
            validator = {'type': 'allow-all', 'value': None}

        prompt = curr_field['question']
        if validator['type'] == 'choice':
            choices = '\n'.join(
                [f'{i + 1}. {v}' for i, v in enumerate(validator['value'])])
            prompt += f'\n（请输入序号）\n\n{choices}'

        value = session.get(f'field_{curr_idx}', prompt=prompt)

        valid = True
        if validator['type'] == 'regex':
            valid = re.fullmatch(validator['value'], value, re.IGNORECASE)
        elif validator['type'] == 'choice':
            try:
                choice_idx = int(value) - 1
                value = validator['value'][choice_idx]
            except (ValueError, IndexError):
                valid = False
        if not valid:
            await session.pause('输入不符合要求，请重新输入哦～')

        field_values.append(value)
        session.args['field_values'] = field_values

    # information collection done
    signup = await dao.create_signup(session.ctx, event, field_values)
    if not signup:
        if await dao.get_signup(session.ctx, event):
            await session.finish('你已经报过名啦～')
        else:
            await session.send('报名失败，请稍后重试～')
    else:
        msg = '恭喜你报名成功啦！'
        if event.qq_group_number:
            msg += f'请加入此活动官方群 {event.qq_group_number} ' \
                f'及时获取活动通知哦（申请将自动通过）～'
        await session.send(msg)


@signup_signup.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run and stripped_arg:
        session.args['code'] = stripped_arg
        return

    if not session.current_key:
        return

    if not stripped_arg:
        await session.pause('请发送正确的内容哦')

    session.args[session.current_key] = stripped_arg


@on_request('group.add')
async def _(session: RequestSession):
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']

    try:
        count = await db.select([db.func.count(Signup.id)]).where(
            (Signup.event_id == Event.id) &
            (Signup.qq_number == user_id) &
            (Event.qq_group_number == group_id)
        ).gino.scalar()

        if count > 0:
            # the user has signed up
            await session.approve()
    except Exception as e:
        logger.exception(e)
