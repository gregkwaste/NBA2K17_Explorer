#-------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      gregkwaste
#
# Created:     14/10/2014
# Copyright:   (c) gregkwaste 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------
import struct


def read_string(f):
    c = ''
    for i in range(128):
        s = struct.unpack('B', f.read(1))[0]
        if not s:
            return c
        else:
            c += chr(s)


f = open('I:\\GameInstalls\\NBA 2K16\\0A', 'rb')


f.seek(16)
arch_num = struct.unpack('<I', f.read(4))[0]
f.read(12)
item_num = struct.unpack('<I', f.read(4))[0]
f.read(12)
print(arch_num, item_num)
s = 0
sizes = []
for i in range(arch_num):
    size = struct.unpack('<Q', f.read(8))[0]
    f.read(8)
    name = read_string(f)
    f.read(13 + 16)
    print(name, hex(size), f.tell())
    sizes.append(s)
    s += size


file_list = []
for i in range(item_num):
    sa = struct.unpack('<Q', f.read(8))[0]
    id0 = struct.unpack('<I', f.read(4))[0]
    sb = struct.unpack('<I', f.read(4))[0]
    id1 = struct.unpack('<Q', f.read(8))[0]
    # t=struct.unpack('<I',f.read(4))[0]
    file_list.append((sa, id0, sb, id1))

f.close()

id = 0
id0 = 1000000000
# s=1000000000
index = 0
for i in range(item_num):
    if file_list[i][3] == 50890150:
        print(file_list[i])
    if file_list[i][2] > id:
        id = file_list[i][2]

print('Max ID: ', id)
print(file_list[index], index)
