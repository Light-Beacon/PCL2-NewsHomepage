from homepagebuilder.interfaces import page_class_handles, require
from homepagebuilder.core.page import CodeBasedPage
import json

def get_args(context):
    if setter := context.setter:
        return setter.override
    return {}

def is_true(string:str):
    return string and isinstance(string,str) and string.lower() != 'false'
    
@page_class_handles('apis/status')
class StatusPage(CodeBasedPage):

    @property
    def display_name(self):
        return 'api/status'

    def generate(self, *args, **kwargs):
        return 'ok'

    def get_content_type(self, setter):
        return 'text/plain'

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
latest_version = mcv.get_latest()

@page_class_handles('apis/versions/latest')
class LatestVersionAPI(CodeBasedPage):

    def __init__(self, project):
        super().__init__(project)
        self.latest_release = self.project.base_library.get_card(mcv.get_latest('release'),False)
        if latest_snap_shot_id := mcv.get_latest('snapshot'):
            self.latest_snapshot = self.project.base_library.get_card(latest_snap_shot_id,False)
        else:
            self.latest_snapshot = None
        self.respond = None
    
    @property
    def display_name(self):
        return 'api/versions/latest'
    
    def pregen_respond(self):
        respond = {}
        if self.latest_snapshot:
            respond['snapshot'] = self.extract_version_info(self.latest_snapshot)
        respond['release'] = self.extract_version_info(self.latest_release) 
        self.respond = respond
    
    def extract_version_info(self,card):
        respond = {}
        expendedcard = self.project.template_manager.expend_card_placeholders(card,'')
        self.copyinfo(respond,expendedcard,'version-type')
        self.copyinfo(respond,expendedcard,'intro')
        self.copyinfo(respond,expendedcard,'version-image-link')
        self.copyinfo(respond,expendedcard,'server-jar')
        self.copyinfo(respond,expendedcard,'translator')
        self.copyinfo(respond,expendedcard,'official-link')
        self.copyinfo(respond,expendedcard,'wiki-link')
        self.copyinfo(respond,expendedcard,'version-id')
        self.copyinfo(respond,expendedcard,'title')
        respond['homepage-json-link'] = f"https://news.bugjump.net/VersionDetail.json?ver={expendedcard['version-id']}"
        return respond
    
    def copyinfo(self,respond,card,key):
        respond[key] = card.get(key)

    def generate(self, context):
        args = get_args(context)
        ensure_ascii = is_true(args.get('ascii',False))
        if not self.respond:
            self.pregen_respond()
        return json.dumps(self.respond,ensure_ascii=ensure_ascii)
    
    def get_content_type(self, setter):
        return 'application/json'
    
@page_class_handles('apis/versions/latest-card')
class LatestVersionCardAPI(CodeBasedPage):
    def generate(self, context):
        setter = context.setter
        card = self.project.base_library.get_card('VersionLatestListCard', False)
        card = setter.decorate(card)
        return self.project.template_manager.build(card)
