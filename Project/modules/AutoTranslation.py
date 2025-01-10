import requests
import re
from homepagebuilder.interfaces import require
from homepagebuilder.interfaces import Logger
logger= Logger('AutoTranslation')

parsers_module = require('markdown_parsers')
handles = parsers_module.handles
Text = parsers_module.Text

PATTERN = re.compile(r"<td>([a-zA-Z\d\s\-]+)</td>\s*<td>([^\(<]+)\s*</td>\s*(?:<td>(?:[^<]+)\s*</td>)?</tr>")
EXTRA_TRANSLATIONS ={
    "data value": "数据值",
    "block state": "方块状态",
    "argument": "参数",
    "parameter": "参数",
    "sprite": "精灵图",
    "variant": "变种",
    "job site": "工作站点",
    "workplace": "工作站点"
}

content = requests.get('https://zh.minecraft.wiki/w/Minecraft_Wiki:译名标准化').content.decode("utf-8")
TRANSLATIONS = {}

for en,zh in re.findall(PATTERN,content):
    en = en.lower()
    zh = zh.replace("\n","")
    if zh == '-':
        TRANSLATIONS[en] = en
    else:
        TRANSLATIONS[en] = zh
logger.info(f"译名标准化已载入 {len(TRANSLATIONS)} 条标准译名。")
TRANSLATIONS.update(EXTRA_TRANSLATIONS)

@handles('n')
class AutoText(Text):
    def convert(self):
        name = self.content
        if translation := TRANSLATIONS.get(name):
            return translation
        else:
            return f'<Italic>{name}</Italic>'