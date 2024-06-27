from Interfaces import script

@script('SeparatorContent')
def script(card,**_):
    content = card['content']
    return '  '.join(list(content))
