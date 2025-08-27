from homepagebuilder.interfaces import require, script

pref_module = require('homepage_preference')
PREFERENCE_MANAGER = pref_module.PreferenceManager
is_true = pref_module.is_true
PREFERENCE_LIST_LENGTH = PREFERENCE_MANAGER.pref_length()
GET_DOMAIN_URL = require('domain').get_doamin_url

def get_url(context, location, domain = None):
    if domain:
        return domain + location
    else:
        return GET_DOMAIN_URL(context) + location

def get_page_link(page_name, context, domain = None, *_args, **kwargs):
    settings:dict = context.setter.toProperties().get('args',{})
    settings_length = len(settings)
    if settings_length == 0:
        return get_url(context, page_name, domain)
    new_args = []
    # 判断优化： 取长度小的遍历
    if PREFERENCE_LIST_LENGTH > len(settings):
        for name, value in settings.items():
            if PREFERENCE_MANAGER.has(name):
                if is_true(value):
                    new_args.append(name)
                else:
                    new_args.append(name + '=' + value)
    else:
        for entry in PREFERENCE_MANAGER.get_entries():
            if value := settings.get(entry.name, None) is not None:
                if is_true(value):
                    new_args.append(entry.name)
                else:
                    new_args.append(entry.name + '=' + value)
    if len(new_args) == 0:
        return get_url(context, page_name, domain)
    if '?' not in page_name:
        page_name += '?'
    else:
        page_name += '&amp;'
    return get_url(context,  page_name + '&amp;'.join(new_args) , domain)

@script('XamlLink')
def link_script(page_name, domain=None, *_args, **kwargs):
    context = kwargs['context']
    return get_page_link(page_name, context, domain)

@script('Link')
def link_script(page_name, domain=None, *_args, **kwargs):
    context = kwargs['context']
    if '.json' not in page_name:
        page_name += '.json'
    return get_page_link(page_name, context, domain)