"""
获取在展示期内的所有卡片的列表
"""
import datetime
import re
from homepagebuilder.interfaces import script, Logger

LOGGER = Logger('NewsList')
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

def strptime(date_str):
    """将字符串转换为datetime对象"""
    if not date_str:
        return None
    if isinstance(date_str, datetime.datetime):
        return date_str
    try:
        return datetime.datetime.strptime(date_str, TIME_FORMAT)
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            LOGGER.warning("无法解析日期字符串: %s", date_str)
            return None

DELTA_PATTEN = re.compile(r'(?P<weeks>\d+w)?\s*(?P<days>\d+d)?\s*(?P<hours>\d+h)?\s*(?P<minutes>\d+m)?\s*(?P<seconds>\d+s)?')

def strpdelta(time_str):
    """将字符串转换为datetime对象"""
    match = DELTA_PATTEN.match(time_str)
    if not match:
        return None
    weeks = int(match.group('weeks')[:-1]) if match.group('weeks') else 0
    days = int(match.group('days')[:-1]) if match.group('days') else 0
    hours = int(match.group('hours')[:-1]) if match.group('hours') else 0
    minutes = int(match.group('minutes')[:-1]) if match.group('minutes') else 0
    seconds = int(match.group('seconds')[:-1]) if match.group('seconds') else 0
    return datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

@script('NewsList')
def news_list(context,**_):
    cardlist = []
    now = datetime.datetime.now()
    for card in context.project.get_all_card():
        card_name = card.get('card_id')
        disptime = card.get('display_time')
        hidetime = card.get('hide_time')
        timespan = card.get('display_span')
        expired = True
        disptime = strptime(disptime)
        hidetime = strptime(hidetime)
        timespan = strpdelta(timespan) if timespan else datetime.timedelta(seconds=0)
        if hidetime and now < hidetime:
            expired = False
            cardlist.append(card['card_id'])
        elif disptime and now < disptime + timespan:
            expired = False
            cardlist.append(card['card_id'])
        if disptime or hidetime:
            LOGGER.debug("%s [%s-%s][%s][%s]",
                card_name, disptime, hidetime, timespan, 'EXPIRED' if expired else 'VAILD')
    return str.join(';', cardlist)
