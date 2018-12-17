import asyncio
import atexit
from datetime import datetime
from os import path
import signal
from typing import Optional

from none import on_natural_language, NLPSession, get_bot
from none.helpers import context_id
from pandas import DataFrame, read_parquet

from amadeus import fs, aio, dt

PLUGIN_NAME = 'message_collector'

bot = get_bot()
data_frame: DataFrame = None
last_collect_dt: datetime = None
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


async def append_message(data) -> None:
    global data_frame, last_collect_dt
    async with lock:
        curr_dt = dt.beijing_now(bot.config.MESSAGE_COLLECTOR_DUMP_FREQ)

        if data_frame is not None and \
                last_collect_dt and last_collect_dt != curr_dt:
            await aio.run_sync_func(dump, last_collect_dt)
            data_frame = None

        if data_frame is None:
            data_frame = DataFrame(data)
        else:
            data_frame = data_frame.append(DataFrame(data), ignore_index=True)
        last_collect_dt = curr_dt


def load(dt_: datetime) -> Optional[DataFrame]:
    filename = make_filename(dt_)
    if path.isfile(filename):
        return read_parquet(filename)


def dump(dt_: datetime) -> None:
    data_frame.to_parquet(make_filename(dt_), compression='gzip')


def make_filename(dt_: datetime) -> str:
    return path.join(fs.get_data_folder(PLUGIN_NAME),
                     dt_.strftime('%Y%m%d%H%M%S.parquet'))


def finalize():
    global data_frame
    if data_frame is not None:
        dump(last_collect_dt or
             dt.beijing_now(bot.config.MESSAGE_COLLECTOR_DUMP_FREQ))
        data_frame = None


def init():
    # initial load
    global data_frame, last_collect_dt
    if data_frame is None:
        curr_dt = dt.beijing_now(bot.config.MESSAGE_COLLECTOR_DUMP_FREQ)
        data_frame = load(curr_dt)
        if data_frame is not None:
            last_collect_dt = curr_dt

    atexit.register(finalize)


init()
