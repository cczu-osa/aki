# Aki

Aki 是 CCZU OSA 编写的一个基于 [NoneBot] 的一个功能型 QQ 机器人核心，具有常见的查询天气、订阅新闻、运行代码、智能聊天等功能。目前 Aki 以机器人**奶茶**（QQ 号 `1647869577`）作为表现层。

[NoneBot]: https://github.com/richardchien/nonebot

仍在编写中，现在功能还很不完善……

## 运行

本项目基于 [NoneBot]，因此在尝试运行本项目之前，请先了解 NoneBot 的使用。

```bash
# 克隆代码
git clone https://github.com/cczu-osa/aki.git
cd aki

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate # Windows
source ./venv/bin/activate # Linux

# 安装依赖
pip install -r requirements.txt

# 运行
python run.py
```

要修改配置，可以导入 `config_base.py` 之后修改，例如：

```python
from config_base import *

DATABASE_URL = 'postgresql://user:password@domain.com:5432/aki'
```

## 期望实现的架构

![架构](assets/架构.png)
