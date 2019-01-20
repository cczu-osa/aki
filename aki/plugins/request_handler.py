from nonebot import on_request, RequestSession


@on_request('friend', 'group.invite')
async def _(session: RequestSession):
    await session.approve()
