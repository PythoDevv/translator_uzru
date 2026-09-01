"""Asinxron va barqaror tarjima xizmati.

`translate` paketi MyMemory xizmatidan foydalanadi va uning kunlik kvotasi juda
kichik. Bu modul Google Translate endpointidan foydalanadi. Production yuklama
uchun `.env` ga GOOGLE_TRANSLATE_API_KEY qo'yilsa, rasmiy Google Cloud
Translation API ishlatiladi; aks holda bepul Google endpointi ishlatiladi.
"""

import asyncio
import logging
import re
import time
from html import unescape
from collections import OrderedDict
from typing import Optional, Tuple

import aiohttp

from data.config import GOOGLE_TRANSLATE_API_KEY


class TranslationError(Exception):
    """Tarjima provayderi vaqtincha javob bermaganda ko'tariladi."""


class TranslationService:
    MAX_INPUT_LENGTH = 4_500
    MOBILE_CHUNK_LENGTH = 1_800
    CACHE_TTL_SECONDS = 3_600
    CACHE_SIZE = 2_000

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: "OrderedDict[Tuple[str, str, str], Tuple[float, str]]" = OrderedDict()
        self._semaphore = asyncio.Semaphore(8)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def translate(self, text: str, source_language: str, target_language: str) -> str:
        if not text or not text.strip():
            return text
        if len(text) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"Matn {self.MAX_INPUT_LENGTH} belgidan oshmasligi kerak")
        if source_language == target_language:
            return text

        key = (text, source_language, target_language)
        cached = self._cache.get(key)
        if cached and time.monotonic() - cached[0] < self.CACHE_TTL_SECONDS:
            self._cache.move_to_end(key)
            return cached[1]
        if cached:
            del self._cache[key]

        async with self._semaphore:
            translated = await self._request_with_retry(text, source_language, target_language)

        self._cache[key] = (time.monotonic(), translated)
        self._cache.move_to_end(key)
        while len(self._cache) > self.CACHE_SIZE:
            self._cache.popitem(last=False)
        return translated

    async def _request_with_retry(self, text: str, source: str, target: str) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(2):
            try:
                return await self._request(text, source, target)
            except (aiohttp.ClientError, asyncio.TimeoutError, TranslationError) as error:
                last_error = error
                if attempt == 0:
                    await asyncio.sleep(0.5)
        logging.warning("Translation provider failed: %s", last_error)
        raise TranslationError("Tarjima xizmati vaqtincha ishlamayapti") from last_error

    async def _request(self, text: str, source: str, target: str) -> str:
        session = await self._get_session()
        timeout = aiohttp.ClientTimeout(total=12)
        if GOOGLE_TRANSLATE_API_KEY:
            endpoint = "https://translation.googleapis.com/language/translate/v2"
            payload = {"q": text, "source": source, "target": target, "format": "text"}
            params = {"key": GOOGLE_TRANSLATE_API_KEY}
            async with session.post(endpoint, params=params, json=payload, timeout=timeout) as response:
                data = await self._json_or_error(response)
                return unescape(data["data"]["translations"][0]["translatedText"])

        # Google'ning mobil sahifasi MyMemory'ning qat'iy kunlik kvotasiga
        # bog'liq emas. Rasmiy API kaliti bo'lsa yuqoridagi yo'l ishlatiladi.
        chunks = self._split_text(text, self.MOBILE_CHUNK_LENGTH)
        translated_chunks = []
        for chunk in chunks:
            params = {"sl": source, "tl": target, "q": chunk}
            async with session.get("https://translate.google.com/m", params=params, timeout=timeout) as response:
                if response.status != 200:
                    details = (await response.text())[:300]
                    raise TranslationError(f"HTTP {response.status}: {details}")
                page = await response.text()
            match = re.search(r'<div class="result-container">(.*?)</div>', page, re.DOTALL)
            if not match:
                raise TranslationError("Tarjima javobi noto'g'ri formatda")
            translated_chunks.append(unescape(match.group(1)).replace('<br>', '\n'))
        return "".join(translated_chunks)

    @staticmethod
    def _split_text(text: str, limit: int):
        if len(text) <= limit:
            return [text]
        chunks = []
        remaining = text
        while len(remaining) > limit:
            split_at = max(remaining.rfind('\n', 0, limit), remaining.rfind(' ', 0, limit))
            if split_at <= 0:
                split_at = limit
            else:
                split_at += 1
            chunks.append(remaining[:split_at])
            remaining = remaining[split_at:]
        chunks.append(remaining)
        return chunks

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    @staticmethod
    async def _json_or_error(response: aiohttp.ClientResponse):
        if response.status != 200:
            details = (await response.text())[:300]
            raise TranslationError(f"HTTP {response.status}: {details}")
        try:
            return await response.json(content_type=None)
        except aiohttp.ContentTypeError as error:
            raise TranslationError("Tarjima xizmati JSON qaytarmadi") from error


translation_service = TranslationService()


async def translate_text(text: str, source_language: str, target_language: str) -> str:
    return await translation_service.translate(text, source_language, target_language)


async def close_translation_service() -> None:
    await translation_service.close()
