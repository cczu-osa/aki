from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot.helpers import context_id


from aki.plugins.signin import data  # 导入用户的小金库数据
from .red_packet_soure import prepare_red_packet, check, check_get_red_packet, check_red_packet  # 导入处理红包信息的函数


@on_command('sand_red_packet', aliases=['发红包'], permission=perm.GROUP)  # 任何人都可以发起，发起时需要@机器人
async def send_red_packet(session: CommandSession):

    warn = await check(session.bot.config.RED_PACKET)  # 首先检查上一轮红包是否被抢光，就算被其他命令中断，下一次也可以继续抢红包
    if warn:
        await session.send('有红包还没有抢完呢，先别着急发红包哟')
        return

    ctx_id = context_id(session.ctx, mode='user')
    if ctx_id not in data.keys():  # 对于那些从未签到过、小金库中没有个人记录的用户，做出以下处理
        await session.send('抱歉，你未在小金库中留有个人记录，可以尝试去签到或者在下一轮中抢别人的红包，'
                           '这样就可以在小金库中留下你的个人记录，所以你现在暂时不能发红包')
        return

    if not data[ctx_id]['wealth']:  # 检查用户的小金库里还有没有金币
        await session.send('不好意思哟，' + session.ctx['sender']['nickname']
                           + '，你的小金库没有金币了呢，所以暂不能发红包，坚持每天签到可获得金币哦')
        return

    coins_num = session.get('coin_num', prompt='请' + session.ctx['sender']['nickname'] + '往你的红包里塞金币吧!\n'
                                               + '温馨提示：你的小金库里现有' + str(data[ctx_id]['wealth'])
                                               + '个金币')
    try:  # 检查要求发送的金币数额是否正确
        coins_num = int(coins_num)
        resp = await prepare_red_packet(coins_num, ctx_id, session.bot.config.RED_PACKET)
        await session.send(resp)

    except ValueError:  # 输入了非正整数的数额
        await session.send('红包发送失败了呢！请输入有效的金币数目哦，金币数目应该为正整数个，且不超过你的小金库存款')


@on_command('get_red_packet', aliases=['抢红包'], only_to_me=False, permission=perm.GROUP)  # 只要发送抢红包即可开抢，不需要@机器人
async def get_red_packet(session: CommandSession):

    nickname = session.ctx['sender']['nickname']  # 获取用户昵称
    ctx_id = context_id(session.ctx, mode='user')  # 获取用户id
    resp = await check_get_red_packet(nickname, session.bot.config.RED_PACKET, session.bot.config.PER_COINS, ctx_id)
    await session.send(resp)

    warn = await check(session.bot.config.RED_PACKET)  # 每次有人抢完红包都需要检查一下红包剩余金额，方便及时结束本轮抢红包
    if warn:  # 如果红包没有抢完，请继续
        return

    # 否则的话，开始清理本次抢红包的成果
    resp = await check_red_packet(session.bot.config.PER_COINS)
    if resp:  # 如果resp不为空，即抢红包正常结束，不是红包没有发起的情形
        session.bot.config.PER_COINS = {}  # 清空本轮抢红包的记录
        await session.send(resp)


@send_red_packet.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return
    session.args[session.current_key] = session.current_arg_text.strip()
