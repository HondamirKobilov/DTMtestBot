from datetime import datetime
import pytz
from environs import Env
from data.channels_manager import ChannelsManager
env = Env()
env.read_env()
BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
VARIANTS_CHANNEL = env.int("VARIANTS_CHANNEL")
PRE_POST_LINK = f"t.me/c/{str(VARIANTS_CHANNEL).replace('-100', '')}/"
USERNAME_START = env.str("USERNAME_START")
domen = "https://mandatuz.uz/"
DB_USER = "postgres"
DB_PASS = "123"
DB_HOST = "localhost"
# DB_NAME = "dtm_test_bot"
DB_NAME = "dtm_mathjax"
channels_manager = ChannelsManager()
uzbekistan_timezone = pytz.timezone("Asia/Tashkent")

months_uz = {
    1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
    5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
    9: "sentabr", 10: "oktabr", 11: "noyabr", 12: "dekabr"
}

def toshkent_now() -> datetime:
    toshkent_zone = pytz.timezone('Asia/Tashkent')
    return datetime.now(toshkent_zone).replace(tzinfo=None)
WEB_APP_URL = 'https://aede-92-63-205-189.ngrok-free.app'
referral_link = "https://t.me/itpark123245bot?start=r_"