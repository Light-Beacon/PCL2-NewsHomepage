from homepagebuilder.interfaces import script, config, enable_by
from homepagebuilder.core.utils.event import listen_event as on, ResultOverride


DEBUG_MODE = config('NewsHomepage.Debug', False, bool)

@script('DebugMode')
def is_debug():
    return DEBUG_MODE

@on('server.get.page.start')
@enable_by(DEBUG_MODE)
def test_reload(api, alias, client, args):
    if alias != 'reload':
        return
    api.reload_project()
    raise ResultOverride({'response':'Success.',
                          'content-type':'text/plain'})