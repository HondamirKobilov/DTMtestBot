import asyncio
import pandas as pd
from aiogram.utils import executor
from aiogram import types

import filters
import handlers
import middlewares
from loader import dp
from utils.database.functions import f_user
from utils.database.models import engine, Base, create_database
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.database.functions.f_diagnostika import check_diagnostika_status  # ✅ Diagnostikani avtomatik tekshirish

async def insert_users_from_csv():
    users_df = pd.read_csv('data/users.csv')
    for _, row in users_df.iterrows():
        is_premium = row["is_premium"] == 't'
        await f_user.create_user(
            user_id=row["user_id"],
            username=row["username"] if pd.notna(row["username"]) else None,
            is_premium=is_premium,
            share_value=row["share_value"] if pd.notna(row["share_value"]) else None
        )
        print(f"Added user: {row['username']} with user_id: {row['user_id']}")

async def on_startup(dispatcher):
    _ = middlewares, filters, handlers
    await create_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

    # ✅ Diagnostika avtomatik status yangilashni fon jarayoniga qo‘shish
    asyncio.create_task(check_diagnostika_status())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_diagnostika_status())  # ✅ Background taskni ishga tushiramiz
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, allowed_updates=types.AllowedUpdates.all())
