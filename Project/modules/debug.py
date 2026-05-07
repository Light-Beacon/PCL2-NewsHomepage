from homepagebuilder.interfaces import script, config
from homepagebuilder.core.config import is_debugging
from homepagebuilder.core.utils.event import listen_event as on, ResultOverride
from homepagebuilder.core.types.context import Context


DEBUG_MODE = config('NewsHomepage.Debug', False, bool)

@script('DebugMode')
def is_debug():
    return DEBUG_MODE

@on('server.setup_routes.return')
def set_up_routes(server, *_, **__):
    server.app.add_url_rule('/reload', "reload", reload_project, ['GET'])

def reload_project():
    if not is_debugging():
        return "Not in debug mode", 403
    context = Context.get_current_context()
    if not hasattr(context, "server_api"):
        return "Outdated builder version", 400
    if not context.server_api:
        return "Not run in server mode", 400
    try:
        context.server_api.reload_project()
        return "Success", 200
    except Exception as ex:
        return "Failed", 500