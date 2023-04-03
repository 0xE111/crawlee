import asyncio
import logging
import re
from functools import wraps

import click

from parsers.telegraph import TelegraphParser

log = logging.getLogger(__name__)


def as_sync(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument('search-term')
@click.option('--text-contains')
@click.option('--html-contains')
@click.option('--limit', type=int)
@click.option('--log-level', type=click.Choice(logging._nameToLevel.keys()), default='INFO')
@click.option('--out-format', type=click.Choice(['text', 'jsonl', 'url', 'mute']), default='text')
@as_sync
async def main(
    search_term: str,
    text_contains: str | None,
    html_contains: str | None,
    limit: int | None,
    log_level: str,
    out_format: str,
):
    logging.basicConfig(level=logging.getLevelName(log_level))

    re_text_contains = text_contains and re.compile(text_contains)
    re_html_contains = html_contains and re.compile(html_contains)

    pages_found, pages_matched = 0, 0
    async with TelegraphParser() as telegraph:
        async for page in telegraph.iter_pages(search_term=search_term, limit=limit):
            pages_found += 1

            if re_text_contains and not re_text_contains.search(page.plain_text):
                continue
            if re_html_contains and not re_html_contains.search(page.html):
                continue

            pages_matched += 1
            match out_format:
                case 'text':
                    print(pages_found, page.as_text())
                    print('-' * 30)
                case 'jsonl':
                    print(page.as_json())
                case 'url':
                    print(page.url)
                case 'mute':
                    pass
                case _:
                    raise ValueError(f'Unknown out_format: {out_format}')

    log.info('Found %s pages, matched %s pages', pages_found, pages_matched)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
