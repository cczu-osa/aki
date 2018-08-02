import atexit
import asyncio
from os import path
from datetime import datetime
from typing import Dict, Any

from none import message_preprocessor, get_bot
from none.helpers import context_id
from pandas import DataFrame

from maruko import fs, aio

PLUGIN_NAME = 'message_dump'

bot = get_bot()
data_frame: DataFrame = None
lock = asyncio.Lock()


@message_preprocessor
async def _(ctx: Dict[str, Any]):
    data = {
        'timestamp': [ctx['time']],
        'ctx_id': [context_id(ctx)],
        'self_id': [ctx['self_id']],
        'message': [str(ctx['message'])]
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
