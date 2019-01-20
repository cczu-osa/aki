import os

from nonebot import get_bot

from .log import logger


def get_data_folder(sub_folder: str = '') -> str:
    data_folder = get_bot().config.DATA_FOLDER
    if sub_folder:
        data_folder = os.path.join(data_folder, sub_folder)

    logger.debug(f'Creating data folder {data_folder} if not exists')
    os.makedirs(data_folder, mode=0o755, exist_ok=True)
    return data_folder
