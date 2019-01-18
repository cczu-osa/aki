from amadeus.aio import requests
from config_base import DICTIONARY_API_KEY  # 从config_base中导入相关API_KEY，详情请见config_base


async def get_info_of_words(words: str) -> str:
    resp = await requests.post('http://v.juhe.cn/chengyu/query?',  # 支持http get/post请求方式
                               data={
                                    'word': words,
                                    'key': DICTIONARY_API_KEY,
                               })
    dictionary_data = await resp.json()

    if not dictionary_data:  # 返回数据为空
        dictionary_resp = '抱歉，暂时无法获取成语字典的相关数据，可能是成语字典服务暂停或者其他的原因'

    else:
        try:  # 尝试读取数据
            if dictionary_data['error_code'] == 0:  # 首先判断错误码
                chengyujs = dictionary_data['result']['chengyujs']  # 成语解释
                from_ = dictionary_data['result']['from_']  # 成语典故
                tongyi = ''  # 初始化储存同义成语的变量
                fanyi = ''   # 初始化储存反义成语的变量
                for ty in dictionary_data['result']['tongyi']:  # 同义成语
                    tongyi += (ty + '\n')
                for fy in dictionary_data['result']['fanyi']:  # 反义成语
                    fanyi += (fy + '\n')
                dictionary_resp = '成语解释：\n' + chengyujs + '\n' \
                                  '\n出自(典故)：\n' + from_ + '\n' \
                                  '\n同义成语：\n' + tongyi + '\n' \
                                  '反义成语：\n' + fanyi + '\n' \
                                  '数据来源：聚合成语字典'
                 
            else:  # 系统级错误
                dictionary_resp = '哎呀，成语数据获取失败了呢，可能是服务中断或者试检查输入的成语是否存在'
        except KeyError:  # 读取数据失败
            dictionary_resp = '无法获取成语数据了呢，可能是网络服务暂停或者其他的原因，请联系项目的开发者试图解决这个问题吧'

    return f'{dictionary_resp}'  # 返回结果


'''
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
'''
