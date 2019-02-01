import asyncio
import re
import string
from typing import List

from nonebot import CommandSession, CommandGroup
from nonebot import permission as perm
from nonebot.command import call_command
from nonebot.command.argfilter import converters, extractors, validators
from nonebot.helpers import context_id

from aki import scheduler
from aki.command import allow_cancellation
from aki.helpers import random_string
from aki.scheduler import ScheduledCommand

__plugin_name__ = '订阅'

PLUGIN_NAME = 'subscribe'

cg = CommandGroup(
    'subscribe',
    permission=perm.PRIVATE | perm.GROUP_ADMIN | perm.DISCUSS
)


@cg.command('subscribe', aliases=['订阅', '添加订阅', '新增订阅', '新建订阅'])
async def subscribe(session: CommandSession):
    message = session.get(
        'message', prompt='你想订阅什么内容呢？',
        arg_filters=[validators.not_empty('请输入有效内容哦～')]
    )

    hour = session.state.get('hour')
    minute = session.state.get('minute')
    if hour is None or minute is None:
        time = session.get(
            'time',
            prompt='你希望我在每天的什么时候给你推送呢？\n'
                   '（请使用24小时制，并使用阿拉伯数字表示小时和分钟）'
        )
        m = re.match(r'(?P<hour>\d{1,2})[.:：](?P<minute>\d{1,2})', time)
        if not m:
            m = re.match(r'(?P<hour>\d{1,2})\s*[点时]\s*'
                         r'(?:(?P<minute>\d{1,2}|半|一刻)\s*[分]?)?', time)

        if m:
            hour = int(m.group('hour'))
            session.state['hour'] = hour
            try:
                minute = int(m.group('minute') or 0)
            except ValueError:
                if m.group('minute') == '半':
                    minute = 30
                elif m.group('minute') == '一刻':
                    minute = 15
            session.state['minute'] = minute
        else:
            del session.state['time']
            session.pause('时间格式不对啦，请重新发送')

    repeat = session.get(
        'repeat',
        prompt='是否希望我在推送消息的时候重复你上面发的消息内容呢？（请回答是或否）',
        arg_filters=[
            extractors.extract_text,
            converters.simple_chinese_to_bool,
            validators.ensure_true(lambda x: x is not None,
                                   '我听不懂呀，请用是或否再回答一次呢')
        ]
    )

    escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
    if repeat:
        switch_arg = f'--repeat "{escaped_message}"'
    else:
        switch_arg = f'"{escaped_message}"'

    try:
        job = await scheduler.add_scheduled_commands(
            ScheduledCommand('switch', switch_arg),
            job_id=scheduler.make_job_id(
                PLUGIN_NAME, context_id(session.ctx),
                (random_string(1, string.ascii_lowercase) +
                 random_string(7, string.ascii_lowercase + string.digits))
            ),
            ctx=session.ctx,
            trigger='cron', hour=hour, minute=minute,
            replace_existing=False
        )
        session.finish(f'订阅成功啦，下次推送时间 '
                       f'{job.next_run_time.strftime("%Y-%m-%d %H:%M")}')
    except scheduler.JobIdConflictError:
        session.finish('订阅失败，有可能只是运气不好哦，请稍后重试～')


@subscribe.args_parser
@allow_cancellation
async def _(session: CommandSession):
    if session.is_first_run:
        if session.current_arg:
            session.state['message'] = session.current_arg
        return


@cg.command('show', aliases=['查看订阅', '我的订阅'])
async def _(session: CommandSession):
    jobs = session.state.get('jobs') or \
           await get_subscriptions(session.ctx)

    if not jobs:
        session.finish(f'你还没有订阅任何内容哦')

    for i, job in enumerate(jobs):
        await session.send(format_subscription(i + 1, job))
        await asyncio.sleep(0.2)
    session.finish(f'以上是所有的 {len(jobs)} 个订阅')


@cg.command('unsubscribe', aliases=['取消订阅', '停止订阅', '关闭订阅', '删除订阅'])
async def unsubscribe(session: CommandSession):
    jobs = session.state.get('jobs') or \
           await get_subscriptions(session.ctx)
    index = session.state.get('index')
    if index is None:
        session.state['jobs'] = jobs
        await call_command(session.bot, session.ctx, ('subscribe', 'show'),
                           args={'jobs': jobs},
                           disable_interaction=True)
        index = session.get(
            'index', prompt='你想取消哪一个订阅呢？（请发送序号）',
            arg_filters=[
                extractors.extract_text,
                validators.ensure_true(str.isdigit, '请输入序号哦～'),
                int,
            ]
        )

    index = index - 1
    if not (0 <= index < len(jobs)):
        session.finish('没有找到你输入的序号哦')

    job = jobs[index]
    if await scheduler.remove_job(job.id):
        session.finish('取消订阅成功')
    else:
        session.finish('出了点问题，请稍后再试吧')


async def get_subscriptions(ctx) -> List[scheduler.Job]:
    return await scheduler.get_jobs(scheduler.make_job_id(
        PLUGIN_NAME, context_id(ctx)))


def format_subscription(index: int, job: scheduler.Job) -> str:
    command = scheduler.get_scheduled_commands_from_job(job)[0]
    switch_argument = command.current_arg
    message = switch_argument[switch_argument.find('"') + 1:-1]
    message = message.replace('\\"', '"').replace('\\\\', '\\')
    return (f'序号：{index}\n'
            f'下次推送时间：'
            f'{job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'订阅内容：'
            f'{message}')
