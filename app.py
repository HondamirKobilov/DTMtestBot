import pandas as pd
from aiogram.utils import executor
import filters
import handlers
import middlewares
from loader import dp
from utils.database.functions import f_user
from utils.database.models import engine, Base, create_database
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


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
    # await insert_subjects_from_csv()
    # await insert_variants_from_csv()
    # await insert_users_from_csv()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
