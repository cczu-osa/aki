import atexit
import asyncio
from os import path
from datetime import datetime

from none import on_natural_language, NLPSession, get_bot
from none.helpers import context_id
from pandas import DataFrame

from maruko import fs, aio

PLUGIN_NAME = 'message_collector'

bot = get_bot()
data_frame: DataFrame = None
lock = asyncio.Lock()


@on_natural_language(only_to_me=False, only_short_message=False)
async def _(session: NLPSession):
    data = {
        'timestamp': [session.ctx['time']],
        'ctx_id': [context_id(session.ctx)],
        'self_id': [session.ctx['self_id']],
        'message': [str(session.ctx['message'])]
    }
    # we don't want to block the processing of message,
    # so just make sure it will append in the future
    asyncio.ensure_future(append_message(data))


async def append_message(data):
    global data_frame
    if data_frame is None:
        data_frame = DataFrame(data)
    else:
        data_frame = data_frame.append(DataFrame(data), ignore_index=True)

    if len(data_frame.index) >= bot.config.MESSAGE_DUMP_SINGLE_FILE_MAX_ROWS:
        async with lock:
            # the following line may use I/O for a little bit time,
            # but since we only do it every MESSAGE_DUMP_SINGLE_FILE_MAX_ROWS
            # messages, it's ok to await here
            await aio.run_sync_func(data_frame.to_parquet,
                                    make_filename(),
                                    compression='gzip')
            data_frame = None


@atexit.register
def exit_callback():
    if data_frame is not None:
        data_frame.to_parquet(make_filename(), compression='gzip')


def make_filename() -> str:
    return path.join(fs.get_data_folder(PLUGIN_NAME),
                     datetime.now().strftime('%Y%m%d%H%M%S.parquet'))
