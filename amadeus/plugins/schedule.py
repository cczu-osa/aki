import asyncio
import re
import shlex
from typing import List, Optional

from none import CommandGroup, CommandSession, permission as perm
from none.argparse import ArgumentParser, ParserExit, Namespace
from none.command import parse_command
from none.helpers import context_id

from amadeus import scheduler
from amadeus.scheduler import ScheduledCommand

PLUGIN_NAME = 'schedule'

sched = CommandGroup(PLUGIN_NAME, permission=perm.PRIVATE | perm.GROUP_ADMIN)


@sched.command('add', aliases=('schedule',))
async def sched_add(session: CommandSession):
    parser = ArgumentParser()
    parser.add_argument('-S', '--second')
    parser.add_argument('-M', '--minute')
    parser.add_argument('-H', '--hour')
    parser.add_argument('-d', '--day')
    parser.add_argument('-m', '--month')
    parser.add_argument('-w', '--day-of-week')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--name', required=True)
    parser.add_argument('commands', nargs='+')

    args = await parse_args(session, parser,
                            argv=session.get_optional('argv'),
                            help_msg=sched_add_help)

    if not re.match(r'[_a-zA-Z][_a-zA-Z0-9]*', args.name):
        await session.send(
            '计划任务名必须仅包含字母、数字、下划线，且以字母或下划线开头')
        return

    parsed_commands: List[ScheduledCommand] = []
    invalid_commands: List[str] = []

    if args.verbose:
        parsed_commands.append(
            ScheduledCommand(('echo',), f'开始执行计划任务 {args.name}……'))

    for cmd_str in args.commands:
        cmd, current_arg = parse_command(session.bot, cmd_str)
        if cmd:
            tmp_session = CommandSession(session.bot, session.ctx, cmd,
                                         current_arg=current_arg)
            if await cmd.run(tmp_session, dry=True):
                parsed_commands.append(ScheduledCommand(cmd.name, current_arg))
                continue
        invalid_commands.append(cmd_str)
    if invalid_commands:
        invalid_commands_joined = '\n'.join(
            [f'- {c}' for c in invalid_commands])
        await session.send(f'计划任务添加失败，'
                           f'因为下面的 {len(invalid_commands)} 个命令无法被运行'
                           f'（命令不存在或权限不够）：\n'
                           f'{invalid_commands_joined}')
        return

    trigger_args = {k: v for k, v in args.__dict__.items()
                    if k in {'second', 'minute', 'hour',
                             'day', 'month', 'day_of_week'}}
    try:
        job = await scheduler.add_scheduled_commands(
            parsed_commands,
            job_id=scheduler.make_job_id(
                PLUGIN_NAME, context_id(session.ctx), args.name),
            ctx=session.ctx,
            trigger='cron', **trigger_args,
            replace_existing=args.force
        )
    except scheduler.JobIdConflictError:
        # a job with same name exists
        await session.send(f'计划任务 {args.name} 已存在，'
                           f'若要覆盖请使用 --force 参数')
        return

    await session.send(f'计划任务 {args.name} 添加成功')
    await session.send(format_job(args.name, job))


@sched.command('get')
async def sched_get(session: CommandSession):
    parser = ArgumentParser()
    parser.add_argument('name')
    args = await parse_args(session, parser,
                            argv=session.get_optional('argv'),
                            help_msg=sched_get_help)
    job = await scheduler.get_job(scheduler.make_job_id(
        PLUGIN_NAME, context_id(session.ctx), args.name))
    if not job:
        await session.send(f'没有找到计划任务 {args.name}，请检查你的输入是否正确')
        return

    await session.send('找到计划任务如下')
    await session.send(format_job(args.name, job))


@sched.command('list')
async def sched_list(session: CommandSession):
    job_id_prefix = scheduler.make_job_id(PLUGIN_NAME, context_id(session.ctx))
    jobs = await scheduler.get_jobs(scheduler.make_job_id(
        PLUGIN_NAME, context_id(session.ctx)))
    if not jobs:
        await session.send(f'你还没有添加过计划任务')
        return

    for job in jobs:
        await session.send(format_job(job.id[len(job_id_prefix):], job))
        await asyncio.sleep(0.8)
    await session.send_expr(f'以上是所有的 {len(jobs)} 个计划任务')


@sched.command('remove')
async def sched_remove(session: CommandSession):
    parser = ArgumentParser()
    parser.add_argument('name')
    args = await parse_args(session, parser,
                            argv=session.get_optional('argv'),
                            help_msg=sched_remove_help)
    ok = await scheduler.remove_job(scheduler.make_job_id(
        PLUGIN_NAME, context_id(session.ctx), args.name))
    if ok:
        await session.send(f'成功删除计划任务 {args.name}')
    else:
        await session.send(f'没有找到计划任务 {args.name}，请检查你的输入是否正确')


@sched_add.args_parser
@sched_get.args_parser
@sched_list.args_parser
@sched_remove.args_parser
async def _(session: CommandSession):
    session.args['argv'] = shlex.split(session.current_arg_text)


async def parse_args(session: CommandSession, parser: ArgumentParser,
                     argv: Optional[List[str]], help_msg: str) -> Namespace:
    if not argv:
        await session.send(help_msg)
    else:
        try:
            return parser.parse_args(argv)
        except ParserExit as e:
            if e.status == 0:
                # --help
                await session.send(help_msg)
            else:
                await session.send(
                    '参数不足或不正确，请使用 --help 参数查询使用帮助')
    session.finish()  # this will stop the command session


def format_job(job_name: str, job: scheduler.Job) -> str:
    commands = scheduler.get_scheduled_commands_from_job(job)
    commands_str = '\n'.join(
        [f'- {cmd.name}，参数：{cmd.current_arg}' for cmd in commands])
    return (f'名称：{job_name}\n'
            f'下次触发时间：'
            f'{job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'命令：\n'
            f'{commands_str}')


sched_add_help = r"""
使用方法：
    schedule.add [OPTIONS] --name NAME COMMAND [COMMAND ...]

OPTIONS：
    -h, --help  显示本使用帮助
    -S SECOND, --second SECOND  定时器的秒参数
    -M MINUTE, --minute MINUTE  定时器的分参数
    -H HOUR, --hour HOUR  定时器的时参数
    -d DAY, --day DAY  定时器  的日参数
    -m MONTH, --month MONTH  定时器的月参数
    -w DAY_OF_WEEK, --day-of-week DAY_OF_WEEK  定时器的星期参数
    -f, --force  强制覆盖已有的同名计划任务
    -v, --verbose  在执行计划任务时输出更多信息

NAME：
    计划任务名称

COMMAND：
    要计划执行的命令，如果有空格或特殊字符，需使用引号括起来
""".strip()

sched_get_help = r"""
使用方法：
    schedule.get NAME

NAME：
    计划任务名称
""".strip()

sched_remove_help = r"""
使用方法：
    schedule.remove NAME

NAME：
    计划任务名称
""".strip()
