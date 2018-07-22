import asyncio

from none import CommandSession, CommandGroup
from none.command import call_command
from none.helpers import context_id
from none.expression import render

from maruko import aio, baidu_aip
from maruko.db import db
from maruko.command import handle_cancellation

from . import expressions as expr
from .models import Note

note = CommandGroup('note')


async def note_count(ctx_id: str) -> int:
    return await db.select([db.func.count(Note.id)]).where(
        Note.context_id == ctx_id).gino.scalar()


@note.command('add', aliases=('记录', '记笔记', '添加笔记'))
async def note_add(session: CommandSession):
    content = session.get('content', prompt='你想记录什么内容呢？')
    new_note = await Note.create(
        content=content, context_id=context_id(session.ctx))
    await session.send_expr(expr.NOTE_ADD_SUCCESS,
                            id=new_note.id, content=new_note.content)


@note.command('list', aliases=('查看记录', '查看笔记', '所有笔记'))
async def _(session: CommandSession):
    count = await note_count(context_id(session.ctx))
    if count == 0:
        await session.send_expr(expr.NOTE_LIST_EMPTY)
        return

    all_notes = await Note.query.where(
        Note.context_id == context_id(session.ctx)).gino.all()
    for n in all_notes:
        await session.send(f'ID：{n.id}\r\n内容：{n.content}')
        await asyncio.sleep(0.8)
    await session.send_expr(expr.NOTE_LIST_COMPLETE, count=count)


@note.command('remove', aliases=('删除记录', '删除笔记'))
async def note_remove(session: CommandSession):
    count = await note_count(context_id(session.ctx))
    if count == 0:
        await session.send_expr(expr.NOTE_LIST_EMPTY)
        return

    id_ = session.get('id', prompt='你想删除的笔记的 ID 是多少呢？')
    await session.send(f'你删除了笔记 {id_}')


@note_add.args_parser
@handle_cancellation
async def _(session: CommandSession):
    if not session.current_key and session.current_arg.strip():
        session.args['content'] = session.current_arg
    else:
        session.args[session.current_key] = session.current_arg


@note_remove.args_parser
@handle_cancellation
async def _(session: CommandSession):
    if session.current_key == 'id':
        # currently asking for id, the user may want to ask for all notes
        match_score = 0.0
        nlp = baidu_aip.get_nlp_client()
        try:
            # NOTE!! this block is dangerous, we should do as few as we can
            # here, because we are catching any exceptions and ignore them
            result = await aio.run_sync_func(
                nlp.simnet, '现在有哪些呢？', session.current_arg_text.strip())
            match_score = result.get('score', match_score)
        except:
            # internal request of baidu aip may failed, ignore it
            pass

        if match_score > 0.70:
            # we think it matches
            await session.send_expr(expr.NOTE_QUERYING_ALL)
            await asyncio.sleep(1)
            await call_command(session.bot, session.ctx, ('note', 'list'),
                               check_perm=False,
                               disable_interaction=True)
            await session.pause()

    if not session.current_key and session.current_arg.strip():
        # first interaction, and there is an argument, we take it as the id
        session.current_key = 'id'

    if session.current_key == 'id':
        id_str = session.current_arg.strip()
        try:
            id_ = int(id_str)
            session.args['id'] = id_
        except ValueError:
            session.pause(render(expr.NOTE_BAD_ID, bad_id=id_str))
