
# DDS HEADER File
# Contains defined classes for dds texture files parsing

# Created By: gregkwaste
# Contact: gregkwaste@gmail.com


import struct
import gc
from StringIO import StringIO

dx10_types = {70: 'DXT1',
              71: 'DXT1',
              72: 'DXT1',
              76: 'DXT3',
              77: 'DXT3',
              78: 'DXT3',
              82: 'DXT5',
              83: 'ATI2',
              84: 'ATI2',
              }


class dds_header:

    def __init__(self, *args):
        try:
            mode = args[0]
        except:
            print('You need to pass the mode')
            raise TypeError
        if mode:
            try:
                data = StringIO()
                data.write(args[1])
                data.seek(0)
                # print(type(data))
            except:
                print('With Read mode you have to pass the image file')
                raise TypeError

        if not mode:
            self.dwmagic = 0x44445320
            self.dwSize = 0
            self.dwFlags = 0
            self.dwHeight = 0
            self.dwWidth = 0
            self.dwPitchOrLinearSize = 0
            self.dwDepth = 0
            self.dwMipMapCount = 0
            self.dwReserved = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            self.ddspf = ddspf(False)
            self.dwCaps = 0
            self.dwCaps2 = 0
            self.dwCaps3 = 0
            self.dwCaps4 = 0
            self.dwReserved2 = 0
        else:
            self.headerSize = 0
            self.dwmagic = struct.unpack('>I', data.read(4))[0]
            if not self.dwmagic == 0x44445320:
                print(hex(self.dwmagic))
                raise TypeError
            self.dwSize = struct.unpack('<I', data.read(4))[0]
            self.dwFlags = struct.unpack('<I', data.read(4))[0]
            self.dwHeight = struct.unpack('<I', data.read(4))[0]
            # self.dwHeight=self.dwHeight % 4 + self.dwHeight #correct
            # dimensions
            self.dwWidth = struct.unpack('<I', data.read(4))[0]
            # self.dwWidth=self.dwWidth % 4 + self.dwWidth #correct dimensions
            self.dwPitchOrLinearSize = struct.unpack('<I', data.read(4))[0]
            self.dwDepth = struct.unpack('<I', data.read(4))[0]
            self.dwMipMapCount = struct.unpack('<I', data.read(4))[0]
            self.dwReserved = struct.unpack('<11I', data.read(44))
            self.ddspf = ddspf(True, data)
            self.dwCaps = struct.unpack('<I', data.read(4))[0]
            self.dwCaps2 = struct.unpack('<I', data.read(4))[0]
            self.dwCaps3 = struct.unpack('<I', data.read(4))[0]
            self.dwCaps4 = struct.unpack('<I', data.read(4))[0]
            self.dwReserved2 = struct.unpack('<I', data.read(4))[0]
            self.headerSize = 0x80
            # check for DX10 texture
            if ''.join(self.ddspf.dwFourCC) == 'DX10':
                self.dwdx10header = dx10_header(True, data)
                self.headerSize += 0x14


class dx10_header:

    def __init__(self, *args):
        try:
            mode = args[0]
        except:
            print('You need to pass the mode')
            raise TypeError
        if mode:
            try:
                data = args[1]
            except:
                print('With Read mode you have to pass the image file')
                raise TypeError
        if not mode:
            self.dxgi_format = 0
            self.d3d10_resource_dimension = 0
            self.miscFlag = 0
            self.arraySize = 0
            self.miscFlags2 = 0
        else:
            self.dxgi_format = struct.unpack('<I', data.read(4))[0]
            self.d3d10_resource_dimension = struct.unpack(
                '<I', data.read(4))[0]
            self.miscFlag = struct.unpack('<I', data.read(4))[0]
            self.arraySize = struct.unpack('<I', data.read(4))[0]
            self.miscFlags2 = struct.unpack('<I', data.read(4))[0]


class ddspf:
    # DDS pixelformat class

    def __init__(self, *args):
        try:
            mode = args[0]
        except:
            print('You need to pass the mode')
            raise TypeError
        if mode:
            try:
                data = args[1]
            except:
                print('With Read mode you have to pass the image file')
                raise TypeError

        if not mode:
            self.dwSize = 0
            self.dwFlags = 0
            self.dwFourCC = ('', '', '', '')
            self.dwRGBBitCount = 0
            self.dwRBitMask = 0
            self.dwGBitMask = 0
            self.dwBBitMask = 0
            self.dwABitMask = 0
        else:
            self.dwSize = struct.unpack('<I', data.read(4))[0]
            self.dwFlags = struct.unpack('<I', data.read(4))[0]
            self.dwFourCC = struct.unpack('4c', data.read(4))
            self.dwRGBBitCount = struct.unpack('<I', data.read(4))[0]
            self.dwImageMode = ['', '', '', '']
            self.dwRBitMask = struct.unpack('>I', data.read(4))[0]

            te = self.dwRBitMask
            for i in range(4):
                if te & 0xFF:
                    self.dwImageMode[3 - i] = 'R'
                    break
                else:
                    te = te >> 8
            self.dwGBitMask = struct.unpack('>I', data.read(4))[0]
            te = self.dwGBitMask
            for i in range(4):
                if te & 0xFF:
                    self.dwImageMode[3 - i] = 'G'
                    break
                else:
                    te = te >> 8
            self.dwBBitMask = struct.unpack('>I', data.read(4))[0]

            te = self.dwBBitMask
            for i in range(4):
                if te & 0xFF:
                    self.dwImageMode[3 - i] = 'B'
                    break
                else:
                    te = te >> 8
            self.dwABitMask = struct.unpack('>I', data.read(4))[0]

            te = self.dwABitMask
            for i in range(4):
                if te & 0xFF:
                    self.dwImageMode[3 - i] = 'A'
                    break
                else:
                    te = te >> 8
            self.dwImageMode = ''.join(self.dwImageMode)


class dds_file:
    # DDS Header class

    def __init__(self, *args):
        self.header = dds_header(args[0], args[1])
        self.data = StringIO()
        self.data.write(args[1][self.header.headerSize:])
        self.data.seek(0x0)

    def write_texture(self, dx10=False):
        t = StringIO()
        t.write(struct.pack('>I', 0x44445320))  # write DDS magic
        t.write(struct.pack('<7I', self.header.dwSize, self.header.dwFlags, self.header.dwHeight, self.header.dwWidth,
                            self.header.dwPitchOrLinearSize, self.header.dwDepth, self.header.dwMipMapCount))
        for i in self.header.dwReserved:
            t.write(struct.pack('<I', i))
        t.write(
            struct.pack('<II', self.header.ddspf.dwSize, self.header.ddspf.dwFlags))

        # Check for dx10 Option
        if dx10:
            temp_fourCC = self.header.ddspf.dwFourCC
        else:
            if self.header.ddspf.dwFourCC == ('D', 'X', '1', '0'):
                temp_fourCC = list(
                    dx10_types[self.header.dwdx10header.dxgi_format])
            else:
                temp_fourCC = self.header.ddspf.dwFourCC

        for i in temp_fourCC:
            t.write(struct.pack('c', i))
        t.write(struct.pack('<I', self.header.ddspf.dwRGBBitCount))
        t.write(struct.pack('>4I', self.header.ddspf.dwRBitMask, self.header.ddspf.dwGBitMask,
                            self.header.ddspf.dwBBitMask, self.header.ddspf.dwABitMask))
        t.write(struct.pack('<5I', self.header.dwCaps, self.header.dwCaps2,
                            self.header.dwCaps3, self.header.dwCaps4, self.header.dwReserved2))

        if dx10:
            if self.header.ddspf.dwFourCC == ('D', 'X', '1', '0'):
                head = self.header.dwdx10header
                t.write(struct.pack('<5I', head.dxgi_format,
                                    head.d3d10_resource_dimension,
                                    head.miscFlag, head.arraySize,
                                    head.miscFlags2))
        self.data.seek(0)
        t.write(self.data.read())
        self.data.seek(0)
        t.seek(0)
        return t

    def _get_full_size(self):
        size = self.header.headerSize
        size += self._get_mipmap_size(self.header.dwMipMapCount)
        return size

    def _get_rest_size(self):
        im_size = self._get_mipmap_size(self.header.dwMipMapCount)
        print('Image Size: ', im_size)

        pos = self.data.tell()
        self.data.seek(0)

        realImSize = len(self.data.read())

        return realImSize - im_size

    def _get_rest_data(self):
        fullSize = self._get_full_size()
        self.data.seek(fullSize - self.header.headerSize)
        data = self.data.read()
        self.data.seek(0)
        return data

    def _get_mipmap_size(self, count):
        w = self.header.dwWidth
        h = self.header.dwHeight
        if ''.join(self.header.ddspf.dwFourCC) == 'DXT1':
            mode = 8
        else:
            mode = 16

        size = 0
        while count > 0:
            pixels = w * h
            blocks = (pixels - 1) / 16
            mipmapSize = (blocks + 1) * mode
            size += max(mipmapSize, mode)
            w = max(w / 2, 4)
            h = max(h / 2, 4)
            count -= 1
        return int(size)

    def unswizzle_2k(self):
        t = StringIO()  # temporary StringIO
        self.data.seek(0)
        colors = StringIO()
        indexing = StringIO()
        alpha0 = StringIO()
        alpha1 = StringIO()

        if ''.join(self.header.ddspf.dwFourCC) == 'DXT1':
            mode = 0.5
        else:
            mode = 1

        if not self.header.dwMipMapCount:  # Force 1 mipmap
            self.header.dwMipMapCount = 1
            size = self.header.dwPitchOrLinearSize // (4 * mode)
        else:
            size = self._get_mipmap_size(
                self.header.dwMipMapCount) // (4 * mode)

        size = int(size)

        print('calculated size: ', size)
        # write to buffer
        colors.write(self.data.read(size))  # write color information
        colors.seek(0)
        indexing.write(self.data.read(size))  # write color information
        indexing.seek(0)
        if mode >= 1:
            # write first portion of the alpha
            alpha0.write(self.data.read(size))
            alpha0.seek(0)

            # write second portion of the alpha
            alpha1.write(self.data.read(size))
            alpha1.seek(0)

        for i in range(size // 4):
            t.write(colors.read(4))
            t.write(indexing.read(4))
            if mode >= 1:
                t.write(alpha0.read(4))
                t.write(alpha1.read(4))

        # COllect garbage
        colors.close()
        indexing.close()
        alpha0.close()
        alpha1.close()
        self.data.close()
        gc.collect()
        t.seek(0)
        self.data = t

    def swizzle_2k(self):
        t = StringIO()  # temporary StringIO
        self.data.seek(0)
        colors = StringIO()
        indexing = StringIO()
        alpha0 = StringIO()
        alpha1 = StringIO()
        if ''.join(self.header.ddspf.dwFourCC) == 'DXT1':
            mode = 0.5
        else:
            mode = 1

        if not self.header.dwMipMapCount:  # Force 1 mipmap
            self.header.dwMipMapCount = 1
            size = self.header.dwPitchOrLinearSize // (4 * mode)
        else:
            size = self._get_mipmap_size(
                self.header.dwMipMapCount) // (4 * mode)

        size = int(size)

        print('calculated size: ', size)

        for i in range(size // 4):
            colors.write(self.data.read(4))
            indexing.write(self.data.read(4))
            if mode >= 1:
                alpha0.write(self.data.read(4))
                alpha1.write(self.data.read(4))

        colors.seek(0)
        indexing.seek(0)
        alpha0.seek(0)
        alpha1.seek(0)

        t.write(colors.read())
        t.write(indexing.read())
        if mode >= 1:
            t.write(alpha0.read())
            t.write(alpha1.read())

        self.data.close()
        gc.collect()
        t.seek(0)
        self.data = t
