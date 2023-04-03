import logging
import random
from asyncio import sleep
from functools import cache
from pathlib import Path

from aiogram import Bot, Dispatcher, Message
from environs import Env

log = logging.getLogger(__name__)

random.seed()
env = Env()

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_ID = env.int('TELEGRAM_ADMIN_ID')
GITHUB_URL = env('GITHUB_URL')


dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")


@dp.message(commands={"start"})
async def command_start_handler(message: Message):
    user = message.from_user
    log.debug(f'-> {user.id} @{user.username} {message.text}')
    await message.answer('This bot scans https://telegra.ph for articles with any title you specify. This bot only does the scan and is not responsible for any content posted on the site.')
    await message.answer(f'Wanna contribute or self-host? Visit {GITHUB_URL}')
    await message.answer('Please enter search phrase and wait for search to complete.')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG,
    )
    dp.run_polling(bot)
