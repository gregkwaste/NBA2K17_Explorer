bl_info = {
    "name": "NBA 2K15 Model Importer",
    "description": "Importing NBA2K15 3d Models (with Animation Skeleton) into Blender's viewport",
    "author": "gregkwaste",
    "version": (0, 8, 'beta'),
    "blender": (2, 71, 0),
    "location": "View3D > Scene",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import struct
import imp
import os
import webbrowser
# from io import BytesIO
# from mathutils import Vector, Matrix
from shutil import copyfile
from math import radians

version_text = 'v0.9 Coded by gregkwaste'


class Model2kPart:

    def __init__(self, name, start, count):
        self.name = name
        self.start = start
        self.count = count


class ModelEntry:

    def __init__(self):
        self.faces = []
        self.verts = []
        self.uvs = []
        self.cols = []

    def parse_data(self, ob):
        self.faces = []
        self.verts = []
        self.uvs = []
        self.cols = []

        uvs_0 = []
        uvs_1 = []
        uvs_2 = []
        data = ob.data
        print('Processing: ', ob.name)
        bm = bmesh.new()
        bm.from_mesh(data)
        bm.normal_update()

        # Matrices
        object_matrix_wrld = ob.matrix_world
        rot_x_mat = Matrix.Rotation(radians(0), 4, 'X')
        scale_mat = Matrix.Scale(1, 4)  # Keeping only this scale for FIFA 15

        # New way
        uvcount = len(bm.loops.layers.uv)
        colcount = len(bm.loops.layers.color)

        # Store Vertices
        for v in bm.verts:
            co = scale_mat * rot_x_mat * object_matrix_wrld * v.co
            self.verts.append((co[0], co[1], co[2]))

        for i in range(len(self.verts)):
            uvs_0.append(0)
            uvs_1.append(0)
            uvs_2.append(0)

        for f in bm.faces:
            for l in f.loops:
                vid = l.vert.index  # Get vertex index
                # uvs
                for k in range(uvcount):
                    layer = bm.loops.layers.uv[k]
                    u = l[layer].uv.x
                    v = 1. - l[layer].uv.y
                    exec('uvs_' + str(k) + '[vid]=(round(u,8),round(v,8))')
                # for k in range(colcount):
                    # layer=bm.loops.layers.color[k]
                    # r=l[layer].r*1023
                    # g=l[layer].g*1023
                    # b=l[layer].b*1023
                    # eval('col_'+str(k)+'.append((r,g,b))')

                # Define a face for each loop
            # if len(f.loops)==4:
                # indices.append((id,id+1,id+2))
                # indices.append((id+3,id,id+2))
                # id+=4
            # elif len(f.loops)==3:
                # indices.append((id,id+1,id+2))
                # id+=3
        # bm.free()

        # Gather different maps
        for j in range(uvcount):
            eval('self.uvs.append(uvs_' + str(j) + ')')
        for j in range(colcount):
            eval('self.cols.append(col_' + str(j) + ')')

        for i in range(len(uvs_0)):
            if not uvs_0[i]:
                print(i)


class Bone:

    def __init__(self, Sibling, Child, Name, boneId, Position):
        self.Sibling = Sibling
        self.Child = Child
        self.Name = Name
        self.id = boneId
        self.Position = Position


class Model2k:

    def __init__(self, f):
        self.__file__ = f
        self.type = struct.unpack('>I', f.read(4))[0]
        self.size = struct.unpack('<I', f.read(4))[0]
        self.hash = struct.unpack('>Q', f.read(8))[0]
        self.num0 = struct.unpack('>I', f.read(4))[0]
        self.num1 = struct.unpack('<H', f.read(2))[0]
        self.num2 = struct.unpack('B', f.read(1))[0]
        self.num3 = struct.unpack('B', f.read(1))[0]
        self.headersize = 0x18
        self.data = None
        print('Section ', hex(self.type), self.size, hex(
            self.hash), self.num0, self.num1, self.num2, self.num3)

    def tell(self):
        return self.__file__.tell()

    def skip_section(self):
        self.__file__.seek(self.size - self.headersize, 1)

    def get_verts(self, vformat, scale):
        if vformat == "R16G16B16A16_SNORM":
            return self.read_vertices_half(scale)
        elif vformat == "R32G32B32_FLOAT":
            return self.read_vertices_float3(scale)
        else:
            print('Not Implemented vertex format: ', vformat)

    def get_colors(self, vformat):
        if vformat == "R8G8B8A8_UNORM":
            return self.read_blendweights_unorm()
        elif vformat == "R16G16B16A16_FLOAT":
            return self.read_colors_half()
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

    def get_normals(self, vformat):
        if vformat == "R32G32B32_FLOAT":
            return self.read_vertices_float()
        elif vformat == "R16G16B16A16_SNORM":
            return self.read_normals_half()
        else:
            print('Wrong num2')

    def get_uvs(self, vformat, scale, offset):
        if vformat in ["R16G16_SNORM", "R16G16_FLOAT"]:
            return self.read_uvs_half(scale, offset)
        elif vformat == "R16G16B16A16_FLOAT":
            return self.read_uvs_half()
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
        self.__file__.seek(self.headersize + 8 + 0x2 * start)
        while count < target:
            temp = struct.unpack('<3H', self.__file__.read(6))
            if not (temp[0] == temp[1] or temp[1] == temp[2] or temp[2] == temp[0]):
                indices.append(temp)
            count += 3
        return indices

    def read_strips(self, start, target):
        indices = []
        count = 0
        self.__file__.seek(self.headersize + 8 + 0x2 * start)
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
        v_count = (self.size - self.headersize) // 8
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

    def read_normals_half(self):
        v_count = (self.size - self.headersize) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            self.__file__.read(2)
            verts.append((v1, v2, v3))
        return verts

    def read_colors_half(self):
        v_count = (self.size - self.headersize) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            self.__file__.read(2)
            verts.append((v1, v3, v2))
        return verts

    def read_uvs_half(self):
        v_count = (self.size - self.headersize) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', self.__file__.read(2))[0] / 65535.0
            self.__file__.read(4)
            verts.append((v1, v2))
        return verts

    def write_vertices_half(self, scale, verts):
        oldv_count = (self.size - self.headersize) // 8
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
        v_count = (self.size - self.headersize) // 12
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<f', self.__file__.read(4))[0]
            v2 = struct.unpack('<f', self.__file__.read(4))[0]
            v3 = struct.unpack('<f', self.__file__.read(4))[0]
            verts.append((-scale[0] * v1, scale[2] * v3, scale[1] * v2))
        return verts

    def read_vertices_float(self, f, scale):
        v_count = (self.size - self.headersize) // 12
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<f', f.read(4))[0]
            v2 = struct.unpack('<f', f.read(4))[0]
            v3 = struct.unpack('<f', f.read(4))[0]
            verts.append((scale[0] * v1, scale[2] * v3, scale[1] * v2))
        return verts

    def read_uvs_half(self, scale, offset):
        uv_count = (self.size - self.headersize) // 4
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
        count = (self.size - self.headersize) // 8
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
        count = (self.size - self.headersize) // 4
        indices = []
        for i in range(count):
            entry = struct.unpack('4B', self.__file__.read(4))
            indices.append(entry)
        return indices

    def read_blendweights_unorm(self):
        count = (self.size - self.headersize) // 4
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


class Model2kPart:

    def __init__(self, name, start, count):
        self.name = name
        self.start = start
        self.count = count

# Create Mesh and Object Function


def model_import(scn):
    jsondata = json_parser.NbaJsonParser(scn.nba_json_filepath)
    # =========================================================================
    # Get JSON Data
    # jsondata = json_parser.NbaJsonParser('/home/gregkwaste/irving/0G/group_0_unknown_6_hi_head5/metadata.json')
    # jsondata = json_parser.NbaJsonParser('/home/gregkwaste/irving/0G/group_0_unknown_5_hiheadnodes/metadata.json')
    # jsondata = json_parser.NbaJsonParser('C:\\Users\\gregkwaste\\Desktop\\irving\\0G\\group_0_unknown_5_hiheadnodes\\metadata.json')
    # BinaryModelName = jsondata['Model']['player']['Binary']
    # print("Correct Model File Name: ", BinaryModelName)

    # Start Reading Model File
    # modeldata = open('/home/gregkwaste/irving/0G/group_0_unknown_6_hi_head5/' + BinaryModelName, 'rb')
    # modeldata = open('/home/gregkwaste/irving/0G/group_1_unknown_11', 'rb')
    modeldata = open(scn.nba_model_filepath, 'rb')
    fType = struct.unpack('>I', modeldata.read(4))[0]
    print('File Type: ', hex(fType))

    # Parse Model Parts
    mindex = jsondata['Model']
    for model in mindex:
        model_parts = []
        sect = Model2k(modeldata)
        index = mindex[model]['Prim']
        mode = None
        start = 0
        for dataentry in index:
            print('Model Part:', dataentry)
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
                print('Target Strips: ', part.count)
                print('Starting offset: ', hex(sect.tell()))
                sect.data = sect.read_strips(part.start, part.count + 1)
                part_indices = sect.strips_to_faces()
            else:
                print('Target Triangles: ', part.count)
                print('Starting offset: ', hex(sect.tell()))
                part_indices = sect.read_lists(part.start, part.count)

            start += count
            print('-' * 20)
            model_parts.append([part, part_indices])
            # break

        modeldata.seek(sect.size + 4)
        # Parsing the Vertex Data
        index = mindex[model]['VertexFormat']
        try:
            scale = index[model]['Radius']
        except:
            print("Missing Radius Parameter")
            scale = 1.0
        scale = [scale, scale, scale]

        print('model: ', model)

        verts, binormals, tangents, uvs, blendindices, blendweights = [
        ], [], [], [], [], []
        for dataentry in index:
            print('dataentry', dataentry)
            vformat = None
            scale = None
            offset = None

            if dataentry == 'POSITION0':
                # parsing vertices
                vformat = index[dataentry]['Format']
                sect = Model2k(modeldata)
                verts = sect.get_verts(vformat, scale)
            elif dataentry == 'BINORMAL0':
                # parsing normals
                vformat = index[dataentry]['Format']
                sect = Model2k(modeldata)
                binormals = sect.get_verts(vformat, scale)
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
                    print("Missing Scale Parameter")
                try:
                    offset = index[dataentry]['Offset']
                except:
                    print("Missing Offset Parameter")
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

        print('Uvs length', len(uvs))
        ob_name = createmesh(verts, faces, uvs, part.name, 0, 0, '', [
        ], [], [], Vector(mindex[model]['Center']).xzy)

        ### Add Vertex Groups with the Model Parts ###
        ob = bpy.data.objects[ob_name]

        bpy.context.scene.objects.active = ob  # Set active object on scene

        ### Create Material Vertex Groups ###
        for part, indices in model_parts:
            vg = ob.vertex_groups.new(part.name)

            sel_verts = []
            for v0, v1, v2 in indices:
                sel_verts.extend([v0, v1, v2])
            vg.add(sel_verts, 1.0, 'ADD')

        if scn.nba2k15_skeleton_flag:
            skeleton_import(jsondata, blendindices, blendweights, ob)


def skeleton_import(jsondata, blendindices, blendweights, ob):
    # Parsing the Bones
    index = jsondata['Model']['player']['Node']
    bones = []
    boneId = 0
    ### Store Bones ###
    for dataentry in index:
        Child = None
        Sibling = None
        Name = dataentry
        Position = None
        try:
            Child = index[dataentry]['Child']
        except:
            pass

        try:
            Sibling = index[dataentry]['Sibling']
        except:
            pass

        try:
            Position = 0.5 * Vector(index[dataentry]['Pos'])
            Position[0] *= -1.0
        except:
            pass

        bone = Bone(Sibling, Child, Name, boneId, Position)
        ob.vertex_groups.new(bone.Name)
        bones.append(bone)
        boneId += 1

    print('Total Bones Detected: ', len(bones))
    ### Create Groups for Bones ###
    v_blendgroups = []
    v_blendweights = []
    for i in range(len(bones)):
        v_blendgroups.append([])
    for i in range(len(bones)):
        v_blendweights.append(0)

    for v_id in range(len(blendindices)):
        vblendindices = blendindices[v_id]
        vblendweights = blendweights[v_id]

        for e in range(len(vblendindices)):
            v_bone_id = vblendindices[e]
            v_bone_weight = vblendweights[e]
            # v_blendgroups[bone_id].append(v_id)
            vg = ob.vertex_groups[bones[v_bone_id].Name]
            vg.add([v_id], v_bone_weight, 'ADD')

    bpy.ops.object.add(
        type='ARMATURE',
        enter_editmode=True,
        location=Vector(jsondata['Model']['player']['Center']).xzy)

    ob = bpy.data.objects['Armature']
    ob.show_x_ray = True
    ob.name = 'nba_bones'
    amt = ob.data
    amt.name = 'NBA_Amt'
    amt.show_axes = True

    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')

    for b in bones:
        if b.Name not in amt.edit_bones:
            bone = amt.edit_bones.new(b.Name)
        else:
            bone = amt.edit_bones[b.Name]

        if b.Position:
            bone.tail = bone.head + b.Position.xzy
        else:
            bone.tail = bone.head + Vector([0.01, 0.01, 0.01])
        bone.use_connect = True

        if b.Child:
            cb = bones[b.Child]
            child = amt.edit_bones.new(cb.Name)
            child.parent = bone
            child.head = bone.tail

        if b.Sibling:
            sb = bones[b.Sibling]
            sibling = amt.edit_bones.new(sb.Name)
            sibling.parent = bone.parent
            sibling.head = bone.head

    bpy.ops.object.mode_set(mode='OBJECT')


def model_export(scn, ob, jsondata, modeldata):
    print('Exporting:', ob.name)
    modeldata.seek(0x4)  # Skip header
    sect = Model2k(modeldata)
    modeldata.seek(sect.size + 4)  # Skip Triangles
    mindex = jsondata['Model']
    for model in mindex:
        index = mindex[model]['VertexFormat']
        model = ModelEntry()
        model.parse_data(ob)

        for dataentry in index:
            print('dataentry', dataentry)
            vformat = None
            scale = None
            offset = None

            if dataentry == 'POSITION0':
                print("Writing Verts")
                # writing vertices
                vformat = index[dataentry]['Format']
                try:
                    scale = index[dataentry]['Scale']
                except:
                    print("Missing Scale Parameter")
                sect = Model2k(modeldata)
                sect.write_verts(vformat, scale, model.verts)
            elif dataentry == 'BINORMAL0':
                print("Writing Binormals")
                # writing normals
                vformat = index[dataentry]['Format']
                print('binormals starting offset', modeldata.tell())
                sect = Model2k(modeldata)

                modeldata.seek(sect.size - 0x10, 1)
            elif dataentry == 'TANGENT0':
                print("Writing Tangents")
                # writing tangents
                vformat = index[dataentry]['Format']
                sect = Model2k(modeldata)
                modeldata.seek(sect.size - 0x10, 1)
            elif 'TEXCOORD' in dataentry:
                print("Writing Uvs", dataentry)
                # writing uvs
                vformat = index[dataentry]['Format']
                try:
                    scale = index[dataentry]['Scale']
                except:
                    print("Missing Scale Parameter")
                try:
                    offset = index[dataentry]['Offset']
                except:
                    print("Missing Offset Parameter")
                sect = Model2k(modeldata)
                id = int(dataentry.split('TEXCOORD')[-1])
                print('id', id, len(model.uvs[id]))
                sect.write_uvs(vformat, scale, offset, model.uvs[id])
            elif dataentry == 'BLENDINDICES0':
                # parsing blendindices
                vformat = index[dataentry]['Format']
                sect = Model2k(modeldata)
                modeldata.seek(sect.size - 0x10, 1)
            elif dataentry == 'BLENDWEIGHT0':
                # parsing blendweights
                vformat = index[dataentry]['Format']
                sect = Model2k(modeldata)
                modeldata.seek(sect.size - 0x10, 1)

    modeldata.close()
