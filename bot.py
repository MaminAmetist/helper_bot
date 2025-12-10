import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiohttp import web

from config.config_bot import Config, load_config
from handlers.basic_handlers import *
from handlers.dialog_handlers import *
from promt.create_db import init_db

logger = logging.getLogger(__name__)

config: Config = load_config()
bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp: Dispatcher = Dispatcher()

WEBHOOK_PATH = f"/webhook/{config.tg_bot.token}"


async def handle_webhook(request):
    """Обрабатывает POST-запросы от Telegram."""
    url = str(request.url)

    if url.split('/')[-1] == WEBHOOK_PATH.split('/')[-1]:
        update = Update.model_validate_json(await request.text())
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    else:
        return web.Response(status=403)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, filemode='w', filename='runner_bot.log', encoding='UTF-8',
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
    )
    init_db()

    dp.include_router(start_router)
    dp.include_router(dialog_router)

    try:
        WEB_SERVER_PORT = int(os.environ.get("PORT", 8080))
    except ValueError:
        WEB_SERVER_PORT = 8080

    WEB_SERVER_HOST = "0.0.0.0"

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    await site.start()

    logging.info(f"Bot started as Web Service on port {WEB_SERVER_PORT}")

    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())
