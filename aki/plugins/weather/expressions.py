WHERE = (
    '你想知道哪个城市的天气呢？',
    '你想知道哪里的天气呢？',
    '你要查询的城市是哪个呢？',
    '你要查询哪个城市呢？',
    '你要查询哪里呢？',
    '哪个城市呢？',
    '请告诉我你要查询的城市～',
)

WHERE_IN_PROVINCE = (
    '{}哪里呢？',
    '{}的哪个城市呢？',
    '{}的哪座城市呢？',
    '具体要查哪个城市呢？',
)

REPORT_NOW = r"""
现在天气{cond_txt}，气温 {tmp} ℃，体感温度 {fl} ℃，能见度 {vis} km，
空气湿度 {hum}%，{wind_dir} {wind_sc} 级。
""".replace('\n', '')

REPORT_FUTURE_DAY = r"""
{0}（{date}）白天天气{cond_txt_d}，晚上天气{cond_txt_n}，
气温 {tmp_min}~{tmp_max} ℃，能见度 {vis} km，空气湿度 {hum}%，
{wind_dir} {wind_sc} 级，降水概率 {pop}%。
""".replace('\n', '')
