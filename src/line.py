from src.util import gradient

from math import cos, hypot, pi, sin
from random import Random, randint, uniform

import pyglet
from pyglet.gl import *
import config
import glsl.shader as shader

def _buildLaserShader():
    laser_shader = shader.ShaderProgram(
     shader.VertexShader("""
        void main(){
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }"""
     ),
     shader.FragmentShader("""
        uniform vec2 position;
        uniform vec2 core_position;
        uniform vec2 random;
        uniform int enable_intensity;
        uniform int horizontal;
        
        void main(){
            float red = 0.0;
            float player_distance = 0.0;
            if(horizontal == 1){
                red = mod(((position.x + random.x) * gl_FragCoord.y) + gl_FragCoord.x, 8.0) * 64.0; 
                red = max(50.0, min(255.0, red + 30.0));
            }else{
                red = mod(((position.y + random.y) * gl_FragCoord.x) + gl_FragCoord.y, 8.0) * 64.0; 
                red = max(50.0, min(255.0, red + 30.0));
            }
            
            if (enable_intensity == 1){
                player_distance = sqrt(
                 pow((position.x - core_position.x), 2.0) +
                 pow((position.y - core_position.y), 2.0)
                );
            }
            red = max(0.0, red - max(25.0, player_distance - 130.0));
            
            gl_FragColor = vec4(red / 255.0, 0.0, 0.0, 0.75);
        }"""
     )
    )
    _shader_message = laser_shader.link()
    if _shader_message and __debug__:
        print _shader_message
    return laser_shader
    
class Laser(object):
    LENGTH = 30
    SPEED = 150
    
    laser_fx = pyglet.media.load('dat/audio/fx/laser.mp3', streaming=False) if config.options['USE_SOUND'] else None

    
    def __init__(self, group, x1, y1, x2, y2):
        # TODO: add asserts
        assert(x1 <= x2)
        assert(y1 <= y2)
        
        self.group = group
        
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        #self.v1 = x2 - x1
        #self.v2 = y2 - y1
        #self.length_sq = float(self.v1 * self.v1 + self.v2 * self.v2)
        self.play_fx()
        
    def play_fx(self):
        if config.options['USE_SOUND']:
            player = pyglet.media.Player()
            player.queue(self.laser_fx)
            player.volume = 0.1
            player.play()
        
class HorizontalLaser(Laser):
    def __init__(self, group, y_pos):
        x1 = 0
        x2 = self.LENGTH
        y1 = y2 = y_pos
        super(HorizontalLaser, self).__init__(group, x1, y1, x2, y2)
        self.forward = True
        group.addHorizontalLaser(self)
        
    def __slot(self):
        return self.y1
    slot =property(__slot)
    
    def delete(self):
        self.group.removeHorizontalLaser(self)
        
    def update(self, dt):
        if self.forward:
            pc = dt * self.SPEED
            self.x1 += pc
            self.x2 += pc
            if self.x2 >= 600:
                self.forward = False
                self.x1 = 600 - self.LENGTH
                self.x2 = 600
                self.play_fx()
        else:
            pc = dt * self.SPEED
            self.x1 -= pc
            self.x2 -= pc
            if self.x1 <= 0:
                self.forward = True
                self.x1 = 0
                self.x2 = self.LENGTH
                self.play_fx()
                
class VerticalLaser(Laser):
    def __init__(self, group, x_pos):
        y1 = 0
        y2 = self.LENGTH
        x1 = x2 = x_pos
        super(VerticalLaser, self).__init__(group, x1, y1, x2, y2)
        self.forward = True
        group.addVerticalLaser(self)
        
    def __slot(self):
        return self.y1
    slot =property(__slot)
    
    def delete(self):
        self.group.removeVerticalLaser(self)
        
    def update(self, dt):
        if self.forward:
            pc = dt * self.SPEED
            self.y1 += pc
            self.y2 += pc
            if self.y2 >= 600:
                self.forward = False
                self.y1 = 600 - self.LENGTH
                self.y2 = 600
                self.play_fx()
        else:
            pc = dt * self.SPEED
            self.y1 -= pc
            self.y2 -= pc
            if self.y1 <= 0:
                self.forward = True
                self.y1 = 0
                self.y2 = self.LENGTH
                self.play_fx()
                
class LaserGroup(object):
    horizontal_lasers = None
    vertical_lasers = None
    laser_shader = None
    if config.options['SHADE_LASERS']:
        laser_shader = gl_info.have_version(2) and _buildLaserShader()
    
    def __init__(self):
        horizontal_vertices = [-15.0, -1.5] + [15.0, -1.5] + [15.0, 1.5] + [-15.0, 1.5]
        self.laser_horizontal = (GLfloat * len(horizontal_vertices))(*horizontal_vertices)
        
        vertical_vertices = [-1.5, -15.0] + [1.5, -15.0] + [1.5, 15.0] + [-1.5, 15.0]
        self.laser_vertical = (GLfloat * len(vertical_vertices))(*vertical_vertices)
        
        self.horizontal_lasers = []
        self.vertical_lasers = []
        
    def addHorizontalLaser(self, laser):
        self.horizontal_lasers.append(laser)
        
    def addVerticalLaser(self, laser):
        self.vertical_lasers.append(laser)
        
    def removeHorizontalLaser(self, laser):
        self.horizontal_lasers = [l for l in self.horizontal_lasers if not l == laser]
        
    def removeVerticalLaser(self, laser):
        self.vertical_lasers = [l for l in self.vertical_lasers if not l == laser]
        
    def update(self, dt):
        for laser in self.horizontal_lasers + self.vertical_lasers:
            laser.update(dt)
            
    def draw(self, width, height, player_x, player_y, enable_intensity):
        _laser_shader = self.laser_shader
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, width, 0.0, height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        if self.horizontal_lasers or self.vertical_lasers:
            if _laser_shader:
                _laser_shader.enable()
                
                _laser_shader.setUniform_vec2('core_position', player_x, player_y)
                _laser_shader.setUniform_vec2('random', uniform(-8.0, 8.0), uniform(-8.0, 8.0))
                _laser_shader.setUniform_int('enable_intensity', int(enable_intensity))
                _laser_shader.setUniform_int('horizontal', 1)

            else:
                glColor3f(1.0, 0.0, 0.0)
                
            glVertexPointer(2, GL_FLOAT, 0, self.laser_horizontal)
            for laser in self.horizontal_lasers:
                centre_x = (laser.x1 + laser.x2) / 2
                if _laser_shader:
                    _laser_shader.setUniform_vec2('position', centre_x, laser.y1)
                else:
                    if enable_intensity:
                        glColor3f((255.0 - max(25.0, ((((centre_x - player_x) ** 2) + ((laser.y1 - player_y) ** 2)) ** 0.5) - 130.0)) / 255.0, 0.0, 0.0)
                        
                glLoadIdentity()
                glTranslatef(centre_x, laser.y1, 0.0)
                glDrawArrays(GL_QUADS, 0, 4)
                
            if _laser_shader:
                _laser_shader.setUniform_int('horizontal', 0)
                
            glVertexPointer(2, GL_FLOAT, 0, self.laser_vertical)
            for laser in self.vertical_lasers:
                centre_y = (laser.y1 + laser.y2) / 2
                if _laser_shader:
                    _laser_shader.setUniform_vec2('position', laser.x1, centre_y)
                else:
                    if enable_intensity:
                        glColor3f((255.0 - max(25.0, ((((laser.x1 - player_x) ** 2) + ((centre_y - player_y) ** 2)) ** 0.5) - 130.0)) / 255.0, 0.0, 0.0)
                        
                glLoadIdentity()
                glTranslatef(laser.x1, centre_y, 0.0)
                glDrawArrays(GL_QUADS, 0, 4)
                
            if _laser_shader:
                _laser_shader.disable()
            else:
                glColor3f(1.0, 1.0, 1.0)
                
        glDisableClientState(GL_VERTEX_ARRAY)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
