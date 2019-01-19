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

JOKE_API_KEY = ''  # 输入你的api_key,来源：聚合数据服务——笑话大全

DICTIONARY_API_KEY = ''  # 输入你的api_key，来源：聚合数据服务——成语字典

TULING123_API_KEY = ''

MESSAGE_COLLECTOR_DUMP_FREQ = 'H'

AIOCACHE_DEFAULT_CONFIG = {
    'cache': 'aiocache.SimpleMemoryCache',
    'serializer': {
        'class': 'aiocache.serializers.PickleSerializer'
    }
}

MANUAL_IMAGE_URL_FORMAT = 'https://raw.githubusercontent.com/cczu-osa/amadeus/master/manual/screenshots/{}.png'
