import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from parsers.telegraph import TelegraphParser
from environs import Env

log = logging.getLogger(__name__)

env = Env()

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_ID = env.int('TELEGRAM_ADMIN_ID')
GITHUB_URL = env('GITHUB_URL')
SEARCH_LIMIT = env.int('SEARCH_LIMIT', default=10)


dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")


@dp.message()
async def command_handler(message: Message):
    user = message.from_user
    log.debug(f'-> {user.id} @{user.username} {message.text}')

    if user.id != TELEGRAM_ADMIN_ID:
        await bot.forward_message(TELEGRAM_ADMIN_ID, message.chat.id, message.message_id)

    if message.text == "/start":
        await message.answer('This bot scans https://telegra.ph for articles with any title you specify.')
        await message.answer('IMPORTANT! This bot only does the scan and sends URLS back to user. The bot is not responsible for any content posted on the site. All the posts retrieved by bot are public and can be viewed by anyone on the internet. Please address website owners if you find any inappropriate content.')
        await message.answer(f'Wanna more options / contribute / self-host? Visit {GITHUB_URL}')
        await message.answer('Please enter search phrase and wait for search to complete. Shorter phrases are more likely to be found.')
        return

    if len(message.text) > 64:
        await message.answer('Please enter search phrase shorter than 64 characters.')
        return

    try:
        async with TelegraphParser() as telegraph:
            await message.answer('Searching...')

            i = 1
            async for page in telegraph.iter_pages(search_term=message.text, limit=SEARCH_LIMIT):
                await message.answer(page.url)
                i += 1

            await message.answer('Search complete. Enter another phrase to search')

    except Exception:
        log.exception(message.text)
        await message.answer('Oops! Something went wrong. Please try again later.')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG,
    )
    dp.run_polling(bot)
