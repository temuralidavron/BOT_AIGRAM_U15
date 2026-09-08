import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


async def run():
    from handlers import register

    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    register(dp)
    try:
        me = await bot.get_me()
        logger.info("Bot ishga tushdi: @%s", me.username)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()



class Command(BaseCommand):
    help = "Telegram botni ishga tushiradi"

    def handle(self, *args, **options):
        if not settings.BOT_TOKEN:
            raise CommandError("BOT_TOKEN .env faylida ko'rsatilmagan.")
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s | %(levelname)s | %(message)s")
        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nBot to'xtatildi."))