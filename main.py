from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import math

import random
from math import * # trigonometry
import time

from core import *

class Cube:
    def __init__(self,x,y,z,texid):
        self.rx = 0
        self.ry = 0
        self.rz = 0
        
        self.px = x
        self.py = y
        self.pz = z

        self.tex = texid
    def render(self):
        glPushMatrix()
        glTranslate(self.px,self.py,self.pz)
        glRotate(self.rx,1,0,0)
        glRotate(self.ry,0,1,0)
        glRotate(self.rz,0,0,1)

        glBindTexture(GL_TEXTURE_2D, self.tex)
                        
        glBegin(GL_QUADS)

        #glColor3ub(213,17,27)
        #glColor3f(0.83,0.06,0.10)
        #glTexCoord2f(0,0)
        glNormal3f(0, 0, -1)
        glVertex3f( -1, -1, -1)
        glVertex3f( 1, -1, -1)
        glVertex3f( 1, 1, -1)
        glVertex3f( -1, 1, -1)

        #glColor3ub(255,128,0)
        #glColor3f(1,0.50,0)           
        #glTexCoord2f(1,0)
        glNormal3f(0, 0, 1)
        glVertex3f( -1, -1, 1)
        glVertex3f( 1, -1, 1)
        glVertex3f( 1, 1, 1)
        glVertex3f( -1, 1, 1)

        #glColor3ub(0,128,255)
        #glColor3f(0,0.50,1)
        #glTexCoord2f(0.5,0)
        glNormal3f(0, -1, 0)
        glVertex3f( -1, -1, -1)
        glVertex3f( 1, -1, -1)
        glVertex3f( 1, -1, 1)
        glVertex3f( -1, -1, 1)

        #glColor3ub(70,225,4)
        #glColor3f(0.27,1,0.01)
        #glTexCoord2f(0,1)
        glNormal3f(0, 1, 0)
        glVertex3f( -1, 1, -1)
        glVertex3f( 1, 1, -1)
        glVertex3f( 1, 1, 1)
        glVertex3f( -1, 1, 1)

        #glColor3ub(255,255,0)
        #glColor3f(1,1,0)
        #glTexCoord2f(0.5,1)
        glNormal3f(-1, 0, 0)
        glVertex3f( -1, -1, -1)
        glVertex3f( -1, 1, -1)
        glVertex3f( -1, 1, 1)
        glVertex3f( -1, -1, 1)

        #glColor3ub(255,255,255)
        #glColor3f(1,1,1)
        #glTexCoord2f(1,1)
        glNormal3f(1, 0, 0)
        glVertex3f( 1, -1, -1)
        glVertex3f( 1, 1, -1)
        glVertex3f( 1, 1, 1)
        glVertex3f( 1, -1, 1)
        
        glEnd()
        glPopMatrix()

class Matrix:
    animations = []
    def __init__(self):
        self.m = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        self.animations = []

    def rotate(self,cutoff,angle,x,y,z):
        a = {'obj':self, 'co':cutoff, 'crr':0, 'ang':angle, 'x':x, 'y':y, 'z':z}
        Matrix.animations.append(a)
        self.animations.append(a)

    def rotateNow(self,angle,x,y,z):
        glPushMatrix()
        glLoadMatrixf(self.m)
        glRotate(angle,x,y,z)
        self.m = glGetDoublev(GL_MODELVIEW_MATRIX)
        glPopMatrix()

    def mult(self):
        glMultMatrixf(self.m)
        i = len(self.animations) 
        while i:
            a = self.animations[i-1]
            glRotate(a['crr'],a['x'],a['y'],a['z'])
            i-=1
                
def animateMatrices(time):
    d = []
    for a in Matrix.animations:
        a['crr']=lowPass(a['crr'],a['ang'],time,a['co'])
        if abs(a['ang']-a['crr'])<=0.01:
            d.append(a)

    for a in d:
        a['obj'].rotateNow(a['ang'],a['x'],a['y'],a['z'])
        a['obj'].animations.remove(a)
        Matrix.animations.remove(a)

def lowPass(var,newval,period,cutoff):
    RC=1.0/cutoff
    alpha=period/(period+RC)
    return newval * alpha + var * (1.0 - alpha)

def wrap(x,y):
    z = math.fmod(x,y)
    if (z<0):
        z+=y
    return z

def swap(v,p1,p2):
    aux = v[p2]
    v[p2] = v[p1]
    v[p1] = aux

class MyEngine(GREPEngine):
    def __init__(self):
        super(MyEngine, self).__init__(800, 600)

        self.animFrame = 0
        self.lastAnimTime = 0
        self.animationTime = 0
        self.peekX = 0
        self.peekY = 0
        self.peekXC = 0
        self.peekXC = 0

        self.rotMatrix = Matrix()
                
        self.shaderColor = -1
        self.lightColor = [0,0,1]
        self.lightCounter = 0
        self.lightColors = [[0,0,1],[0,1,0],[1,0,0]]
        self.lastT = 1

    def loadImage( self, imageName = "tex.bmp" ):
        im = Image.open(imageName)
        try:
            ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
        except SystemError:
            ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)

        ID = glGenTextures(1)

        glActiveTexture(GL_TEXTURE0); # use first texturing unit
        glBindTexture( GL_TEXTURE_2D, ID );

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        return ID
        
    def InitImpl(self):
        self.shaderColor = glGetUniformLocation(self.shaderProgram,"phColor")
        
        self.cubes={}
        self.cubetex=self.loadImage("tex.bmp");
        self.peekXC = 0
        self.peekYC = 0

        self.rotationMatrix = Matrix()

        for x in range(-1,2):
            self.cubes[x] = {}
            for y in range(-1,2):
                self.cubes[x][y]={}
                for z in range(-1,2):
                    self.cubes[x][y][z] = Cube(x*2.5,y*2.5,z*2.5,self.cubetex)

    def OnFrameBegin(self):
        tt = time.time()
        self.animationElapsed = tt-self.lastAnimTime
        if not self.paused:
                self.animationTime += self.animationElapsed
                animateMatrices(self.animationElapsed)
        else:
                self.animationElapsed = 0
        self.lastAnimTime = tt
        
        t = self.animationTime*60
        st = sin(t/100.0)
        ct = cos(t/100.0)
        gluLookAt(st,ct, -12, 0, 0, 0, 0, 1, 0)
        
        self.ld = [sin(t/32.0)*6.0, sin(t/40.0)*6.0, cos(t/32.0)*6.0]
        self.colorQuantum = (sin(t/20.0)+1)/2
        if (sin(self.lastT/20.0)+1)/2<=0.01 and (sin(t/20.0)+1)/2>0.01:
            self.lightCounter+=1
            if self.lightCounter>=len(self.lightColors):
                self.lightCounter = 0
            self.lightColor = self.lightColors[self.lightCounter]
        self.lastT = t;
    
    def OnRender(self):
        
        glLightfv(GL_LIGHT0, GL_POSITION, self.ld)
        glLightfv(GL_LIGHT1, GL_POSITION, [0,0,0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [1, 1, 1, 1])

        glUniform4f(self.shaderColor,self.lightColor[0]*self.colorQuantum,self.lightColor[1]*self.colorQuantum,self.lightColor[2]*self.colorQuantum,1)
        
        glEnable(GL_LIGHT1)
        gd = 3

        glBegin(GL_QUADS)
        
        glVertex3f(-10,-10,10)
        glVertex3f(10,-10,10);
        glVertex3f(10,-10,-10);
        glVertex3f(-10,-10,-10);


        glVertex3f(-10,-10,-10);
        glVertex3f(10,-10,-10);
        glVertex3f(10,-10,10);
        glVertex3f(-10,-10,10)
        
        
        glEnd()
        
        glEnable(GL_TEXTURE_2D)
        glPushMatrix()
        self.peekXC = lowPass(self.peekXC, self.peekX*100*math.pi/6, self.animationElapsed, 5.0)
        glRotate(self.peekXC,1,0,0)
        self.peekYC = lowPass(self.peekYC, self.peekY*100*math.pi/6, self.animationElapsed, 5.0)
        glRotate(self.peekYC,0,1,0)

        self.rotMatrix.mult()

        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    self.cubes[x][y][z].render()
        glPopMatrix()

    def OnFrameEnd(self):
        if not self.paused:
            self.animFrame += 1

    def rotateX(self,i):
        self.rotMatrix.rotate(5.0,-90*i,0,1,0)

    def rotateY(self,i):
        self.rotMatrix.rotate(5.0,90*i,1,0,0)                
            
    def OnKeyPress(self, key):
        if key == pygame.K_i:
            self.peekX = 1
        if key == pygame.K_k:
            self.peekX = -1
        if key == pygame.K_j:
            self.peekY = -1
        if key == pygame.K_l:
            self.peekY = 1
        if key == pygame.K_SPACE:
            self.paused = not self.paused

        if key == pygame.K_LEFT:
            self.rotateX(-1)
        if key == pygame.K_RIGHT:
            self.rotateX(1)
        if key == pygame.K_UP:
            self.rotateY(-1)
        if key == pygame.K_DOWN:
            self.rotateY(1)

        if key == pygame.K_a:
            self.rotateFace(1)
                    
    def OnKeyUp(self, key):
        if key == pygame.K_i:
            self.peekX = 0
        if key == pygame.K_k:
            self.peekX = 0
        if key == pygame.K_j:
            self.peekY = 0
        if key == pygame.K_l:
            self.peekY = 0
                
def main():
    core = MyEngine()
    core.Initialize()

    core.run()

    core.Shutdown()

if __name__ == 'main':
    main()
