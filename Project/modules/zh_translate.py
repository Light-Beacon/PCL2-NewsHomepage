import requests
import json
from homepagebuilder.interfaces import script, Logger
from homepagebuilder.core.config import config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homepagebuilder.core.types import Context
    
logger = Logger("TranslationScript")
TRANSLATIONS = {}

@script('name')
def translate(*args, **_):
    if not args:
        return ''
    name = args[0]
    if len(args) == 2:
        fallback = args[1]
    else:
        fallback = name
    return TRANSLATIONS.get(name.lower(), fallback)

def fetch_transltions():
    logger.info("正在加载中文翻译")
    try:
        response = requests.get('https://raw.githubusercontent.com/Light-Beacon/Minecraft-ZH-Translation-Sheet/refs/heads/main/data/translations.json', 
                        timeout=10)
    except ConnectionError:
        logger.warning("无法加载中文翻译")
        return {}
    response_content = response.content
    return json.loads(response_content)

def init(context:'Context', *args, **kwargs):
    global TRANSLATIONS
    if config('NewsHomepage.Translation.UseReloadCache', config('NewsHomepage.Debug')):
        if translations_manifset_cache := context.builder.get_data('translation_manifset_cache'):
            TRANSLATIONS = translations_manifset_cache
            logger.info("从缓存中加载中文翻译数据成功, 共计 %d 条翻译", len(TRANSLATIONS))
            return
    TRANSLATIONS = fetch_transltions()
    logger.info("加载中文翻译数据成功, 共计 %d 条翻译", len(TRANSLATIONS))
    context.builder.set_data('translation_manifset_cache', TRANSLATIONS)