from typing import Optional

from nonebot.typing import Context_T

from aki import logger
from .models import Account


async def get_or_create_account(ctx: Context_T) -> Optional[Account]:
    user_id = ctx.get('user_id')
    if user_id is None:
        return None

    try:
        account = await Account.query.where(
            Account.qq_number == user_id).gino.first()
        if account is None:
            account = await Account.create(qq_number=user_id)
        return account
    except Exception as e:
        logger.exception(e)
        return None


async def update(account: Account, **kwargs) -> bool:
    try:
        await account.update(**kwargs).apply()
        return True
    except Exception as e:
        logger.exception(e)
        return False
