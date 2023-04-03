import asyncio
import re
from dataclasses import dataclass, asdict
import json
from functools import cached_property
from itertools import product
from logging import getLogger
from typing import Any, ClassVar, Iterator

import aiohttp
from bs4 import BeautifulSoup
from transliterate import translit

log = getLogger(__name__)


@dataclass(repr=False, frozen=True, kw_only=True)
class Page:
    url: str
    html: str
    soup: BeautifulSoup

    def __str__(self) -> str:
        return self.url

    @cached_property
    def title(self) -> str:
        return self.soup.find('h1').get_text()

    @cached_property
    def plain_text(self) -> str:
        return self.soup.get_text(' ')

    @property
    def normalized_text(self) -> str:
        return re.sub(r'(\n\s*){2,}', '\n', self.plain_text)

    def as_text(self) -> str:
        return '\n'.join([
            self.title,
            self.url,
            self.normalized_text,
        ])

    def as_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class TelegraphParser:
    BASE_URL: ClassVar[str] = 'https://telegra.ph'

    session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def iter_pages(self, search_term: str, limit: int | None = None) -> Iterator[Any]:

        if not search_term.isascii():
            search_term = translit(search_term, reversed=True)
        search_term = search_term.replace(' ', '-')

        log.debug('Running search for: %s', search_term)

        tasks = [
            asyncio.create_task(self.iter_pages_for_url(url))
            for month, day in product(range(1, 13), range(1, 32))
            if (url := f'{self.BASE_URL}/{search_term}-{month:02}-{day:02}')
        ]

        num_yielded = 0
        for task in asyncio.as_completed(tasks):
            pages = await task
            for page in pages:
                yield page
                num_yielded += 1
                if limit and num_yielded >= limit:
                    break

            if limit and num_yielded >= limit:
                for task_ in tasks:
                    task_.cancel()
                break

    async def iter_pages_for_url(self, url: str) -> list[Page]:
        log.debug('Checking suffixes for %s', url)
        pages = []

        suffix_number = 1
        while True:
            suffix = f'-{suffix_number}' if suffix_number > 1 else ''
            url_with_suffix = f'{url}{suffix}'
            log.debug('Probing %s', url_with_suffix)
            async with self.session.get(url_with_suffix) as response:
                if response.status == 404:
                    break
                response.raise_for_status()
                log.debug('Found existing url %s', url_with_suffix)
                html = await response.text()

            soup = BeautifulSoup(html, features='html.parser')
            pages.append(
                Page(url=url_with_suffix, html=html, soup=soup.find('main'))
            )
            suffix_number += 1

        return pages