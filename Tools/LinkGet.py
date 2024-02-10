import json
def trans(froms,key,dest):
    mapping = {}
    for file in froms:
        with open(file,'r') as f:
            for item in json.load(f)['cards']:
                mapping.update({item['name']:item[key]})
    with open(dest,'w') as f:            
        json.dump(mapping,f)