import json

def getValueFromCheckbox(item):
    if len( str( item)) == 0:
        return 0
    elif item in ['True', 'False']:
        return int( json.loads(item.lower()) )
    else:
        return int(item)

