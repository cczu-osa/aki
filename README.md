# Amadeus

Amadeus 是基于 [NoneBot] 实现的一个功能型 QQ 机器人，（即将）具有常见的查天气、查单词、翻译、教务查询、新闻订阅等功能。

[NoneBot]: https://github.com/richardchien/nonebot

名字来源于动漫《命运石之门 0》中的人工智能 Amadeus，可以通过提取人类记忆来让 Amadeus 拥有其人格、记忆等，动漫中有牧濑红莉栖和比屋定真帆两个版本。

本 repo 的 Amadeus 为一个机器人核心，实际运行中（目前）以**奶茶机器人**作为表现层。

施工中……

## 运行

本项目基于 [NoneBot]，因此在尝试运行本项目之前，请先了解 NoneBot 的使用。

```bash
git clone https://github.com/cczu-osa/amadeus.git
cd amadeus
python run.py
```

要修改配置，可以导入 `config_base.py` 之后修改，例如：

```python
from config_base import *

DATABASE_URL = 'postgresql://amadeus:123456@somedomain.com:5432/amadeus'
```

## 期望实现的架构

![架构](assets/架构.png)
