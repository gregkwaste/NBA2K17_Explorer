# Imports
from PySide import QtCore, QtGui, QtOpenGL
from PySide.QtGui import QMenu, QMessageBox
from PIL import Image
import sys
import math
from dds import *
from models_2k import Model2k
from StringIO import StringIO
from ctypes import *
import numpy as np
import time
# pyopengl checking
try:
    # from OpenGL import *
    import OpenGL.GL as GL
    import OpenGL.GLUT as GLUT
    # import OpenGL.GLU as GLU
    import OpenGL.arrays.vbo as glvbo

except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL textures",
                               "PyOpenGL must be installed to run this example.",
                               QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                               QtGui.QMessageBox.NoButton)
    sys.exit(1)

# Logging
import logging
logging.basicConfig(level=logging.INFO)

# Init Glut
GLUT.glutInit()
# from OpenGL.constants import GLfloat
vec4 = GL.constants.GLfloat_4

# texture GL type dictionary
image_types = {'DXT1': 0x83F1,
               'DXT3': 0x83F2,
               'DXT5': 0x83F3,
               'ATI2': 0x8DBD,  # Working 0x8DBD
               70: 0x83F1,
               71: 0x83F1,
               72: 0x83F1,
               76: 0x83F2,
               77: 0x83F2,
               78: 0x83F2,
               82: 0x83F3,
               83: 0x8dbd,
               84: 0x83F3,
               '\x00\x00\x00\x00': 0,
               'q\x00\x00\x00': 0,
               113: 0,
               }

verticies = (
    (1.0, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

quadverts = [
    (-1.0, 1.0, 0.0),
    (1.0, 1.0, 0.0),
    (-1.0, -1.0, 0.0),
    (1.0, -1.0, 0.0)
]

quadfaces = [
    (0, 1, 2),
    (1, 2, 3)
]

quaduvs = [
    (0.0,  1.0),
    (1.0,  1.0),
    (0.0, 0.0),
    (1.0, 0.0)
]

quadnorms = [
    (0.0, 0.0, 1.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, 1.0)
]

edges = (
    (0, 1),
    (0, 3),
    (0, 4),
    (2, 1),
    (2, 3),
    (2, 7),
    (6, 3),
    (6, 4),
    (6, 7),
    (5, 1),
    (5, 4),
    (5, 7)
)

colors = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0, 1, 0),
    (1, 1, 1),
    (0, 1, 1),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 0),
    (1, 1, 1),
    (0, 1, 1),
)

surfaces = ((0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6))

myVS = '''
# version 330
//attributes
in vec3 vPosition;
in vec2 uvPosition;
in vec3 nPosition;
//in mat4 projMat;
out vec3 L,N;
out vec2 texCoord;
uniform vec3 theta;
uniform vec4 lightPos;
uniform float scale,panX,panY,aspect;

void main() {
    texCoord = uvPosition;
    vec3 angles = radians( theta );
    vec3 c = cos( angles );
    vec3 s = sin( angles );

    // Remeber: thse matrices are column-major
    mat4 rx = mat4( 1.0,  0.0,  0.0, 0.0,
            0.0,  c.x,  s.x, 0.0,
            0.0, -s.x,  c.x, 0.0,
            0.0,  0.0,  0.0, 1.0 );

    mat4 ry = mat4( c.y, 0.0, -s.y, 0.0,
            0.0, 1.0,  0.0, 0.0,
            s.y, 0.0,  c.y, 0.0,
            0.0, 0.0,  0.0, 1.0 );

    mat4 rz = mat4( c.z, -s.z, 0.0, 0.0,
            s.z,  c.z, 0.0, 0.0,
            0.0,  0.0, 1.0, 0.0,
            0.0,  0.0, 0.0, 1.0 );

    mat4 sMat = mat4( scale, 0.0, 0.0, 0.0,
                      0.0,  scale, 0.0, 0.0,
                      0.0,  0.0, scale, 0.0,
                      0.0,  0.0, 0.0, 1.0 );

    mat4 panning = mat4(1.0, 0.0, 0.0 , 0.0,
                      0.0, 1.0, 0.0, 0.0,
                      0.0, 0.0, 1.0, 0.0,
                      panX*(scale+1.0), panY*(scale+1.0), 0.0, 1.0);

    float w = 20.0*aspect*scale;
    float h = 20.0*scale;
    mat4 projMat = mat4(2.0/w, 0.0,  0.0, 0.0,
                        0.0, 2.0/h,  0.0, 0.0,
                        0.0, 0.0, -2.0/20000.0, 0.0,
                        0.0, 0.0,  0.0, 1.0);


    mat4 mv = rz*ry*rx;
    vec4 pos = mv*vec4(vPosition, 1.0);
    //vec4 lightPos = vec4(0.0, 5.0, -5.0, 0.0);
    //lightPos = normalize(lightPos);
    //vec4 lPos = normalize(lightPos);
    //vec4 light = mv * lightPos
    vec4 nPos = vec4(nPosition.x, nPosition.y,nPosition.z, 0.0);
    L = normalize(pos - lightPos).xyz;
    N = normalize(mv*nPos).xyz;

    gl_Position = projMat * panning * pos;
    }
'''

myFS = '''
# version 330
out vec4 gl_FragColor;
in vec2 texCoord;
in vec3 N, L;
void main() {
    float kd = max(dot(L,N), 0.0);
    vec3 light_diffuse = vec3(1.0, 1.0, 1.0);
    vec3 ambient = vec3(0.7, 0.7, 0.7);
    vec3 mColor  = vec3(0.3, 0.3, 0.3);
    gl_FragColor = vec4(kd*light_diffuse*ambient + mColor, 1.0 );
}
'''

texVS = '''
# version 330
//attributes
in vec3 vPosition;
in vec2 uvPosition;
out vec2 texCoord;
uniform float scale, aspect;

void main() {
    texCoord = uvPosition;

    float w = 2.0*aspect;
    float h = 2.0*scale;
    mat4 projMat = mat4(2.0/w, 0.0,  0.0, 0.0,
                        0.0, 2.0/h,  0.0, 0.0,
                        0.0, 0.0, -2.0/1.0, 0.0,
                        0.0, 0.0,  0.0, 1.0);

    gl_Position = projMat*vec4(vPosition.x,vPosition.y,vPosition.z, 1.0);
    }
'''


texFS = '''
# version 330
in vec2 texCoord;
out vec4 gl_FragColor;
uniform sampler2D Tex0;

void main() {
    vec2 convPos = vec2(texCoord.x , 1.0-texCoord.y);
    gl_FragColor = texture2D(Tex0, convPos);
}
'''

lightVS = '''
# version 330
in vec3 vPosition;
uniform vec3 theta;
uniform float scale,panX,panY;

void main(){
    vec3 angles = radians( theta );
    vec3 c = cos( angles );
    vec3 s = sin( angles );

    // Remeber: thse matrices are column-major
    mat4 rx = mat4( 1.0,  0.0,  0.0, 0.0,
            0.0,  c.x,  s.x, 0.0,
            0.0, -s.x,  c.x, 0.0,
            0.0,  0.0,  0.0, 1.0 );

    mat4 ry = mat4( c.y, 0.0, -s.y, 0.0,
            0.0, 1.0,  0.0, 0.0,
            s.y, 0.0,  c.y, 0.0,
            0.0, 0.0,  0.0, 1.0 );

    mat4 rz = mat4( c.z, -s.z, 0.0, 0.0,
            s.z,  c.z, 0.0, 0.0,
            0.0,  0.0, 1.0, 0.0,
            0.0,  0.0, 0.0, 1.0 );

    mat4 panning = mat4(1.0, 0.0, 0.0 , 0.0,
          0.0, 1.0, 0.0, 0.0,
          0.0, 0.0, 1.0, 0.0,
          panX*(scale+1.0), panY*(scale+1.0), 0.0, 1.0);
    
    mat4 mv = rz*ry*rx;
    float w = 20.0*scale;
    float h = 20.0*scale;
    mat4 projMat = mat4(2.0/w, 0.0,  0.0, 0.0,
                        0.0, 2.0/h,  0.0, 0.0,
                        0.0, 0.0, -2.0/300, 0.0,
                        0.0, 0.0,  0.0, 1.0);
    gl_Position = projMat*panning*mv*vec4(vPosition,1.0);
}
'''

lightFS = '''
# version 330
out vec4 gl_FragColor;

void main(){
    gl_FragColor = vec4(0.0,0.0,1.0,1.0);
}
'''


def flattenlist(data):
    l = []
    for i in data:
        if len(i) > 1:
            for j in i:
                l.append(float(j))
        else:
            l.append(i)
    return l


def orthoMatrix(left, right, bottom, top, near, far):
    w = right - left
    h = top - bottom
    d = far - near
    l = []
    l.append(2.0 / w)
    l.append(0.0)
    l.append(0.0)
    l.append(-(left + right) / w)

    l.append(0.0)
    l.append(2.0 / h)
    l.append(0.0)
    l.append(-(bottom + top) / h)

    l.append(0.0)
    l.append(0.0)
    l.append(-2.0 / d)
    l.append((near + far) / d)

    l.append(0.0)
    l.append(0.0)
    l.append(0.0)
    l.append(1.0)

    #mat = np.array(l)
    # mat =
    # logging.info(mat)
    return l


class globject:

    def __init__(self):
        self.vBuffer = None
        self.iBuffer = None
        self.nBuffer = None
        self.uvBuffer = None
        self.program = None


class GLWidgetQ(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.object = 0
        self.zoom = 1.0
        self.scale = 1.0
        self.aspect = 1.0
        self.panX = 0.0
        self.panY = 0.0
        self.xMov = 0.0
        self.yMov = 0.0
        self.lightPos = [0.0, 0.0, 100.0, 0.0]
        self.sizeDiv = 1.0
        self.lastPos = QtCore.QPoint()
        self.info = False
        self.wireframe = False
        # Object List
        self.objects = []
        # Model Data
        self.verts = []
        self.faces = []

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.0, 0.0, 0.0, 0.2)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.0, 0.0, 0.0, 0.7)

        # Image Props
        self.tex_width = 512
        self.tex_height = 512

        # Model Props
        self.vc = 0
        self.fc = 0

        self.activeTexture = None
        self.textures = []

        # Parent Window
        self.win = self.window()

        # Context Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ctx_menu)

        # Render Attributes
        self.programs = []
        self.theta = [0., 180., 180.]

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGL)
        self.timer.setInterval(20)
        self.timer.start()

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXMov(self, step):
        self.xMov += step / 500.0
        self.updateGL()

    def setYMov(self, step):
        self.yMov += step / 500.0
        self.updateGL()

    def compileShaders(self):
        # Create objects
        program = GL.glCreateProgram()
        vertex = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        fragment = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)

        # Load Sources to Objects
        GL.glShaderSource(vertex, myVS)
        GL.glShaderSource(fragment, myFS)
        # Compile Shaders
        GL.glCompileShader(vertex)
        GL.glCompileShader(fragment)
        # Use Shaders
        GL.glAttachShader(program, vertex)
        GL.glAttachShader(program, fragment)
        # check compilation error
        resultv = GL.glGetShaderiv(vertex, GL.GL_COMPILE_STATUS)
        resultf = GL.glGetShaderiv(fragment, GL.GL_COMPILE_STATUS)
        if not (resultf & resultv):
            raise(RuntimeError(GL.glGetShaderInfoLog(vertex)))
            raise(RuntimeError(GL.glGetShaderInfoLog(fragment)))

        # Dettach Shaders
        # GL.glDetachShader(program, vertex)
        # GL.glDetachShader(program, fragment)

        # Create Texture Program
        texprogram = GL.glCreateProgram()
        vertex1 = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        fragment1 = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        # Load Sources to Objects
        GL.glShaderSource(vertex1, texVS)
        GL.glShaderSource(fragment1, texFS)
        # Compile Shaders
        GL.glCompileShader(vertex1)
        GL.glCompileShader(fragment1)
        # Use Shaders
        GL.glAttachShader(texprogram, vertex1)
        GL.glAttachShader(texprogram, fragment1)
        # check compilation error
        resultv = GL.glGetShaderiv(vertex1, GL.GL_INFO_LOG_LENGTH)
        logging.info(GL.glGetShaderInfoLog(vertex1))
        resultf = GL.glGetShaderiv(fragment1, GL.GL_COMPILE_STATUS)
        logging.info(GL.glGetShaderInfoLog(fragment1))

        # Create Texture Program
        lightprogram = GL.glCreateProgram()
        vertex1 = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        fragment1 = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        # Load Sources to Objects
        GL.glShaderSource(vertex1, lightVS)
        GL.glShaderSource(fragment1, lightFS)
        # Compile Shaders
        GL.glCompileShader(vertex1)
        GL.glCompileShader(fragment1)
        # Use Shaders
        GL.glAttachShader(lightprogram, vertex1)
        GL.glAttachShader(lightprogram, fragment1)
        # check compilation error
        resultv = GL.glGetShaderiv(vertex1, GL.GL_INFO_LOG_LENGTH)
        logging.info(GL.glGetShaderInfoLog(vertex1))
        resultf = GL.glGetShaderiv(fragment1, GL.GL_COMPILE_STATUS)
        logging.info(GL.glGetShaderInfoLog(fragment1))

        # Link Program
        GL.glLinkProgram(texprogram)
        GL.glLinkProgram(program)
        GL.glLinkProgram(lightprogram)

        self.programs.append(program)
        self.programs.append(texprogram)
        self.programs.append(lightprogram)

    def initializeGL(self):
        # Setup Viewport
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glViewport(0, 0, 800, 800)
        self.qglClearColor(self.trolltechPurple.darker())

        self.compileShaders()
        # Setup TExture
        f = open('./resources/2k17.dds', 'rb')
        data = f.read()
        f.close()
        image = dds_file(True, data)
        self.texture_setup(image)
        # setup model
        # verts, norms, faces = self.loadOBJ('blogtext.obj')
        # ob = globject()
        # ob.vBuffer = np.array(verts, dtype=np.float32)
        # ob.vBuffer = glvbo.VBO(ob.vBuffer)
        # ob.vLen = len(verts)
        # ob.iBuffer = np.array(faces, dtype=np.int32)
        # ob.iBuffer = glvbo.VBO(ob.iBuffer, target=GL.GL_ELEMENT_ARRAY_BUFFER)
        # ob.iLen = len(faces) * 3
        # ob.program = self.programs[0]

        # self.objects.append(ob)
        # ob.iBuffer = glvbo.VBO(flattenlist(faces))
        # ob.nBuffer = glvbo.VBO(flattenlist(norms))

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        for ob in self.objects:
            activeBuffers = []
            # GL.glLinkProgram(ob.program)
            GL.glLinkProgram(ob.program)
            GL.glUseProgram(ob.program)
            # logging.info(ob.vBuffer, ob.uvBuffer, ob.nBuffer, ob.iBuffer)

            # Common Uniforms for both shaders
            loc = GL.glGetUniformLocation(ob.program, "aspect")
            GL.glUniform1f(loc, self.aspect)
            # Bind Vertex VBO
            ob.vBuffer.bind()
            activeBuffers.append(ob.vBuffer)
            vpos = GL.glGetAttribLocation(ob.program, "vPosition")
            GL.glVertexAttribPointer(
                vpos, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
            GL.glEnableVertexAttribArray(vpos)

            if ob.program == self.programs[0]:
                # Update Panning
                loc = GL.glGetUniformLocation(ob.program, "panX")
                GL.glUniform1f(loc, self.panX)
                loc = GL.glGetUniformLocation(ob.program, "panY")
                GL.glUniform1f(loc, self.panY)
                # Update Scale in Shader
                loc = GL.glGetUniformLocation(ob.program, "scale")
                GL.glUniform1f(loc, self.zoom)
                # Update Theta in Shader
                loc = GL.glGetUniformLocation(ob.program, "theta")
                GL.glUniform3fv(loc, 1, self.theta)
                # Update Light Position
                loc = GL.glGetUniformLocation(ob.program, "lightPos")
                GL.glUniform4fv(loc, 1, self.lightPos)
            elif ob.program == self.programs[1]:
                # Upate Texture Scale
                loc = GL.glGetUniformLocation(ob.program, "scale")
                GL.glUniform1f(loc, self.scale)

            if ob.uvBuffer:
                # Bind UVs
                ob.uvBuffer.bind()

                uvpos = GL.glGetAttribLocation(ob.program, "uvPosition")
                GL.glVertexAttribPointer(uvpos, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
                GL.glEnableVertexAttribArray(uvpos)
                activeBuffers.append(ob.uvBuffer)

            if ob.nBuffer:
                # Bind Normals
                ob.nBuffer.bind()
                npos = GL.glGetAttribLocation(ob.program, "nPosition")
                GL.glVertexAttribPointer(npos, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
                GL.glEnableVertexAttribArray(npos)
                activeBuffers.append(ob.nBuffer)

            # Bind Indices VBO
            ob.iBuffer.bind()
            activeBuffers.append(ob.iBuffer)

            if not self.wireframe:
                GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
                GL.glPolygonMode(GL.GL_BACK, GL.GL_FILL)

            else:
                GL.glPolygonMode(GL.GL_FRONT, GL.GL_LINE)
                GL.glPolygonMode(GL.GL_BACK, GL.GL_LINE)

            GL.glDrawElements(
                GL.GL_TRIANGLES, ob.iLen, GL.GL_UNSIGNED_INT, None)

            # GL.glDrawArrays(GL.GL_POINTS, 0, ob.vLen)
            # Unbind everything
            for buf in activeBuffers:
                buf.unbind()

            # Render Light
            # if ob.program == self.programs[0]:
            #    self.renderLight()

        # self.renderText(0.5, 0.5, "3dgamedevblog")

    def renderLight(self):
        GL.glUseProgram(self.programs[2])
        # Update Theta in Shader
        loc = GL.glGetUniformLocation(self.programs[2], "theta")
        GL.glUniform3fv(loc, 1, self.theta)
        # Upate Texture Scale
        loc = GL.glGetUniformLocation(self.programs[2], "scale")
        GL.glUniform1f(loc, self.scale)
        # Update
        loc = GL.glGetUniformLocation(self.programs[2], "panX")
        GL.glUniform1f(loc, self.panX)
        loc = GL.glGetUniformLocation(self.programs[2], "panY")
        GL.glUniform1f(loc, self.panY)

        lightvbo = np.array(self.lightPos, dtype=np.float32)
        lightvbo = glvbo.VBO(lightvbo)
        lightvbo.bind()
        vpos = GL.glGetAttribLocation(self.programs[2], "vPosition")
        GL.glVertexAttribPointer(
            vpos, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(vpos)
        GL.glPointSize(10.0)
        GL.glDrawArrays(GL.GL_POINTS, 0, 1)
        GL.glPointSize(1.0)
        lightvbo.unbind()

    def resizeGL(self, width, height):
        side = min(width, height)
        self.aspect = float(width) / height
        # logging.info(self.aspect)
        tex_side = self.tex_width / self.tex_height
        f_height = width / tex_side

        # if self.activeTexture:
        #    GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        # else:
        GL.glViewport(0, 0, width, height)

        # logging.info('Viewport Size: ', width, height, 'Sides: ', side, tex_side,
        #      'Texture Sizes: ', self.tex_width, self.tex_height)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def wheelEvent(self, event):
        self.zoom -= event.delta() * 0.0005
        self.zoom = max(self.zoom, 0.005)
        # logging.info(self.zoom)
        self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if (event.buttons() & QtCore.Qt.LeftButton) and (event.modifiers() & QtCore.Qt.AltModifier):
            self.theta[0] += dy * 0.5
            self.theta[2] += dx * 0.5
        elif (event.buttons() & QtCore.Qt.LeftButton):
            self.theta[0] += dy * 0.5
            self.theta[1] += dx * 0.5
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.panX += dx * 0.005
            self.panY -= dy * 0.005

        self.lastPos = QtCore.QPoint(event.pos())
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_I:
            self.info = not self.info
        elif event.key() == QtCore.Qt.Key_1:
            self.lightPos[2] += 0.5
        elif event.key() == QtCore.Qt.Key_3:
            self.lightPos[2] -= 0.5
        elif event.key() == QtCore.Qt.Key_4:
            self.lightPos[1] += 0.5
        elif event.key() == QtCore.Qt.Key_6:
            self.lightPos[1] -= 0.5
        elif event.key() == QtCore.Qt.Key_7:
            self.lightPos[0] += 0.5
        elif event.key() == QtCore.Qt.Key_9:
            self.lightPos[0] -= 0.5
        elif event.key() == QtCore.Qt.Key_R:
            logging.info(''.join(map, (self.lightPos, self.scale, self.theta)))
        elif event.key() == QtCore.Qt.Key_Plus:
            self.zoom -= 0.5
        elif event.key() == QtCore.Qt.Key_Minus:
            self.zoom += 0.5
        elif event.key() == QtCore.Qt.Key_Space:
            self.wireframe = not self.wireframe

    def cubeDraw(self):
        logging.info('drawingCube')
        # glRotatef(1.0, 3.0, 1.0, 1.0)
        # glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_EMISSION) ;
        # GL.glColorMaterial ( GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE
        # )
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, (0.0, 0.8, 0.8, 1.0))
        # GL.glMaterialfv( GL.GL_FRONT, GL.GL_SPECULAR, (1.0,1.0,1.0,1.0))
        # GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 100.0 );

        dlist = GL.glGenLists(1)
        self.qglColor(QtCore.Qt.red)
        GL.glNewList(dlist, GL.GL_COMPILE)
        GL.glBegin(GL.GL_QUADS)
        self.qglColor(self.trolltechGreen)
        for surface in surfaces:
            for vertex in surface:
                GL.glVertex3fv([v / 3.0 for v in verticies[vertex]])
        GL.glEnd()
        GL.glEndList()
        return dlist

    def customModel(self, args):
        # Get vc and fc
        try:
            verts = args[0]
            faces = args[1]
            uvs = args[2]
            normals = args[3]
        except:
            logging.info('Wrong Arguments')
        self.theta[0] = 90.
        self.theta[1] = 0.

        self.vc = len(verts)
        self.fc = len(faces)

        ob = globject()
        ob.vBuffer = np.array(verts, dtype=np.float32)
        ob.vBuffer = glvbo.VBO(ob.vBuffer)
        ob.vLen = len(verts)
        ob.iBuffer = np.array(faces, dtype=np.int32)
        ob.iBuffer = glvbo.VBO(ob.iBuffer, target=GL.GL_ELEMENT_ARRAY_BUFFER)
        ob.iLen = len(faces) * 3
        # ob.uvBuffer = np.array(uvs, dtype=np.float32)
        # ob.uvBuffer = glvbo.VBO(ob.uvBuffer)
        ob.nBuffer = np.array(normals, dtype=np.float32)
        ob.nBuffer = glvbo.VBO(ob.nBuffer)
        ob.program = self.programs[0]

        # if self.objects:
        #    self.objects.pop()
        self.objects.append(ob)

    def makeTextureQuad(self):
        self.theta[0] = 0.
        ob = globject()
        ob.vBuffer = np.array(quadverts, dtype=np.float32)
        ob.vBuffer = glvbo.VBO(ob.vBuffer)
        ob.vLen = len(quadverts)
        ob.iBuffer = np.array(quadfaces, dtype=np.int32)
        ob.iBuffer = glvbo.VBO(ob.iBuffer, target=GL.GL_ELEMENT_ARRAY_BUFFER)
        ob.iLen = len(quadfaces) * 3
        ob.uvBuffer = np.array(quaduvs, dtype=np.float32)
        ob.uvBuffer = glvbo.VBO(ob.uvBuffer)
        # ob.nBuffer = np.array(quadnorms, dtype=np.float32)
        # ob.nBuffer = glvbo.VBO(ob.nBuffer)
        ob.program = self.programs[1]
        return ob

    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        GL.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        Pi = 3.14159265358979323846
        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * Pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * Pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        GL.glEnd()
        GL.glEndList()

        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.qglColor(self.trolltechGreen)

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x4, y4, -0.05)

        GL.glVertex3d(x4, y4, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.qglColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        GL.glVertex3d(x1, y1, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def texture_setup(self, image_data):
        self.image = image_data
        if not self.image:
            return
        typ = ''.join(self.image.header.ddspf.dwFourCC)
        if typ == 'DX10':
            typ = image_types[self.image.header.dwdx10header.dxgi_format]
        else:
            typ = image_types[typ]

        height = self.image.header.dwHeight
        width = self.image.header.dwWidth

        # use TexProgram
        GL.glUseProgram(self.programs[1])
        self.activeTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.activeTexture)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        self.tex_width = width
        self.tex_height = height
        self.scale = float(width) / height
        self.image.data.seek(0)

        # set class texture size

        GL.glTexParameterf(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameterf(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameterf(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        if not typ:  # normal uncompressed Texture
            buf_size = self.image.header.dwPitchOrLinearSize * height

            if self.image.header.ddspf.dwImageMode == 'BGRA':
                typ = GL.GL_BGRA
            else:
                typ = GL.GL_RGBA

            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 3, width, height, 0,
                            typ, GL.GL_UNSIGNED_BYTE, image_data.data.read(buf_size))
        else:
            buf_size = self.image.header.dwPitchOrLinearSize

            # Remove the swizzle check 2016
            # if ((self.image.header.dwFlags & 0xff000000) >> 24) == 0x80:
            #    logging.info('unswizzling')
            #    self.image.unswizzle_2k()

            GL.glEnable(GL.GL_BLEND)
            GL.glDisable(GL.GL_COLOR_LOGIC_OP)
            '''INVERT COLORS IN CASE OF NORMAL MAPS'''
            if typ == 0x8DBD:
                GL.glEnable(GL.GL_COLOR_LOGIC_OP)
                GL.glLogicOp(GL.GL_COPY_INVERTED)

            # GL.glBlendFunc(GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ZERO)
            GL.glCompressedTexImage2D(
                GL.GL_TEXTURE_2D, 0, typ, width, height, 0, buf_size,
                self.image.data.read(buf_size))

        logging.info(' '.join(map(str, (hex(typ), height, width, hex(buf_size)))))

        # Changing Object
        ob = self.makeTextureQuad()
        self.objects.append(ob)

        # Update View
        self.resizeGL(self.width(), self.height())

    def ctx_menu(self, position):
        menu = QMenu()
        menu.addAction(self.tr('Save Image'))
        # menu.addAction(self.tr('Import Image'))
        # menu.addAction(self.tr('Export Model'))
        menu.addAction(self.tr('Make Coffee'))

        res = menu.exec_(self.mapToGlobal(position))
        if not res:
            return

        if res.text() == 'Save Image':
            logging.info('Saving Image to DDS')
            location = QtGui.QFileDialog.getSaveFileName(
                caption="Save File", filter='*.dds')
            f = open(location[0], 'wb')
            f.write(self.image.write_texture().read())
            f.close()
            # StatusBar notification
            self.window().statusBar.showMessage(
                "Texture Saved to " + str(location[0]))
        elif res.text() == 'Make Coffee':
            logging.info('Making Coffee for buddaking')
            verts, norms, faces = self.loadOBJ('./resources/coffee.obj')
            self.objects = []
            self.customModel([verts, faces, [], norms])

        # elif res.text() == 'Export Model':
        #     logging.info('Saving Model to Wavefront OBJ')
        #     location = QtGui.QFileDialog.getSaveFileName(
        #         caption="Save File", filter='*.obj')
        #     f = open(location[0], 'w')

        #     # writing data
        #     f.write('o custom_mesh \n')
        #     for v in self.verts:
        #         f.write('v ' + ' '.join([str(vi) for vi in v]) + '\n')
        #     f.write('usemtl None \n')
        #     f.write('s off \n')
        #     for face in self.faces:
        #         f.write('f ' + ' '.join([str(fi + 1) for fi in face]) + '\n')

        #     f.close()
        #     # StatusBar notification
        #     self.window().statusBar.showMessage(
        #         "Obj Saved to " + str(location[0]))

    def loadOBJ(self, filename):
        numVerts = 0
        verts = []
        faces = []
        norms = []
        vertsOut = []
        normsOut = []
        for line in open(filename, "r"):
            vals = line.split()
            if vals[0] == "v":
                v = map(float, vals[1:4])
                verts.append(v)
            if vals[0] == "vn":
                n = map(float, vals[1:4])
                norms.append(n)
            if vals[0] == "f":
                vals = [val.split("/")[0] for val in vals[1:4]]
                fa = map(int, vals)
                faces.append([f - 1 for f in fa])
        return verts, norms, faces

    def loadDDS(self, typ, width, height, image):

        if typ == 'DX10':
            typ = image_types[image.header.dwdx10header.dxgi_format]
        else:
            typ = image_types[typ]

        image.data.seek(0)
        if not typ:  # normal uncompressed Texture
            logging.info('Uncompressed Image')
            buf_size = image.header.dwPitchOrLinearSize * height

            if image.header.ddspf.dwImageMode == 'BGRA':
                typ = GL.GL_BGRA
            else:
                typ = GL.GL_RGBA

            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 3, width, height,
                            0, typ, GL.GL_UNSIGNED_BYTE, image.data.read(buf_size))
        else:
            logging.info('Compressed Image')
            buf_size = image.header.dwPitchOrLinearSize
            # logging.info(hex(self.image.header.dwFlags),(self.image.header.dwFlags & 0xff000000)>>24)
            # if ((image.header.dwFlags & 0xff000000)>>24) == 0x80:
            #    image.unswizzle_2k()

            image.data.seek(0)
            GL.glEnable(GL.GL_BLEND)

            GL.glCompressedTexImage2D(
                GL.GL_TEXTURE_2D, 0, typ, width, height, 0, buf_size, image.data.read(buf_size))
            GL.glBlendFunc(GL.GL_ONE_MINUS_DST_COLOR, GL.GL_ZERO)

        # msg=QMessageBox()
        # msg.setText('Done')
        # msg.exec_()
