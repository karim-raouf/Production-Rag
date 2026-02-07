from fastapi import Body

# from loguru import logger
from ..schemas import TextToTextRequest
from .service import extract_urls, fetch_all
import logging


async def fetch_urls_content(prompt: str):
    try:
        urls = extract_urls(prompt)
        content = await fetch_all(urls)
        return content
    except Exception as e:
        logging.error(f"Error fetching URLs: {e}")
        return None


async def get_urls_content(body: TextToTextRequest = Body(...)):
    return await fetch_urls_content(body.prompt)
