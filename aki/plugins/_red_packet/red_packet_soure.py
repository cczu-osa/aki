import random
from aki.plugins._signin import data  # 导入用户的小金库数据


async def check(red_packet):  # 防止发红包命令重叠或者检查红包剩余金额
    if red_packet:  # 检查上一轮红包是否被抢光，如果没有抢光，让新的发红包命令失效
        return 1
    return 0  # 如果红包抢光了，允许发起新的发红包命令


async def prepare_red_packet(coin_num, ctx_id, red_packet):
    if coin_num > data[ctx_id]['wealth']:  # 检查金币数量是否符合规范
        return f'抱歉，你要求发送的红包中，金币数量已超过你的小金库所能承受的金币的数量，红包发送失败'
    elif coin_num <= 0:
        return f'抱歉，你要求发送的红包中，金币数量不符合规范，金币数量应该为正整数个，且不超过你的小金库存款，红包发送失败'
    else:
        red_packet += coin_num  # 将局部的金币数量储存在全局变量中
        data[ctx_id]['wealth'] -= red_packet  # 发起红包的用户减去等量的金币
        return f'总额为{red_packet}个金币的虚拟红包已经成功发出，发送“抢红包”即可开抢，祝大家财运滚滚来哟~'


async def check_get_red_packet(nickname, red_packet, per_coins, ctx_id):
    if nickname not in per_coins.keys():  # 检查每人每轮抢红包的次数，规定每人每轮只许抢一次红包
        if red_packet:  # 检查红包剩余金币数目。正常情况下，当一轮红包被抢完时，会自动结束本轮抢红包。所以红包余额为零，就是没有人发起红包的情况
            get_coins = random.randint(1, red_packet)  # 随机决定抢到的金币数目
            per_coins[nickname] = get_coins
            red_packet -= get_coins  # 更新红包剩余金额

            if ctx_id not in data.keys():  # 如果抢红包的用户在小金库中没有记录
                data[ctx_id] = {'last_signin_date': None,
                                'signin_count': 0,
                                'wealth': get_coins}  # 我们将帮助他创建一个小金库账户，并记录下这次获得的金额
            else:
                data[ctx_id]['wealth'] += get_coins  # 将本次获得的金币累加到用户账户中
            return f'恭喜你，{nickname}，你本次抢红包获得了{get_coins}个金币\n\n本轮红包还剩：{red_packet}个金币'

        else:  # 在没有人发起红包的情况下有人抢红包
            return f'暂时还没有人发起红包活动呢，试着试用一下“发红包”的命令吧'

    else:  # 每轮红包有人多抢的处理方案
        return f'本次你已经抢过红包了，留点机会给其他人，耐心等待等下一轮的红包吧'


async def check_red_packet(per_coins):
    if not per_coins:  # 对于没有发起红包导致的金币数量为零的情况，上面已经处理过了，这里就不再多此一举的说明了
        return

    luck_dog = []  # 存储本次抢到红包的金币数值
    for luck in per_coins.values():
        luck_dog.append(luck)

    luck_dog = max(luck_dog)

    luck_man = ''  # 本次抢红包获得金币最多的运气王
    for luck in per_coins.keys():
        if luck_dog != per_coins[luck]:
            continue
        luck_man += luck + '，抢到了：' + str(luck_dog) + '个金币！\n'

    return f'红包被抢完了呢，本轮红包的运气王如下：\n\n{luck_man}'
