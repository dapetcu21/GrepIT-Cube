from OpenGL.GL import *
from OpenGL.GLU import *
import random
from math import * # trigonometry

import pygame # just to get a display

import Image
import sys
import time

class GREPEngine(object):
    '''
    Main engine impl
    '''
    def __init__(self, width, height, vertexShader='main_vs.vs', pixelShader='main_ps.ps'):
        self.width = width
        self.height = height
        self.numFrame = 0
        self.pixelShaderFn = pixelShader
        self.vertexShaderFn = vertexShader
        self.paused = False
        self.win = None
        self.font = None

        self.showFps = True
        self.fps = 0
        self.fpsNumFrame = 0
        self.lastFpsDrawTime = time.time()
        self.currentTime = time.time()

        self.caps_override = {}
            
    def Initialize(self):
        print 'Initializing engine...'
        
        pygame.init()
        pygame.display.set_caption('GREPEngine')
        self.win = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)

        # shaders
        self._initShaders()

        print 'Calling init implementation...'
        self.InitImpl()
        
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glCullFace(GL_BACK)
            
    def Shutdown(self):
        pygame.quit()
            
    def run(self):
        done = False
        print 'Entering main loop...'
        while not done:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    done = True
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        done = True
                    else:
                        self.OnKeyPress(e.key)
                if e.type == pygame.KEYUP:
                    self.OnKeyUp(e.key)
            
            glDepthFunc(GL_LEQUAL)
            glShadeModel(GL_SMOOTH)
            glEnable(GL_DEPTH_TEST)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(90, 1, 0.01, 1000)

            # template
            self.OnFrameBegin()

            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # template
            self.OnRender()

            # template
            self.OnFrameEnd()
    
            pygame.display.flip()
            
            self.numFrame += 1
            self.fpsNumFrame += 1
        
                    
    def InitImpl(self):
        pass
            
    def OnFrameBegin(self):
        raise NotImplementedException()
    def OnRender(self):
        raise NotImplementedException()
    def OnFrameEnd(self):
        raise NotImplementedException()

    def OnKeyPress(self, key):
        pass
    def OnKeyUp(self, key):
        pass
            
    def _createAndCompileShader(self, type, source):
        shader = glCreateShader(type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        # get "compile status" - glCompileShader will not fail with
        # an exception in case of syntax errors

        result = glGetShaderiv(shader, GL_COMPILE_STATUS)

        if (result != 1): # shader didn't compile
            raise Exception("Couldn't compile shader\nShader compilation Log:\n" + glGetShaderInfoLog(shader))
        return shader

    def _initShaders(self):
        if self.getCaps('shaders'):
            with open(self.vertexShaderFn) as f:
                vertex_shader = self._createAndCompileShader(GL_VERTEX_SHADER, f.read());

            fragment_shader = None
            with open(self.pixelShaderFn) as f:
                fragment_shader = self._createAndCompileShader(GL_FRAGMENT_SHADER, f.read());

            # build shader program
            program = glCreateProgram()
            glAttachShader(program, vertex_shader)
            glAttachShader(program, fragment_shader)
            glLinkProgram(program)

            # try to activate/enable shader program
            # handle errors wisely

            try:
                glUseProgram(program)
            except OpenGL.error.GLError:
                print glGetProgramInfoLog(program)
                raise

            self.shaderProgram = program
        else:
            raise Exception('This demo requires shaders')

    def forceDisableCaps(self, capabilityName):
        self.caps_override[capabilityName] = True
            
    def getCaps(self, capabilityName):
        try:
            if self.caps_override[capabilityName] == True:
                    return False
        except:
            pass
        if capabilityName == 'shaders':
            return bool(glCreateShader)
        return True
