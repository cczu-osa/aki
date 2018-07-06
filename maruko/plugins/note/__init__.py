from none import CommandSession, CommandGroup

note = CommandGroup('note')


@note.command('add', aliases=('记录', '记笔记'))
async def note_add(session: CommandSession):
    content = session.get('content', prompt='你想记录什么内容呢？')
    await session.send(f'记录了：{content}')


@note_add.args_parser
async def _(session: CommandSession):
    if not session.current_key and session.current_arg:
        session.args['content'] = session.current_arg
    else:
        session.args[session.current_key] = session.current_arg


@note.command('list', aliases=('查看记录', '查看笔记', '所有笔记'))
async def _(session: CommandSession):
    await session.send('列出所有笔记')


@note.command('remove', aliases=('删除记录', '删除笔记'))
async def note_remove(session: CommandSession):
    id_ = session.get('id', prompt='你想删除的笔记的 ID 是多少呢？')
    await session.send(f'你删除了笔记 {id_}')


@note_remove.args_parser
async def _(session: CommandSession):
    if session.current_key:
        if session.current_arg_text.strip() in {'算了', '不删了', '取消'}:
            session.finish('好的')
            return

    if not session.current_key and session.current_arg.strip():
        # initial interaction, and there is an argument, we take it as the id
        session.current_key = 'id'

    if session.current_key == 'id':
        try:
            id_ = int(session.current_arg.strip())
            session.args['id'] = id_
        except ValueError:
            session.pause('ID 不正确，应只包含数字，请重新输入')
