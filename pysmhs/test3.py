from config.configobj import ConfigObj

config = ConfigObj('config/newactions.txt', indent_type='\t')
actionlist = {}
events = [
    {'tag': 'plchandler_vkcVan4', 'value': 'mama1'},
    {'tag': 'plchandler_vkcVan4', 'value': 'mama2'},
    {'tag': 'plchandler_vkcKyh', 'value': 'mama3'}
]
tags = {}
for event in events:
    tags[event['tag']] = event['value']
for name, params in config.items():
    actionlist[params['condition']] = params['actions']
print tags
print actionlist

print '--------'
for cond in actionlist.keys():
    if any(tag in cond for tag in tags.keys()):
        print cond
