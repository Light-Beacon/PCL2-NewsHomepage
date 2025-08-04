from homepagebuilder.interfaces import require, script

pref_module = require('homepage_preference')
PREFERENCE_LIST = pref_module.PREFERENCE_LIST
PREFERENCE_LIST_LENGTH = len(PREFERENCE_LIST)
DOMAIN = pref_module.DOMAIN

@script('Link')
def link_script(page_name, context, *_args, **kwargs):
    settings:dict = context.setter.toProperties()
    settings_length = len(settings)
    if '.json' not in page_name:
        page_name += '.json'
    if settings_length == 0:
        return DOMAIN + page_name
    new_args = []
    # 判断优化： 取长度小的遍历
    if PREFERENCE_LIST_LENGTH > len(settings):
        for name, value in settings.items():
            if name in PREFERENCE_LIST:
                new_args.append(name + '=' + value)
    else:
        for name in PREFERENCE_LIST:
            if value := settings.get(name, None) is not None:
                new_args.append(name + '=' + value)
    if len(new_args) == 0:
        return DOMAIN + page_name
    if '?' not in page_name:
        page_name += '?'
    else:
        page_name += '&amp;'
    return DOMAIN + page_name + '&amp;'.join(new_args)