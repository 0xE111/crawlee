import logging

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from parsers.telegraph import TelegraphParser
from environs import Env
import random

log = logging.getLogger(__name__)

env = Env()

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_ID = env.int('TELEGRAM_ADMIN_ID')
GITHUB_URL = env('GITHUB_URL')
SEARCH_LIMIT = env.int('SEARCH_LIMIT', default=10)
BLACKLIST = env.list('BLACKLIST', default=[])


dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")
queue = asyncio.Queue(maxsize=128)


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
        queue_size = queue.qsize()
        if queue_size == 0:
            await message.answer('Processing your request...')
        else:
            await message.answer(f'Added your request to queue, please wait. Your queue number: {queue_size+1}')
        queue.put_nowait(message)

    except queue.Full:
        await message.answer('Sorry, the queue is full. Please try again later.')


async def process_queue():
    log.debug('Listening for messages...')
    blacklist_lowered = [word.lower() for word in BLACKLIST]

    async with TelegraphParser() as telegraph:
        while True:
            message: Message = await queue.get()
            user_id = message.from_user.id
            log.debug('Processing message by %s: %s', message.from_user, message.text)
            try:
                if any(word in message.text.lower() for word in blacklist_lowered):
                    await asyncio.sleep(random.randint(3, 10))
                else:
                    async for page in telegraph.iter_pages(search_term=message.text, limit=SEARCH_LIMIT):
                        await bot.send_message(
                            user_id,
                            page.url,
                            disable_web_page_preview='<img' in page.html and user_id != TELEGRAM_ADMIN_ID,
                        )
                await bot.send_message(user_id, 'Search complete. Enter another phrase to search')

            except Exception:
                log.exception(message.text)
                await message.answer('Oops! Something went wrong. Please try again later.')

            queue.task_done()


async def main():
    loop = asyncio.get_event_loop()
    _ = loop.create_task(process_queue())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG,
    )
    asyncio.run(main())
