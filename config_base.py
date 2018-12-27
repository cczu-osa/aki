from os import path

from nonebot.default_config import *

NICKNAME = ['奶茶', '小奶茶']
COMMAND_START = {'', '/', '!', '／', '！'}
COMMAND_SEP = {'/', '.'}
SESSION_CANCEL_EXPRESSION = ('好的',)
SESSION_RUN_TIMEOUT = timedelta(seconds=20)

DATA_FOLDER = path.join(path.dirname(__file__), 'data')

DATABASE_URL = ''

BAIDU_AIP_APP_ID = ''
BAIDU_AIP_API_KEY = ''
BAIDU_AIP_SECRET_KEY = ''

LTP_CLOUD_API_KEY = ''

TULING123_API_KEY = ''

MESSAGE_COLLECTOR_DUMP_FREQ = 'H'

AIOCACHE_DEFAULT_CONFIG = {
    'cache': 'aiocache.SimpleMemoryCache',
    'serializer': {
        'class': 'aiocache.serializers.PickleSerializer'
    }
}
