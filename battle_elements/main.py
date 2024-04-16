import asyncio
import logging
import os

import django
from fastapi import Depends, FastAPI
from social_bot.config.config import bot, dp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'battle_elements.settings')


app = FastAPI()


async def on_startup(dp):
    logging.basicConfig(
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.INFO,
    )
    logging.info('Bot started')


async def on_shutdown(dp):
    await dp.storage.close()


def start_django():
    os.environ.setdefault(
         'DJANGO_SETTINGS_MODULE',
         'battle_elements.settings',
    )
    django.setup()


async def start_bot():
    start_django()
    await load_data()
    from social_bot.handlers import battle_list, battles, user_registr
    dp.include_routers(
        user_registr.router,
        battles.router,
        battle_list.router,)
    await dp.start_polling(bot)


if __name__ == "__main__":
    start_django()
    from social_bot.config.django import load_data
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup(dp))
    loop.run_until_complete(start_bot())
