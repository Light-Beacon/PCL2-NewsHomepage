"""
生成官网链接
"""

import re
from homepagebuilder.interfaces import script
from homepagebuilder.core.formatter import format_code

SNAPSHOT_PATTERN = re.compile(r'^[0-9]{2}[w|W][0-9]{2}[A-Fa-f]$')
NEW_SNAPSHOT_PATTERN = re.compile(r'^[0-9]{2}(\.[0-9]+)*-snapshot-[0-9]+$')
PRE_RELEASE_PATTERN = re.compile(r'^.*-pre[0-9]+$')
RELEASE_CANDIDATE_PATTERN = re.compile(r'^.*-rc[0-9]+$')
RELEASE_PATTERN = re.compile(r'^1\.[0-9]+(\.[0-9]+)?$')

def gen_official_link(vid:str):
    '''生成官网链接'''
    if re.match(SNAPSHOT_PATTERN,vid):
        return f'https://minecraft.net/article/minecraft-snapshot-{vid.lower()}'
    if re.match(NEW_SNAPSHOT_PATTERN,vid):
        return f'https://minecraft.net/article/minecraft-{vid.replace(".","-")}'
    if re.match(PRE_RELEASE_PATTERN,vid):
        version,sub=vid.split('-pre')
        return f'https://minecraft.net/article/minecraft-{version.replace(".","-")}-pre-release-{sub}'
    if re.match(RELEASE_CANDIDATE_PATTERN,vid):
        version,sub=vid.split('-rc')
        return f'https://minecraft.net/article/minecraft-{version.replace(".","-")}-release-candidate-{sub}'
    if re.match(RELEASE_PATTERN,vid):
        return f'https://minecraft.net/article/minecraft-java-edition-{vid.replace(".","-")}'
    return ''

@script('GetLink')
def get_link(link_type,link_key=None,**kwargs):
    card = kwargs['card']
    context = kwargs['context']
    name:str = card['version-id']
    if card.get('wip') == 'true' and link_type != 'Official':
        return ''
    data = context.data[f'{link_type}Link']
    if link_key:
        return data[link_key]
    name = format_code(name,card,context)
    if link_type == 'Official' and name not in data:
        return gen_official_link(name)
    result = data.get(name)
    return result if result else ""
