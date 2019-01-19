from nonebot import CommandGroup

__plugin_name__ = 'Bilibili'

cg = CommandGroup('bilibili_anime')

from . import index, timeline, nlp
