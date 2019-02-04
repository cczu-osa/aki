from nonebot import on_command, CommandSession
from nonebot import permission as perm
import random


from aki.plugins._signin import data  # 导入用户的小金库数据


RED_PACKET = {'red_packet': 0}  # 红包的剩余金额数
PER_COINS = {}  # 记录抢红包的人员及其金额


@on_command('sand_red_packet', aliases=['发红包'], permission=perm.GROUP)  # 任何人都可以发起，发起时需要@机器人
async def send_red_packet(session: CommandSession):

    if RED_PACKET['red_packet']:  # 首先检查上一轮红包是否被抢光，就算被其他命令中断，下一次也可以继续抢红包
        await session.send('还有红包没有抢完呢，先别着急发红包哟')
        return

    ctx_id = session.ctx['user_id']
    if ctx_id not in data.keys():  # 对于那些从未签到过、小金库中没有个人记录的用户，做出以下处理
        await session.send('抱歉，你未在小金库中留有个人记录，可以尝试去签到或者在下一轮中抢别人的红包，'
                           '这样就可以在小金库中留下你的个人记录，所以你现在暂时不能发红包')
        return

    if not data[ctx_id]['wealth']:  # 检查用户的小金库里还有没有金币
        await session.send('不好意思哟，' + session.ctx['sender']['nickname']
                           + '，你的小金库没有金币了呢，所以暂不能发红包，坚持每天签到可获得金币哦')
        return

    coins_num = session.get('coin_num', prompt=(session.ctx['sender']['nickname'] + '，请往你的红包里塞金币吧!\n'
                            + '温馨提示：你的小金库里现有' + str(data[ctx_id]['wealth']) + '个金币'))
    try:  # 检查要求发送的金币数额是否正确
        coins_num = int(coins_num)
        if coins_num > data[ctx_id]['wealth']:  # 检查金币数量是否符合规范
            await session.send('抱歉，你要求发送的红包中，金币数量已超过你的小金库所能承受的金币的数量，红包发送失败')
        elif coins_num <= 0:
            await session.send('抱歉，你要求发送的红包中，金币数量不符合规范，金币数量应该为正整数个，'
                               '且不超过你的小金库存款，红包发送失败')
        else:
            RED_PACKET['red_packet'] += coins_num  # 将局部的金币数量储存在全局变量中
            data[ctx_id]['wealth'] -= RED_PACKET['red_packet']  # 发起红包的用户减去等量的金币
            await session.send('稍等一下哦，奶茶正在准备把你的红包发送出去……')
            await session.send('总额为' + str(RED_PACKET['red_packet'])
                               + '个金币的虚拟红包已经成功发出，发送“抢红包”即可开抢，祝大家财运滚滚来哟~')

    except ValueError:  # 输入了非正整数的数额
        await session.send('红包发送失败了呢！请输入有效的金币数目哦，金币数目应该为正整数个，且不超过你的小金库存款')


@on_command('get_red_packet', aliases=['抢红包'], only_to_me=False, permission=perm.GROUP)  # 只要发送抢红包即可开抢，不需要@机器人
async def get_red_packet(session: CommandSession):

    nickname = session.ctx['sender']['nickname']  # 获取用户昵称
    ctx_id = session.ctx['user_id']  # 获取用户id
    if nickname not in PER_COINS.keys():  # 检查每人每轮抢红包的次数，规定每人每轮只许抢一次红包
        if RED_PACKET['red_packet']:  # 检查红包剩余金币数目。正常情况下，当一轮红包被抢完时，会自动结束本轮抢红包。所以红包余额为零，就是没有人发起红包的情况
            get_coins = random.randint(1, RED_PACKET['red_packet'])  # 随机决定抢到的金币数目
            PER_COINS[nickname] = get_coins
            RED_PACKET['red_packet'] -= get_coins  # 更新红包剩余金额

            if ctx_id not in data.keys():  # 如果抢红包的用户在小金库中没有记录
                data[ctx_id] = {'last_signin_date': None,
                                'signin_count': 0,
                                'wealth': get_coins}  # 我们将帮助他创建一个小金库账户，并记录下这次获得的金额
            else:
                data[ctx_id]['wealth'] += get_coins  # 将本次获得的金币累加到用户账户中
            await session.send('恭喜你，' + nickname + '，你本次抢红包获得了' + str(get_coins) + '个金币!\n'
                                                   '\n本轮红包还剩：' + str(RED_PACKET['red_packet']) + '个金币!')

        else:  # 在没有人发起红包的情况下有人抢红包
            await session.send('暂时还没有人发起红包活动呢，试着用一下“发红包”的命令吧')

    else:  # 每轮红包有人多抢的处理方案
        await session.send('本次你已经抢过红包了，留点机会给其他人，耐心等待等下一轮的红包吧')

    # 每次有人抢完红包都需要检查一下红包剩余金额，方便及时结束本轮抢红包
    if RED_PACKET['red_packet']:  # 如果红包没有抢完，请继续
        return

    # 否则的话，开始清理本次抢红包的成果
    if not PER_COINS:  # 对于没有发起红包导致的金币数量为零的情况，上面已经处理过了，这里就不再多此一举的说明了
        return

    luck_dog = []  # 存储本次抢到红包的金币数值
    for luck in PER_COINS.values():
        luck_dog.append(luck)

    luck_dog = max(luck_dog)  # 找出最大金额

    luck_man = ''  # 公布本次抢红包获得金币最多的运气王
    for luck in PER_COINS.keys():
        if luck_dog != PER_COINS[luck]:
            continue
        luck_man += luck + '，抢到了：' + str(luck_dog) + '个金币！\n'
    await session.send('红包被抢完了呢，本轮红包的运气王如下：\n'
                       '\n' + luck_man)

    delete_name = []  # 删除的名单
    for name in PER_COINS.keys():
        delete_name.append(name)

    for name in delete_name:  # 清空本次抢红包记录
        del PER_COINS[name]


@send_red_packet.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return
    session.args[session.current_key] = session.current_arg_text.strip()
