import requests
import json
from homepagebuilder.interfaces import script, Logger

logger = Logger("TranslationScript")

response = requests.get('https://raw.githubusercontent.com/Light-Beacon/Minecraft-ZH-Translation-Sheet/refs/heads/main/data/translations.json', 
                        timeout=10)
response_content = response.content
translations = json.loads(response_content)
logger.info("加载中文翻译数据成功, 共计 %d 条翻译", len(translations))

@script('name')
def translate(*args, **_):
    if not args:
        return ''
    name = args[0]
    if len(args) == 2:
        fallback = args[1]
    else:
        fallback = name
    return translations.get(name.lower(), fallback)
