from aki import dt
from aki.db import make_table_name, db


class Account(db.Model):
    __tablename__ = make_table_name('rpg', 'accounts')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qq_number = db.Column(db.BigInteger, nullable=False, unique=True)
    created_dt = db.Column(db.DateTime(timezone=True), default=dt.beijing_now)

    total_coins = db.Column(db.BigInteger, default=0)  # 总金币数
    total_sign_in = db.Column(db.BigInteger, default=0)  # 总签到次数
    last_sign_in_date = db.Column(db.Date)  # 上次签到时间

    @property
    def avatar_url(self):
        return 'https://q1.qlogo.cn/g?b=qq&nk={}&s=40'.format(self.qq_number)
