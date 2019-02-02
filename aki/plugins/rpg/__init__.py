from nonebot import CommandGroup

__plugin_name__ = '签到'

cg = CommandGroup('rpg')

from . import account, signin
