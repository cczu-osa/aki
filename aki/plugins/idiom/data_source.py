from nonebot import NoneBot

from aki.aio import requests


async def get_info_of_word(bot: NoneBot, word: str) -> str:
    resp = await requests.post(
        'http://v.juhe.cn/chengyu/query',
        data={
            'word': word,
            'key': bot.config.JUHE_IDIOM_API_KEY,
        }
    )
    payload = await resp.json()

    if not payload or not isinstance(payload, dict):  # 返回数据不正确
        return '抱歉，暂时无法查询哦'

    info = ''
    if payload['error_code'] == 0:
        try:
            chengyujs = payload['result']['chengyujs']  # 成语解释
            from_ = payload['result']['from_']  # 成语典故
            tongyi = '\n'.join(payload['result']['tongyi'] or [])  # 同义成语
            fanyi = '\n'.join(payload['result']['fanyi'] or [])  # 反义成语
            info = f'{word}\n\n' \
                f'成语解释：\n{chengyujs}\n\n' \
                f'出处（典故）：\n{from_}\n\n' \
                f'同义成语：\n{tongyi or "无"}\n\n' \
                f'反义成语：\n{fanyi or "无"}\n\n' \
                f'数据来源：聚合数据成语词典'
        except KeyError:
            pass

    return info or '哎呀，查询失败了'


"""
请求参数说明：
word  必填  string  填写需要查询的成语，UTF8 urlencode 编码
key   必填  string  api_key
dtype 选填  string  返回数据格式，xml或json，默认json

JSON返回示例：
{
    "reason": "success",
    "result": {
        "bushou": "禾",
        "head": "积",
        "pinyin": "jī shǎo chéng duō",
        "chengyujs": " 积累少量的东西，能成为巨大的数量。",
        "from_": " 《战国策·秦策四》：“积薄而为厚，聚少而为多。”《汉书·董仲舒传》：“聚少成多，积小致巨。”",
        "example": " 其实一个人做一把刀、一个勺子是有限得很，然而～，这笔账就难算了，何况更是历年如此呢。 《二十年目睹之怪现状》第二十九回",
        "yufa": " 连动式；作谓语、宾语、分句；用于事物的逐渐聚积",
        "ciyujs": "[many a little makes a mickle;from small increments comes abundance;little will grow to much;
        penny and penny laid up will be many] 积累少数而渐成多数",
        "yinzhengjs": "谓只要不断积累，就会从少变多。语出《汉书·董仲舒传》：“众少成多，积小致鉅。”
         唐 李商隐 《杂纂》：“积少成多。” 
         宋 苏轼 《论纲梢欠折利害状》：“押纲纲梢，既与客旅附载物货，官不点检，专栏无由乞取；然梢工自须赴务量纳税钱，以防告訐，积少成多，所获未必减於今日。” 
         清 薛福成 《陈派拨兵船保护华民片》：“惟海军船数不多，经费不裕，势难分拨，兵轮久驻海外， 华 民集貲，积少成多，未尝不愿供给船费。” 
         包天笑 《钏影楼回忆录·入泮》：“这项赏封，不过数十文而已，然积少成多，亦可以百计。”",
        "tongyi": [
            "集腋成裘",
            "聚沙成塔",
            "日积月累",
            "积水成渊"
        ],
        "fanyi": [
            "杯水车薪"
        ]
    },
    "error_code": 0
}
"""
