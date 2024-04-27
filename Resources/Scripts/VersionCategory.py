from Core.Project import Project
from Core.Debug import LogWarning, LogInfo
from Core.ModuleManager import invokeModule, untilLoaded
import requests
import json

untilLoaded('FetchMainfest')
MANIFSET = invokeModule('FetchMainfest','fetch')()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

def script(cat_name,proj:Project,**kwargs):
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), proj.getAllCard()))
    cardrefs = [card['card_id'] for card in cards]
    cardrefs.sort(key=lambda ver:ID_LIST.index(ver.split(':')[1]))
    return str.join(';',cardrefs)