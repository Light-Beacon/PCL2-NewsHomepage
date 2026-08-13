import requests
from queue import Queue
from datetime import datetime, timedelta
from typing import TypedDict, Literal, TypeAlias
from homepagebuilder.interfaces import script

API_URL = "https://www.mcstate.net/api/mojang-status"
QUEUE_MAX_SIZE = 3

GREEN_COLOR = "#41D041"
YELLOW_COLOR = "#D1A041"
RED_COLOR = "#D14241"
GRAY_COLOR = "#888888"

StatusState: TypeAlias = Literal['up', 'down', 'unknown']
class StatusDetials(TypedDict):
    session: StatusState = "unknown"
    accounts: StatusState = "unknown"
    microsoft: StatusState = "unknown"
    api: StatusState = "unknown"
    textures: StatusState = "unknown"
    website: StatusState = "unknown"

class StatusRecord(TypedDict):
    status: StatusDetials
    check_time: datetime = datetime.min

CHECK_TIME: datetime = datetime.now()
UPDATE_INTERVAL = 150
UPDATE_TIME = datetime.min
STATUS_RECORDS: Queue[StatusRecord | None] = Queue(maxsize=QUEUE_MAX_SIZE)
CALCULATED_STATUS_CACHE: StatusRecord = None

def get_status():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response as a dictionary
    except requests.RequestException as e:
        print(f"Error fetching Mojang status: {e}")
        return None

def get_service_status(status_dict, service_id):
    return next((service['status'] for service in status_dict['services'] if service['id'] == service_id), 'unknown')

def update_status():
    global UPDATE_TIME, CALCULATED_STATUS_CACHE
    result = get_status()
    status: StatusRecord = {'status': StatusDetials()}
    if result is not None:
        status['status']['session'] = get_service_status(result, 'session')
        status['status']['accounts'] = get_service_status(result, 'accounts')
        status['status']['microsoft'] = get_service_status(result, 'microsoft')
        status['status']['api'] = get_service_status(result, 'api')
        status['status']['textures'] = get_service_status(result, 'textures')
        status['status']['website'] = get_service_status(result, 'website')
        status['check_time'] = datetime.strptime(result.get('checkedAt'), "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
    if STATUS_RECORDS.full():
        STATUS_RECORDS.get()
    STATUS_RECORDS.put(status)
    UPDATE_TIME = datetime.now()
    CALCULATED_STATUS_CACHE = None

def should_update_status():
    global UPDATE_TIME
    return (datetime.now() - UPDATE_TIME).total_seconds() >= UPDATE_INTERVAL

def get_calculated_status():
    global CALCULATED_STATUS_CACHE, STATUS_RECORDS
    if CALCULATED_STATUS_CACHE is not None:
        return CALCULATED_STATUS_CACHE
    status: StatusRecord = StatusRecord()
    status['status'] = StatusDetials()
    for item in STATUS_RECORDS.queue:
        if item is None:
            continue
        for key, value in item['status'].items():
            if key == 'check_time':
                continue
            if value == 'down' and status.get(key) != 'up':
                status['status'][key] = 'down'
            elif value == 'up':
                status['status'][key] = 'up'
    status['check_time'] = max((item['check_time'] for item in STATUS_RECORDS.queue if item is not None), default=datetime.min)
    return status
        

def get_mojang_major_status():
    status = get_calculated_status()['status']
    if all(value == 'unknown' for value in status.values()):
        return "未知"
    if status['api'] == 'down' or status['session'] == 'down' or status['microsoft'] == 'down':
        return "异常"
    elif status['accounts'] == 'down' or status['textures'] == 'down' or status['website'] == 'down':
        return "问题"
    else:
        return "正常"

@script('MojangStatusText')
def mojang_status_text(name, **_):
    if should_update_status():
        update_status()
    status = get_calculated_status()['status'].get(name, 'unknown')
    if status == 'up':
        return "正常"
    elif status == 'down':
        return "异常"
    else:
        return "未知"

@script('MojangMajorStatusText')
def mojang_major_status_text(**_):
    if should_update_status():
        update_status()
    return get_mojang_major_status()

@script('MojangStatusColor')
def mojang_status_color(name, **_):
    if should_update_status():
        update_status()
    status = get_calculated_status()['status'].get(name, 'unknown')
    if status == 'up':
        return GREEN_COLOR
    elif status == 'down':
        return RED_COLOR
    else:
        return GRAY_COLOR

@script('MojangMajorStatusColor')
def mojang_major_status_color(**_):
    if should_update_status():
        update_status()
    major_status = get_mojang_major_status()
    if major_status == "正常":
        return GREEN_COLOR
    elif major_status == "异常":
        return RED_COLOR
    elif major_status == "问题":
        return YELLOW_COLOR 
    else:
        return GRAY_COLOR


@script('MojangStatusTime')
def mojang_status_time(**_):
    return get_calculated_status()['check_time'].strftime("%Y年%m月%d日 %H:%M")

@script('MojangStatusTimeCompressed')
def mojang_status_time(**_):
    return get_calculated_status()['check_time'].strftime("%H:%M")

@script('MojangStatusCardReference')
def mojang_status(**_):
    status = get_mojang_major_status()
    if status == "异常":
        return "MojangStatusDetail"
    else:
        return "MojangStatusCompress"