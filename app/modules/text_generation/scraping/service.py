import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup

# from loguru import logger
import logging


def extract_urls(prompt: str) -> list[str]:
    url_pattern = r"(?P<url>https?:\/\/[^\s]+)"
    urls = re.findall(url_pattern, prompt)
    return urls


def parse_inner_text(html_string: str):
    soup = BeautifulSoup(html_string, "lxml")

    if content := soup.find("article"):
        return content.get_text(seperator=" ", strip=True)

    if content := soup.find("main"):
        return content.get_text(seperator=" ", strip=True)

    common_ids = ["bodyContent", "content", "main-content", "post-body", "app"]
    for div_id in common_ids:
        if content := soup.find("div", id=div_id):
            return content.get_text(seperator=" ", strip=True)

    if paragraphs := soup.find_all("p"):
        return "\n".join([p.get_text(strip=True) for p in paragraphs])

    logging.warning("Could not parse the HTML content")
    return ""


async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        html_string = await response.text()
        return parse_inner_text(html_string)


async def fetch_all(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[fetch(session, url) for url in urls], return_exceptions=True
        )

    success_result = [result for result in results if isinstance(result, str)]

    if len(success_result) != len(results):
        logging.warning("Some URLs could not be fetched")
    return "\n".join(success_result)
