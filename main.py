# ============================================================
#  5-DARS — FSM: buyurtma rasmiylashtirish
#
#  NIMA O'ZGARDI (3-darsga nisbatan):
#    - Bitta main.py o'rniga 7 ta fayl
#    - callback_data satri o'rniga TIPLI CallbackData
#    - Ishlaydigan savat (hozircha xotirada)
#
#  FAYLLAR VAZIFASI:
#    data.py       — mahsulotlar (keyin Django modeli bo'ladi)
#    storage.py    — savat (keyin Django modeli bo'ladi)
#    callbacks.py  — tugma "manzillari"
#    keyboards.py  — barcha tugmalar
#    handlers/     — mantiq, mavzu bo'yicha bo'lingan
#    main.py       — faqat yig'ish va ishga tushirish
#
#  ISHGA TUSHIRISH:  python main.py
# ============================================================

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers import register

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register(dp)

    logging.info("Bot ishga tushdi: @%s", (await bot.get_me()).username)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
