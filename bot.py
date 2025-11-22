import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config_bot import Config, load_config
from handlers.basic_handlers import *
from handlers.dialog_handlers import *
from promt.create_db import init_db

logger = logging.getLogger(__name__)

config: Config = load_config()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, filemode='w', filename='runner_bot.log', encoding='UTF-8',
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
    )
    bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher()
    init_db()

    dp.include_router(start_router)
    dp.include_router(dialog_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
