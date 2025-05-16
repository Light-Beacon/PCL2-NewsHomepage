"""
向 MARKDOWN 解析器注册开发者注释类型
"""

from homepagebuilder.interfaces import require
markdown_parsers = require('markdown_parsers')
markdown_parsers.QUOTE_TYPE_NAMES["devnote"] = '开发者注释'
