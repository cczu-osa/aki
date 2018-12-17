from none import on_natural_language, NLPSession


@on_natural_language(allow_empty_message=True)
async def _(session: NLPSession):
    if not session.msg:
        # empty message body
        nicks = list(session.bot.config.NICKNAME)
        if nicks:
            nick = nicks[0]
        else:
            nick = None
        await session.send(f'小主人好呀，{nick or ""}听着呢')
