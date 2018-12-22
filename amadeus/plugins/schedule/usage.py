ADD = r"""
添加计划任务

使用方法：
    schedule.add [OPTIONS] --name NAME COMMAND [COMMAND ...]

OPTIONS：
    -h, --help  显示本使用帮助
    -S SECOND, --second SECOND  定时器的秒参数
    -M MINUTE, --minute MINUTE  定时器的分参数
    -H HOUR, --hour HOUR  定时器的时参数
    -d DAY, --day DAY  定时器  的日参数
    -m MONTH, --month MONTH  定时器的月参数
    -w DAY_OF_WEEK, --day-of-week DAY_OF_WEEK  定时器的星期参数
    -f, --force  强制覆盖已有的同名计划任务
    -v, --verbose  在执行计划任务时输出更多信息

NAME：
    计划任务名称

COMMAND：
    要计划执行的命令，如果有空格或特殊字符，需使用引号括起来
""".strip()

GET = r"""
获取计划任务

使用方法：
    schedule.get NAME

NAME：
    计划任务名称
""".strip()

REMOVE = r"""
删除计划任务

使用方法：
    schedule.remove NAME

NAME：
    计划任务名称
""".strip()
