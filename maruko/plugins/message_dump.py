import atexit
import asyncio
from os import path
from datetime import datetime

from none import on_natural_language, NLPSession, get_bot
from none.helpers import context_id
from pandas import DataFrame

from maruko import fs, aio

PLUGIN_NAME = 'message_dump'

_bot = get_bot()
_data_frame: DataFrame = None
_lock = asyncio.Lock()


@on_natural_language(only_to_me=False, only_short_message=False)
async def _(session: NLPSession):
    global _data_frame
    if _data_frame is None:
        _data_frame = DataFrame({
            'ctx_id': [context_id(session.ctx)],
            'self_id': [session.ctx['self_id']],
            'message': [str(session.msg)]
        })
    else:
        _data_frame = _data_frame.append({
            'ctx_id': context_id(session.ctx),
            'self_id': session.ctx['self_id'],
            'message': str(session.msg)
        }, ignore_index=True)

    if len(_data_frame.index) >= _bot.config.MESSAGE_DUMP_SINGLE_FILE_MAX_ROWS:
        async with _lock:
            # the following line may use I/O for a little bit time,
            # but since we only do it every MESSAGE_DUMP_SINGLE_FILE_MAX_ROWS
            # messages, it's ok to await here
            await aio.run_sync_func(_data_frame.to_parquet, make_filename())
            _data_frame = None


@atexit.register
def exit_callback():
    if _data_frame is not None:
        _data_frame.to_parquet(make_filename())


def make_filename() -> str:
    return path.join(fs.get_data_folder(PLUGIN_NAME),
                     datetime.now().strftime('%Y%m%d%H%M%S.parquet'))
