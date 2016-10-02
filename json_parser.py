#import simplejson as json
import json
import collections
from StringIO import StringIO


def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    count = 0
    d = collections.OrderedDict()
    for k, v in ordered_pairs:
        if k in d:
            d[k + '_dupl_' + str(count)] = v
            count += 1
        else:
            d[k] = v
    return d


def NbaJsonParser(data):
    model_name = data.split('\n')[0].split(':')[0]
    # print(model_name)
    data = data[(len(model_name) + 2):]  # Keep it like that
    # Fix the json formatting before parsing
    data = data.replace('\r\n', '\n')
    data = data.replace(": \n", ': "None"\n')
    data = data.replace(": ,\n", ': "None",\n')
    data = data.replace(" .", '0.')
    data = data.replace("-.", '-0.')
    mid = "\"Binary\":"
    split = data.split("\"Mathnode\":")
    # print split[1]
    # print split[1].split("{")
    print len(split)
    if not len(split) == 1:
        tail = '{' + ''.join(split[1].split("{")[0:2])
        tail += mid + '{' + '{'.join(split[1].split("{")[2:])
        data = split[0] + "\"Mathnode\":" + tail
    # data=split[0]+split[1]
    # data = json.loads(data, parse_float=False,
    # strict=False,object_pairs_hook=collections.OrderedDict)  # Parsing the
    # json
    data = json.loads(data, parse_float=False, strict=False,
                      object_pairs_hook=dict_raise_on_duplicates)  # Parsing the json
    return data

#f = open('temp', 'rb')
#data = f.read()
# f.close()
# t = StringIO()
# t.write(data)
# t.seek(0)
# NbaJsonParser('temp_scne')
# data = NbaJsonParser(t)
# print data

if __name__ == '__main__':
    f=open(r"J:\Projects\NBA2K16 Explorer\temp\_png1413.iff\hihead.SCNExml",'r')
    data = f.read()
    print NbaJsonParser(data)
    f.close()
