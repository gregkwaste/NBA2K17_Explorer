### NBA 2K16 PARSING FUNCTIONS###
import struct
import sys
from nba2k17commonvars import *
import gc
import pylzma
sys.path.append('../gk_blender_lib/modules')
from string_func import *
from models_2k import Model2k, Model2kPart
from json_parser import *
# Logging
import logging
logging.basicConfig(level=logging.INFO)


class sub_file:

    def __init__(self, data):
        self.files = []
        self.data = data
        # self.size = size
        magic = struct.unpack('>I', data.read(4))[0]
        self.data.seek(-4, 1)
        try:
            self.type = type_dict[magic]
        except KeyError:
            logging.info(' '.join(map(str, ('Unknown Type ', hex(magic)))))
            return None

        self.namelist = []
        # ------
        # self.data.seek(0)
        # f=open('C:\\test','wb')
        # f.write(self.data.read())
        # f.close()
        # self.data.seek(0)
        # ------
        self._open()

    @staticmethod
    def _get_zip_info_offset(index, data):
        exit_flag = 0
        i = 0
        while True:
            id = struct.unpack('>I', data.read(4))[0]
            if id == 0x504B0304:
                data.seek(0x4, 1)  # skip to compression mode
                c_type = struct.unpack('<H', data.read(2))[0]
                data.seek(0x8, 1)  # skip to size
                c_size = struct.unpack('<I', data.read(4))[0]
                d_size = struct.unpack('<I', data.read(4))[0]
                name_size = struct.unpack('<H', data.read(2))[0]
                extra_field_size = struct.unpack('<H', data.read(2))[0]
                name = read_string_n(data, name_size)  # read file name
                data.seek(extra_field_size, 1)
                data.seek(c_size, 1)
            elif id == 0x504B0102:
                data.seek(0xC, 1)
                if i >= index:
                    break
                else:
                    i += 1
                data.seek(0x4, 1)
                c_size = struct.unpack('<I', data.read(4))[0]
                d_size = struct.unpack('<I', data.read(4))[0]
                name_size = struct.unpack('<H', data.read(2))[0]
                extra_field_size = struct.unpack('<H', data.read(2))[0]
                data.seek(0xE, 1)
                data.seek(name_size, 1)
                data.seek(extra_field_size, 1)
        return True

    @staticmethod
    def _get_zip_end_offset(data):
        exit_flag = 0
        i = 0
        while True:
            id = struct.unpack('>I', data.read(4))[0]
            if id == 0x504B0304:
                data.seek(0x4, 1)  # skip to compression mode
                c_type = struct.unpack('<H', data.read(2))[0]
                data.seek(0x8, 1)  # skip to size
                c_size = struct.unpack('<I', data.read(4))[0]
                d_size = struct.unpack('<I', data.read(4))[0]
                name_size = struct.unpack('<H', data.read(2))[0]
                extra_field_size = struct.unpack('<H', data.read(2))[0]
                name = read_string_n(data, name_size)  # read file name
                data.seek(extra_field_size, 1)
                data.seek(c_size, 1)
            elif id == 0x504B0102:
                data.seek(0xC, 1)
                data.seek(0x4, 1)
                c_size = struct.unpack('<I', data.read(4))[0]
                d_size = struct.unpack('<I', data.read(4))[0]
                name_size = struct.unpack('<H', data.read(2))[0]
                extra_field_size = struct.unpack('<H', data.read(2))[0]
                data.seek(0xE, 1)
                data.seek(name_size, 1)
                data.seek(extra_field_size, 1)
            elif id == 0x504B0506:
                data.seek(0xC, 1)
                break
        return True

    def _get_zip_offset(self, index):
        logging.info('Seeking Inner File')
        self.data.seek(0)
        exit_flag = 0
        i = 0
        while True:
            id = struct.unpack('>I', self.data.read(4))[0]
            if id == 0x504B0304:
                self.data.seek(0x4, 1)  # skip to compression mode
                c_type = struct.unpack('<H', self.data.read(2))[0]
                self.data.seek(0x8, 1)  # skip to size
                c_size = struct.unpack('<I', self.data.read(4))[0]
                d_size = struct.unpack('<I', self.data.read(4))[0]
                name_size = struct.unpack('<I', self.data.read(4))[0]
                name = read_string_n(self.data, name_size)  # read file name
                if i >= index:
                    break
                else:
                    i += 1
                self.data.seek(c_size, 1)
        ret = self.data.tell()
        self.data.seek(0)
        return ret

    def _zip_parser(self):
        self.data.seek(0)
        self.sects = []
        self.infSects = []
        exit_flag = 0
        while not exit_flag:
            id = struct.unpack('>I', self.data.read(4))[0]
            if id == 0x504B0304:
                self.data.seek(0x4, 1)  # skip to compression mode
                c_type = struct.unpack('<H', self.data.read(2))[0]
                self.data.seek(0x8, 1)  # skip to size
                c_size = struct.unpack('<I', self.data.read(4))[0]
                d_size = struct.unpack('<I', self.data.read(4))[0]
                name_size = struct.unpack('<H', self.data.read(2))[0]
                extra_field_size = struct.unpack('<H', self.data.read(2))[0]

                sec_offset = self.data.tell() - 30
                sec_size = 30 + name_size + extra_field_size

                name = read_string_n(self.data, name_size)  # read file name
                self.data.seek(extra_field_size, 1)

                self.namelist.append(name)

                # type=name.split('.')[-1]
                # type=type.upper()
                # logging.info((name)
                self.files.append(
                    (name, self.data.tell(), c_size, d_size, zip_types[c_type]))
                self.sects.append(
                    (name, sec_offset, sec_size + c_size, '0x504B0304'))
                self.data.read(c_size)
            elif id == 0x504B0102:
                self.data.seek(0x18, 1)  # skip to name size
                name_size = struct.unpack('<H', self.data.read(2))[0]
                extra_field_size = struct.unpack('<H', self.data.read(2))[0]
                self.data.read(0xE)  # skip zeroes

                sec_offset = self.data.tell() - 46
                sec_size = 46 + name_size + extra_field_size

                name = read_string_n(self.data, name_size)  # read file name
                self.data.seek(extra_field_size, 1)
                self.infSects.append(
                    (name, sec_offset, sec_size, '0x504B0102'))
            elif id == 0x504B0506:
                self.data.seek(0x12, 1)
                sec_offset = self.data.tell() - 22
                sec_size = 22

                self.sects.append(('end', sec_offset, sec_size, '0x504B0506'))
                exit_flag = 1
                stop = self.data.tell()

    def _get_file(self, index):
        name, off, size, type = self.files[index]
        logging.info(' '.join(map(str, ('Getting ', name, ' Offset:', off,
                                        ' Type:', type, ' Size:', size))))
        self.data.seek(off)
        t = StringIO()
        t.write(self.data.read(size))
        t.seek(0)

        if type == 'LZMA':
            t.seek(4, 1)
            k = StringIO()
            k.write(pylzma.decompress_compat(t.read()))
            t.close()
            k.seek(0)
            t = k
        return t

    def _open(self):
        gc.collect()
        if self.type == 'ZIP':
            logging.info('Opening ZIP file')
            #------
            # self.data.seek(0)
            # f = open('C:\\test', 'wb')
            # f.write(self.data.read())
            # f.close()
            self.data.seek(0)
            #------
            self._zip_parser()  # populate class by parsing the zip
        elif self.type == 'DDS':
            self.files = [('dds_file', 0, self.size, 'DDS')]
            self.namelist = ['dds_file']
        elif self.type == 'GZIP LZMA':
            self.data.seek(0xE, 1)
            t = StringIO()
            t.write(pylzma.decompress_compat(self.data.read()))
            t.seek(0)
            self.data = StringIO()  # swap buffers
            self.data.write(t.read())
            t.seek(0)
            typecheck = struct.unpack('>I', t.read(4))[0]
            self.size = 4 + len(t.read())
            t.close()
            try:
                self.type = type_dict[typecheck]
            except:
                self.type = 'UNKNOWN'
            self.data.seek(0)

            # logging.info('Reopening')
            self._open()
        elif self.type == 'ZLIB':
            logging.info('Opening ZLIB file')
            self.data.seek(0x10, 0)
            t = StringIO()
            t.write(zlib.decompress(self.data.read()), -15)
            self.size = t.len
            t.seek(0)
            typecheck = struct.unpack('>I', t.read(4))[0]
            t.seek(0)
            try:
                typecheck = type_dict[typecheck]
                self.type = typecheck
            except:
                # Handle Zlib XML files
                self.type = 'XML'
                self.size -= 0x10
                t.seek(0x10)
            self.data = StringIO()
            self.data.write(t.read())
            self.data.seek(0)
            t.close()
            self._open()
        elif self.type == 'MODEL':
            self.files = [('model_file', 0, self.size, 'MODEL')]
            self.namelist = ['model_file']
        elif self.type == 'XML':
            self.files = [('xml_file', 0, self.size, 'XML')]
            self.namelist = ['xml_file']
        else:
            logging.info(' '.join(map(str, ('Unknown type: ', hex(
                struct.unpack('>I', self.data.read(4))[0])))))


def archive_parser(f):
    logging.info('Arhive Parser Func')
    return sub_file(f).files


def parseModel(jsondata, modeldata, mindex):
    fType = struct.unpack('>Q', modeldata.read(8))[0]
    logging.info(' '.join(map(str, ('File Type: ', hex(fType)))))

    # Parse Model Parts
    # mindex = jsondata['Model']
    # for model in mindex:
    model_parts = []
    sect = Model2k(modeldata)
    index = mindex['Prim']
    mode = None
    start = 0
    for dataentry in index:
        logging.info(' '.join(map(str, ('Model Part:', dataentry))))
        mesh = None
        part_name = ''

        try:
            mesh = index[dataentry]['Mesh']
        except:
            mesh = dataentry + str('_model')

        try:
            count = index[dataentry]['Count']
        except:
            pass

        if not mode:
            try:
                mode = index[dataentry]['Type']
            except:
                mode = 'TRIANGLE_STRIP'

        part = Model2kPart(mesh, start, count)  # Create Part Object
        if mode == 'TRIANGLE_STRIP':
            logging.info(' '.join(map(str, ('Target Strips: ', part.count))))
            logging.info(' '.join(map(str, ('Starting offset: ', hex(sect.tell())))))
            sect.data = sect.read_strips(part.start, part.count + 1)
            part_indices = sect.strips_to_faces()
        else:
            logging.info(' '.join(map(str, ('Target Triangles: ', part.count))))
            logging.info(' '.join(map(str, ('Starting offset: ', hex(sect.tell())))))
            part_indices = sect.read_lists(part.start, part.count)

        start += count
        logging.info('-' * 20)
        model_parts.append([part, part_indices])
        # break

    modeldata.seek(sect.size + 8)
    logging.info("Current file offset :" + str(hex(modeldata.tell())))
    # Parsing the Vertex Data
    index = mindex['VertexFormat']
    try:
        scale = mindex['Radius'] / 100.0
    except:
        logging.info("Missing Radius Parameter")
        scale = 1.0
    scale = [1.0, 1.0, 1.0]
    # logging.info(' '.join(map(str,('model: ', mindex))))

    verts, normals, binormals, tangents, uvs, blendindices, blendweights = [
    ], [], [], [], [], [], []
    
    for dataentry in index:
        logging.info(' '.join(map(str, ('dataentry', dataentry))))
        vformat = None
        offset = None
        if dataentry == 'POSITION0':
            # parsing vertices
            vformat = index[dataentry]['Format']
            try:
                locscale = index[dataentry]['Scale']
                logging.info(' '.join(map(str, ('Scale', locscale))))
            except:
                # logging.info("Missing LocalScale Parameter")
                locscale = [1.0, 1.0, 1.0]
            sect = Model2k(modeldata)
            verts = sect.get_verts(vformat, locscale)
        elif dataentry == 'NORMAL0':
            # parsing vertices
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)
            normals = sect.get_normals(vformat)
        elif dataentry == 'BINORMAL0':
            # parsing normals
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)
            binormals = sect.get_verts(vformat, scale)
        elif dataentry == 'COLOR0':
            # parsing colors
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)
            colors = sect.get_colors(vformat)
        elif dataentry == 'TANGENT0':
            # parsing tangents
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)
            tangents = sect.get_verts(vformat, scale)
        elif 'TEXCOORD' in dataentry:
            # parsing uvs
            vformat = index[dataentry]['Format']
            try:
                scale = index[dataentry]['Scale']
            except:
                logging.info("Missing Scale Parameter")
            try:
                offset = index[dataentry]['Offset']
            except:
                logging.info("Missing Offset Parameter")
            sect = Model2k(modeldata)
            uvstemp = sect.get_uvs(vformat, scale, offset)
            if uvstemp:
                uvs.append(uvstemp)
        elif dataentry == 'BLENDINDICES0':
            # parsing blendindices
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)

            blendindices = sect.get_blendindices(vformat)
        elif dataentry == 'BLENDWEIGHT0':
            # parsing blendweights
            vformat = index[dataentry]['Format']
            sect = Model2k(modeldata)
            blendweights = sect.get_blendweights(vformat)
        # break  # RETURNING

    faces = []
    for part, indices in model_parts:
        faces.extend(indices)

    # logging.info(' '.join(map(str,('Uvs length', len(uvs))))
    # ob_name = createmesh(verts, faces, uvs, part.name, 0, 0, '', [
    # ], [], [], Vector(mindex[model]['Center']).xzy)
    # Calculate normals
    if not normals:
        for i in range(len(verts)):
            normals.append((0.0, 1.0, 0.0))
    if len(binormals) & len(tangents):
        normals = Model2k.calculate_normals(binormals, tangents)
    if not uvs:
        temp = []
        for i in range(len(verts)):
            temp.append((0.0, 0.0))
        uvs.append(temp)
    logging.info(' '.join(map(str, (len(verts), len(faces), len(uvs), len(normals)))))
    return (verts, faces, uvs[0], normals)


def constructOgg(original, new, metadata):
    length = metadata['length']
    t = StringIO()
    t.write(original[0:0x14])
    t.write(struct.pack('<I', 48 * length))  # audio parameter calculation
    t.write(struct.pack('<I', 8732))  # first stream size
    t.write(struct.pack('<I', len(new)))  # Write NewData Size
    t.write(original[0x20:0x2C])
    t.write(new[0:0x2214])  # Write First Stream
    t.write(new)
    t.seek(0)
    # f = open('tempogg.ogg', 'wb')
    # f.write(t.read())
    # f.close()
    # t.seek(0)
    return t.read()
