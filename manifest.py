import os

mainDirectory = 'I:\\SteamLibrary\\steamapps\\common\\NBA 2K16'
list_names = {}

file_name = os.path.join(mainDirectory, 'manifest_g')
if not os.path.exists(os.path.join(mainDirectory, 'manifest_g')):
    file_name = os.path.join(mainDirectory, 'manifest')

f = open(file_name, 'r')
for line in f.readlines():
    archname = line.split('\t')[0]
    split = line.split('\t')[1].lstrip().split(' ')
    print split
    name = split[0]
    offset = int(split[1])
    if archname not in list_names.keys():
        list_names[archname] = {}
    list_names[archname][offset] = name
f.close()
