import pylzma
from StringIO import StringIO
import sys
sys.path.append('../gk_blender_lib/modules')
from string_func import *


class zipLocalFileHeader:

    def __init__(self, data):
        self.locHeadSig = None
        self.version = struct.unpack('<H', data.read(2))[0]
        self.gPBF = struct.unpack('<H', data.read(2))[0]
        self.compMethod = struct.unpack('<H', data.read(2))[0]
        self.lMFtime = struct.unpack('<H', data.read(2))[0]
        self.lMFdate = struct.unpack('<H', data.read(2))[0]
        self.crc32 = struct.unpack('<I', data.read(4))[0]
        self.compSize = struct.unpack('<I', data.read(4))[0]
        self.decompSize = struct.unpack('<I', data.read(4))[0]
        self.fileLen = struct.unpack('<H', data.read(2))[0]
        self.extraFileLen = struct.unpack('<H', data.read(2))[0]
        # read file name
        self.name = read_string_n(data, self.fileLen)
        self.size = 30 + self.fileLen + self.extraFileLen
        # Skip extra file data
        data.seek(self.extraFileLen, 1)
        self.data = data.read(self.compSize)

    def _writeFile(self):
        t = StringIO()
        t.write(struct.pack('>I', self.locHeadSig))
        t.write(struct.pack('<H', self.version))
        t.write(struct.pack('<H', self.gPBF))
        t.write(struct.pack('<H', self.compMethod))
        t.write(struct.pack('<H', self.lMFtime))
        t.write(struct.pack('<H', self.lMFdate))
        t.write(struct.pack('<I', self.crc32))
        t.write(struct.pack('<I', self.compSize))
        t.write(struct.pack('<I', self.decompSize))
        t.write(struct.pack('<H', self.fileLen))
        t.write(struct.pack('<H', self.extraFileLen))
        # WriteName
        t.write(struct.pack(str(self.fileLen) + 's', self.name))
        t.write(self.data)

        t.seek(0)
        return t.read()


class zipCdHeader:

    def __init__(self, data):
        self.locHeadSig = None
        self.version = struct.unpack('<H', data.read(2))[0]
        self.versionNeeded = struct.unpack('<H', data.read(2))[0]
        self.gPBF = struct.unpack('<H', data.read(2))[0]
        self.compMethod = struct.unpack('<H', data.read(2))[0]
        self.lMFtime = struct.unpack('<H', data.read(2))[0]
        self.lMFdate = struct.unpack('<H', data.read(2))[0]
        self.crc32 = struct.unpack('<I', data.read(4))[0]
        self.compSize = struct.unpack('<I', data.read(4))[0]
        self.decompSize = struct.unpack('<I', data.read(4))[0]
        self.fileLen = struct.unpack('<H', data.read(2))[0]
        self.extraFileLen = struct.unpack('<H', data.read(2))[0]
        self.fileCommLen = struct.unpack('<H', data.read(2))[0]
        self.diskNumStart = struct.unpack('<H', data.read(2))[0]
        self.inFileAttr = struct.unpack('<H', data.read(2))[0]
        self.extFileAttr = struct.unpack('<I', data.read(4))[0]
        self.relOff = struct.unpack('<I', data.read(4))[0]
        self.name = read_string_n(data, self.fileLen)

        self.size = 46 + self.fileCommLen + self.extraFileLen + self.fileLen

    def _writeFile(self):
        t = StringIO()
        t.write(struct.pack('>I', self.locHeadSig))
        t.write(struct.pack('<H', self.version))
        t.write(struct.pack('<H', self.versionNeeded))
        t.write(struct.pack('<H', self.gPBF))
        t.write(struct.pack('<H', self.compMethod))
        t.write(struct.pack('<H', self.lMFtime))
        t.write(struct.pack('<H', self.lMFdate))
        t.write(struct.pack('<I', self.crc32))
        t.write(struct.pack('<I', self.compSize))
        t.write(struct.pack('<I', self.decompSize))
        t.write(struct.pack('<H', self.fileLen))
        t.write(struct.pack('<H', self.extraFileLen))
        t.write(struct.pack('<H', self.fileCommLen))
        t.write(struct.pack('<H', self.diskNumStart))
        t.write(struct.pack('<H', self.inFileAttr))
        t.write(struct.pack('<I', self.extFileAttr))
        t.write(struct.pack('<I', self.relOff))
        t.write(struct.pack(str(self.fileLen) + 's', self.name))
        t.seek(0)

        return t.read()


class zipEoDRecord:

    def __init__(self, data):
        self.locHeadSig = None
        self.diskNum = struct.unpack('<H', data.read(2))[0]
        self.diskNumStart = struct.unpack('<H', data.read(2))[0]
        self.entriesNumDisk = struct.unpack('<H', data.read(2))[0]
        self.entriesNum = struct.unpack('<H', data.read(2))[0]
        self.sizeOfCD = struct.unpack('<I', data.read(4))[0]
        self.offsetOfCD = struct.unpack('<I', data.read(4))[0]
        self.commLen = struct.unpack('<H', data.read(2))[0]
        data.seek(self.commLen, 1)

    def _writeFile(self):
        t = StringIO()
        t.write(struct.pack('>I', self.locHeadSig))
        t.write(struct.pack('<H', self.diskNum))
        t.write(struct.pack('<H', self.diskNumStart))
        t.write(struct.pack('<H', self.entriesNumDisk))
        t.write(struct.pack('<H', self.entriesNum))
        t.write(struct.pack('<I', self.sizeOfCD))
        t.write(struct.pack('<I', self.offsetOfCD))
        t.write(struct.pack('<H', self.commLen))

        t.seek(0)

        return t.read()


class customZipFile:

    def __init__(self, data):
        self.localHeaders = {}
        self.cDHeaders = {}
        self.nameList = []
        self.endOfCd = None

        # Parse File
        while True:
            magic = struct.unpack('>I', data.read(4))[0]
            if magic == 0x504B0304:
                header = zipLocalFileHeader(data)
                header.locHeadSig = magic
                # print header.name, header.compSize, header.decompSize
                # Store File
                self.nameList.append(header.name)
                self.localHeaders[header.name] = header
            elif magic == 0x504B0102:
                header = zipCdHeader(data)
                header.locHeadSig = magic
                # print header.name, header.compSize, header.decompSize
                # Store File
                self.cDHeaders[header.name] = header
            elif magic == 0x504B0506:
                self.endOfCd = zipEoDRecord(data)
                self.endOfCd.locHeadSig = magic
                break

    def _writeZip(self):
        t = StringIO()
        # Write Local Headers
        for name in self.nameList:
            t.write(self.localHeaders[name]._writeFile())
        # Write Central Directory
        for name in self.nameList:
            t.write(self.cDHeaders[name]._writeFile())
        # Write End of Directory
        t.write(self.endOfCd._writeFile())

        t.seek(0)
        return t.read()


# f = open('chr_coach_r0010_a1.iff', 'rb')
# t = customZipFile(f)
# print t.nameList
# f.close()
# k = open('temp.zip', 'wb')
# k.write(t._writeZip())
# k.close()
