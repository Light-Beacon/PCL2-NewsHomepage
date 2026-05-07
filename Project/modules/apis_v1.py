"""
新的 RESTful API
"""

import json

from homepagebuilder.interfaces import require
from homepagebuilder.interfaces.Events import on
from homepagebuilder.core.types import Context
from homepagebuilder.core.logger import Logger
from typing import NamedTuple
import time

mcv = require('minecraft_versions')  # 需求前置 MinecraftVersions
MCVM = mcv.MCVM

rest_apis_routes = []

logger = Logger('API')

# region API Routes

def api(path, version=None, methods=None):
    if version is None:
        version = 'v1'
    if methods is None:
        methods = ['GET']
    if path[0] != '/':
        path = '/' + path
    def deco(cls):
        api_object = cls()
        rest_apis_routes.append((f'/{version}{path}', f'api.{version}.{cls.__name__}',
                          api_object.generate, methods))
    return deco

@on('project.import.return')
def set_up_routes(*_, **__):
    app = Context.get_current_context().flask_app
    if not app:
        return
    exist_endpoints = app.view_functions.keys()
    for route in rest_apis_routes:
        if route[1] in exist_endpoints:
            app.view_functions[route[1]] = route[2]
        else:
            app.add_url_rule('/api' + route[0], route[1], route[2], methods=route[3])
    logger.debug('routes setuped')

# endregion

def is_true(string: str) -> bool:
    return bool(string and isinstance(string, str) and string.lower() != 'false')

# region Error Classes

class APIError(Exception):
    message = 'Generic Error'
    _code = 0

    def __init__(self, message):
        self.message = message

    @property
    def code(self):
        return self._code

    def to_response(self):
        return Response(message=self.message, status=self._code)

class BadRequest(APIError):
    _code = 400

class Unauthorized(APIError):
    _code = 401

class Forbidden(APIError):
    _code = 403

class NotFound(APIError):
    _code = 404

class InternalServerError(APIError):
    _code = 500

# endregion

class RESTAPI:
    def process(self, **kwargs) -> tuple[str, dict|list]|str|dict|list:
        raise NotImplementedError()

    def generate(self, **kwargs):
        from flask import request, Response as Flask_Response
        response = None
        args = request.args
        try:
            result = self.process(args = args, **kwargs)
            if isinstance(result, Response):
                response = result
            elif isinstance(result, dict | list | str):
                response = Response(data = result)
            elif isinstance(result, int):
                if 200 <= result < 600:
                    response = Response(status = result)
                else:
                    response = Response(data = str(result))
            else:
                raise InternalServerError("")
        except APIError as e:
            response = e.to_response()
        except Exception as e:
            response = Response(message = "Internal Server Error",
                                error = {
                                    "type": e.__class__.__name__,
                                    "args": e.args,
                                },
                                status = 500)
        respond:dict = {'status': response.status,
                   'message': response.message}
        if response.data:
            respond['data'] = response.data
        if response.error:
            respond['error'] = response.error
        ensure_ascii = is_true(args.get('ascii', 'false'))
        respond_json = json.dumps(respond, ensure_ascii=ensure_ascii)
        return Flask_Response(respond_json, status=response.status, mimetype='application/json' )

class Response(NamedTuple):
    data: dict | list | str | None = None
    message: str = ''
    status: int = 200
    error: dict | None = None


@api('/status', 'v1')
class StatusAPI(RESTAPI):
    def process(self, **_):
        return Response(message='OK')


@api('/mcversion/latest/data', 'v1')
class LatestVersionAPI(RESTAPI):

    EXPORT_VERSION_PROPERTIES = [
        'version-id',
        'version-type',
        'version-type-id',
        'title',
        'intro',
        'version-image-link',
        'server-jar',
        'translator',
        'official-link',
        'wiki-link',
        'wip',
    ]

    def __init__(self):
        self.respond = None
        self.__inited = False

    def init(self):
        context = Context.get_current_context()
        library = context.project.base_library
        self.latest_release = library.get_card(MCVM.get_latest_version('release').id, False)
        if latest_developing := MCVM.get_latest_version('development'):
            self.latest_developing = library.get_card(latest_developing.id, False)
        else:
            self.latest_developing = None
        self.__inited = True


    def generate_respond(self):
        if not self.__inited:
            self.init()
        respond = {}
        if self.latest_developing:
            respond['snapshot'] = self.extract_version_info(self.latest_developing)
        respond['release'] = self.extract_version_info(self.latest_release)
        respond['cache-time'] = time.time()
        self.respond = respond

    def extract_version_info(self, card):
        respond = {}
        context = Context.get_current_context()
        expended_card = context.builder.template_manager.expend_card_placeholders(card, '')
        for key in self.EXPORT_VERSION_PROPERTIES:
            respond[key] = expended_card.get(key)
        respond['homepage-json-link'] = f"https://news.bugjump.net/VersionDetail.json?ver={expended_card['version-id']}"
        return respond

    def process(self, **_):
        if not self.respond:
            self.generate_respond()
        return Response(data = self.respond)

@api('/mcversion/latest/card', 'v1')
class LatestVersionCardAPI(RESTAPI):
    def process(self, **_):
        context = Context.get_current_context()
        library = context.project.base_library
        setter = context.setter
        card = library.get_card('VersionLatestListCard', False)
        card = setter.decorate(card)
        return Response(data = context.builder.template_manager.build(card))

@api('/mcversion/version/<version_id>', 'v1')
class MCVersionDataAPI(RESTAPI):

    EXPORT_VERSION_PROPERTIES = [
        'version-id',
        'version-type',
        'version-type-id',
        'title',
        'intro',
        'version-image-link',
        'server-jar',
        'translator',
        'official-link',
        'wiki-link',
        'markdown',
        'wip'
    ]

    def process(self, version_id, **_):
        context = Context.get_current_context()
        library = context.project.base_library
        card = library.get_card(version_id, False)
        if not card:
            raise NotFound(f"Version {version_id} not found")
        respond = {}
        expended_card = context.builder.template_manager.expend_card_placeholders(card, '')
        for key in self.EXPORT_VERSION_PROPERTIES:
            respond[key] = expended_card.get(key)
        return Response(data = respond)

@api('/mcversion/list', 'v1')
class MCVersionListAPI(RESTAPI):
    _cache = None
    def get_list(self):
        context = Context.get_current_context()
        base_library = context.project.base_library
        assert base_library is not None
        version_lib = base_library.get_library('versions')
        result = [c["file_name"] for c in version_lib.get_all_cards()]
        return Response(data = result)

    def process(self, **_):
        if self._cache is None:
            self._cache = self.get_list()
        return self._cache

@api('/<path:path>')
class DefaultNotFoundAPI(RESTAPI):
    def process(self, **_):
        raise NotFound("")