import asyncio
import html

from translate import Translator


async def translate_text(text: str, source_language: str, target_language: str) -> str:
    """Translate text without blocking aiogram's event loop."""
    loop = asyncio.get_running_loop()
    translator = Translator(from_lang=source_language, to_lang=target_language)
    translated = await asyncio.wait_for(
        loop.run_in_executor(None, translator.translate, text),
        timeout=15,
    )
    return html.unescape(translated)
