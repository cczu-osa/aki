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

### 配置

要修改配置，可以在项目根目录新建文件 `config_dev.py`，导入 `config_base.py` 之后修改，例如：

```python
from config_base import *

SUPERUSERS = {1234567}
```

`run.py` 默认会尝试导入 `config_dev`（开发环境配置），要部署到生产环境，需要创建 `config_prod.py` 并设置环境变量 `DEPLOYMENT_ENV` 为 `production` 或 `prod`。

### 云服务的 API Key

部分插件需要使用云服务商提供的 API，包括 [百度 AI 平台](https://ai.baidu.com/)、[图灵机器人](http://www.turingapi.com/)、[和风天气](https://www.heweather.com/) 等，如需使用相应功能，请前往相应服务商注册账号并申请 API key，按照 `config_base.py` 的注释填写。

### 数据库

部分插件需要使用数据库进行数据持久化，包括 RPG 游戏、活动报名功能、计划任务和订阅功能等。Aki 使用 PostgreSQL 数据库，要使用需要数据库的功能，请先运行 PostgreSQL 数据库实例，然后修改 Aki 配置文件的 `DATABASE_URL`：

```python
from config_base import *

DATABASE_URL = 'postgresql://user:pass@host:port/database'
```

然后复制 `alembic.ini.sample` 为 `alembic.ini`，修改 `sqlalchemy.url`：

```ini
sqlalchemy.url = postgresql://user:pass@host:port/database
```

在运行 Aki 之前，需要首先运行下面命令以创建数据库表结构：

```bash
alembic upgrade head
```

## 开发

首先按上面的说明运行 Aki（请将开发环境配置放在 `config_dev.py` 模块，不要被 Git 追踪），然后即可进行开发。

通常，添加新的功能只需要在 `aki/plugins` 里面添加新的 NoneBot 插件即可。如需添加配置项，请在 `config_base.py` 中加入相应项，并赋予默认值。

`aki.cache`、`aki.command`、`aki.dt`、`aki.fs`、`aki.helpers`、`aki.log` 等模块分别提供了缓存、命令、时间、文件系统、日志等相关的辅助函数，可以利用。

`aki.db` 模块提供了 [Gino](http://gino.fantix.pro/zh/latest/) 数据库对象，用于注册数据库模型和访问数据库。具体使用方法请参考 Gino 的官方文档，由于此文档不是很详细，可能需要同时参考 [SQLAlchemy](https://docs.sqlalchemy.org/en/latest/) 的文档（Gino 是基于 SQLAlchemy 的）。

如需增加或修改数据库表结构（比如添加或修改了 ORM 模型类），则需要创建数据库迁移脚本，参考 [Create a Migration Script](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script)。迁移脚本的编写可以参考现有的其它脚本。

**注意，由于数据库操作相对比较危险，容易破坏现有数据，请务必在本地开发环境数据库中测试无误再提交代码。**

## 期望实现的架构

![架构](assets/架构.png)

## 开源许可证

本项目使用 [AGPLv3 许可证](LICENSE)，这意味着你可以使用本项目运行你的机器人，并向你的用户提供服务，但如果你需要对项目的源码进行修改，则必须将你修改后的版本对你的用户开源。

由于本项目的特殊性，本项目的源码中出现在 NoneBot 文档的部分（例如作为其示例代码），不使用 AGPLv3 许可，而使用和 NoneBot 一样的 MIT 许可。
