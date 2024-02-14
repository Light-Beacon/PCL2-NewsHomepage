def script(card,arg,res):
    name = card['version-id']
    return res.data[f'{arg[1]}Link'][name]