import json
def trans(froms,key,dest):
    mapping = {}
    for file in froms:
        with open(file,'r',encoding='utf-8') as f:
            for item in json.load(f)['cards']:
                mapping.update({item['name']:item[key]})
    with open(dest,'w',encoding='utf-8') as f:            
        json.dump(mapping,f,ensure_ascii=False)