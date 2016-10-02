import struct
import sys
import os
from math import sqrt
#from mathutils import Vector


class Model2k:

    def __init__(self, f):
        self.__file__ = f
        self.type = struct.unpack('>I', f.read(4))[0]
        self.size = struct.unpack('<I', f.read(4))[0]
        self.hash = struct.unpack('>I', f.read(4))[0]
        self.num0 = struct.unpack('<H', f.read(2))[0]
        self.num1 = struct.unpack('B', f.read(1))[0]
        self.num2 = struct.unpack('B', f.read(1))[0]
        self.data = None
        print('Section ', hex(self.type), self.size, hex(
            self.hash), self.num0, self.num1, self.num2)

    def tell(self):
        return self.__file__.tell()

    def get_verts(self, vformat, scale):
        if vformat == "R16G16B16A16_SNORM":
            return self.read_vertices_half(scale)
        elif vformat == "R32G32B32_FLOAT":
            return self.read_vertices_float3(scale)
        else:
            print('Not Implemented vertex format: ', vformat)

    def write_verts(self, vformat, scale, verts):
        if vformat == "R16G16B16A16_SNORM":
            return self.write_vertices_half(scale, verts)
        elif vformat == "R32G32B32_FLOAT":
            return self.write_vertices_float3(scale, verts)
        else:
            print('Not Implemented vertex format: ', vformat)

    def write_uvs(self, vformat, scale, offset, uvs):
        if vformat in ["R16G16_SNORM", "R16G16_FLOAT"]:
            return self.write_uvs_half(scale, offset, uvs)
        else:
            print('Not Implemented uv format: ', vformat)

    def get_blendindices(self, vformat):
        if vformat == "R8G8B8A8_UINT":
            return self.read_blendindices_uint()
        else:
            print('Not Implemented vertex format: ', vformat)

    def get_blendweights(self, vformat):
        if vformat == "R8G8B8A8_UNORM":
            return self.read_blendweights_unorm()
        else:
            print('Not Implemented vertex format: ', vformat)

    def get_normals(self, f):
        if self.num2 == 2:
            return self.read_vertices_float(f)
        elif self.num2 == 1:
            return self.read_normals_half(f)
        else:
            print('Wrong num2')

    def get_uvs(self, vformat, scale, offset):
        if vformat in ["R16G16_SNORM", "R16G16_FLOAT"]:
            return self.read_uvs_half(scale, offset)
        else:
            print('Not Implemented uv format: ', vformat)

    def fill_normals(self, count):

        norms = []
        for i in range(count):
            norms.append((0, 0, 1))
        return norms

    def read_lists(self, start, target):
        indices = []
        count = 0
        self.__file__.seek(0x14 + 0x2 * start)
        while count < target:
            temp = struct.unpack('<3H', self.__file__.read(6))
            if not (temp[0] == temp[1] or temp[1] == temp[2] or temp[2] == temp[0]):
                indices.append(temp)
            count += 3
        return indices

    def read_strips(self, start, target):
        indices = []
        count = 0
        self.__file__.seek(0x14 + 0x2 * start)
        while count < target and (self.__file__.tell() < (self.size + 0x14)):
            temp = []
            s = struct.unpack('<H', self.__file__.read(2))[0]
            count += 1
            while s != 0xFFFF and count < target and (self.__file__.tell() < (self.size + 0x14)):
                temp.append(s)
                count += 1
                s = struct.unpack('<H', self.__file__.read(2))[0]
            if len(temp):
                indices.append(temp)

        print('Strips Read: ', count - 1)
        return indices

    def read_vertices_half(self, scale):
        v_count = (self.size - 0x10) // 8
        verts = []
        if not scale:
            scale = [1., 1., 1., 1.]
        for i in range(v_count):
            v1 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            self.__file__.read(2)
            verts.append((-scale[0] * v1, scale[2] * v3, scale[1] * v2))
        return verts

    def write_vertices_half(self, scale, verts):
        oldv_count = (self.size - 0x10) // 8
        if not scale:
            scale = [1., 1., 1.]
        v_count = len(verts)
        t = BytesIO()
        for i in range(v_count):
            v1 = struct.pack('<3h', int(-verts[i][0] * 65535.0 / scale[0]), int(
                verts[i][2] * 65535.0 / scale[2]), int(verts[i][1] * 65535.0 / scale[1]))
            t.write(v1)
            t.write(struct.pack('>H', 0xFF7F))
        t.seek(0)
        self.__file__.write(t.read())

    def read_vertices_float3(self, scale):
        v_count = (self.size - 0x10) // 12
        verts = []
        if not scale:
            scale = [1., 1., 1., 1.]
        for i in range(v_count):
            v1 = struct.unpack('<f', self.__file__.read(4))[0]
            v2 = struct.unpack('<f', self.__file__.read(4))[0]
            v3 = struct.unpack('<f', self.__file__.read(4))[0]
            verts.append((scale[0] * v1, scale[2] * v3, scale[1] * v2))
        return verts

    def read_normals_half(self, f):
        v_count = (self.size - 0x10) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', f.read(2))[0] / 65535.0
            f.read(2)
            verts.append((1.0 - v1, 1.0 - v3, 1.0 - v2))
        return verts

    def read_vertices_float(self, f, scale):
        v_count = (self.size - 0x10) // 12
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<f', f.read(4))[0]
            v2 = struct.unpack('<f', f.read(4))[0]
            v3 = struct.unpack('<f', f.read(4))[0]
            verts.append((scale * v1, scale * v3, scale * v2))
        return verts

    def read_uvs_half(self, scale, offset):
        uv_count = (self.size - 0x10) // 4
        uvs = []
        if not scale:
            scale = [1., 1., 1., 1.]
        if not offset:
            offset = [.0, .0, .0, .0]
        for i in range(uv_count):
            uv1 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            uv2 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            if i in [2456]:
                print(i, uv1 * 65535.0)
                print(i, uv2 * 65535.0)
            uvs.append(
                ((offset[0] + 2 * scale[0] * uv1), (offset[1] + 2 * scale[1] * uv2)))
        return uvs

    def write_uvs_half(self, scale, offset, uvs):
        if not scale:
            scale = [1., 1., 1., 1.]
        if not offset:
            offset = [.0, .0, .0, .0]
        t = BytesIO()
        for i in range(len(uvs)):
            print(uvs[i])
            # print(int(65535.0 * (uvs[i][0] - offset[0]) / (2 * scale[0])), offset[0], scale[0], uvs[i][0], i)
            # print(int(65535.0 * (uvs[i][1] - offset[1]) / (2 * scale[1])),
            # offset[1], scale[1], uvs[i][1], i)
            val1 = int(65535.0 * (uvs[i][0] - offset[0]) / (2 * scale[0]))
            val2 = int(65535.0 * (uvs[i][1] - offset[1]) / (2 * scale[1]))
            print(val1, self.wrap(val1, 32767))
            print(val2, self.wrap(val2, 32767))
            uv1 = struct.pack(
                '<2h', self.wrap(val1, 32767), self.wrap(val2, 32767))
            t.write(uv1)
        t.seek(0)
        self.__file__.write(t.read())

    def read_unknown(self, f):
        count = (self.size - 0x10) // 8
        for i in range(count):
            f.read(8)
        return None

    def tris_to_faces(self):
        chunkNum = len(self.data)
        faces = []
        for i in range(chunkNum):
            if len(self.data[i]) == 4:
                faces.append(self.data[i])
            elif len(self.data[i]) == 8:
                faces.append(self.data[i][0:3])
                faces.append(self.data[i][4:7])
        return faces

    def strips_to_faces(self):
        chunkNum = len(self.data)
        faces = []
        degenerate_faces = []
        for i in range(chunkNum):
            strip = self.data[i]
            faceNum = len(strip) - 2
            flag = True
            index = 0
            for j in range(faceNum):
                if flag:
                    tup = (strip[index], strip[index + 1], strip[index + 2])
                    if not (tup[0] == tup[1] or tup[1] == tup[2] or tup[0] == tup[2]):
                        faces.append(tup)
                    else:
                        degenerate_faces.append(tup)
                    index += 1
                    flag = not flag
                else:
                    tup = (strip[index + 1], strip[index], strip[index + 2])
                    if not (tup[0] == tup[1] or tup[1] == tup[2] or tup[0] == tup[2]):
                        faces.append(tup)
                    else:
                        degenerate_faces.append(tup)
                    index += 1
                    flag = not flag
        print('Degenerate Faces: ', len(degenerate_faces))
        return faces

    def read_blendindices_uint(self):
        count = (self.size - 0x10) // 4
        indices = []
        for i in range(count):
            entry = struct.unpack('4B', self.__file__.read(4))
            indices.append(entry)
        return indices

    def read_blendweights_unorm(self):
        count = (self.size - 0x10) // 4
        indices = []
        for i in range(count):
            entry = struct.unpack('4B', self.__file__.read(4))
            entry = [j / 255.0 for j in entry]
            indices.append(entry)
        return indices

    def wrap(self, val, maxval):
        if val > maxval:
            return int(val - maxval)
        else:
            return val
        # return(int(val - (val / maxval) * maxval))

    @staticmethod
    def calculate_normals(binormals, tangents):
        norms = []
        for i in range(len(binormals)):
            tangs = tangents[i]  # original tangent vector
            # length=sqrt(sum([v**2 for v in tangs])) #  tangent vector length
            # tangs=[v/length for v in tangs] # normalize vector

            binorms = binormals[i]  # original binormals vector
            # length=sqrt(sum([v**2 for v in binorms]))
            # binormal vector length
            # binorms=[v/length for v in binorms] # normalize vector

            # store cross product
            cross = (binorms[1] * tangs[2] - binorms[2] * tangs[1],
                     binorms[2] * tangs[0] - binorms[0] * tangs[2],
                     binorms[0] * tangs[1] - binorms[1] * tangs[0])
            norms.append((cross[0], cross[1], cross[2]))
            # print(cross)
        return norms
# =========================================================================
