import zlib
import binascii


f = open('_chr_coach_r0030_a1.iff\\chr_coach_r0030_a1.TXTR', 'rb')
data = f.read()
f.close()

crc = zlib.crc32(data, 0xdebb20e3)
bcrc = binascii.crc32(data)
print hex(crc ^ 0xFFFFFFFF), hex(bcrc & 0xFFFFFFFF)
