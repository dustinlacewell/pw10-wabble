from math import cos, hypot, pi, sin
from random import Random, randint, uniform

import pyglet
from pyglet.gl import *

import shader

def _buildBallShader():
    ball_shader = shader.ShaderProgram(
     shader.VertexShader("""
        void main(){
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }"""
     ),
     shader.FragmentShader("""
        uniform vec3 rgb;
        uniform vec2 position;
        uniform vec3 core_rgb;
        uniform vec2 core_position;
        uniform float core_radius;
        
        void main(){
            //Calulate radial influence.
            float influence = min(1.0, max(0.0, 1.0 - ((core_radius / 2.0) / sqrt(
             pow((position.x - core_position.x), 2.0) +
             pow((position.y - core_position.y), 2.0)
            ))));
            
            //Calculate inverse square for opacity, with a quantizing twist.
            float alpha = min(1.0, 1.0 / sqrt(
             pow((position.x - gl_FragCoord.x), 2.0) +
             pow((position.y - gl_FragCoord.y), 2.0)
            ));
            
            float brightness_mod = 0.0;
            if(alpha > 0.75){
                brightness_mod = 1.0 + (alpha - 0.75) / 2.0;
            }
            
            if(alpha > 0.2){
                alpha = min(0.8, alpha * 1.5);
            }
            
            gl_FragColor = vec4(
             min(1.0, ((1.0 - influence) * core_rgb.r + influence * rgb.r) * brightness_mod),
             min(1.0, ((1.0 - influence) * core_rgb.g + influence * rgb.g) * brightness_mod),
             min(1.0, ((1.0 - influence) * core_rgb.b + influence * rgb.b) * brightness_mod),
             min(1.0, alpha)
            );
        }"""
     )
    )
    _shader_message = ball_shader.link()
    if _shader_message:
        print _shader_message
    return ball_shader
    
def _buildBallVertices(sides, radius):
    vertices = [0.0, 0.0]
    for i in range(0, 360, 360 / sides):
        i_rad = i * (pi / 180.0)
        vertices += [radius * cos(i_rad), radius * sin(i_rad)]
    vertices += vertices[2:4] #Close the shape.
    return (GLfloat * len(vertices))(*vertices)
    
    
class Blob(object):
    x = None
    y = None
    vec_x = None
    vec_y = None
    root_x = None
    root_y = None
    wander_limit = None
    acceleration_cap = None
    vertices = None
    sides = None
    r = None
    g = None
    b = None
    max_r = None
    max_g = None
    max_b = None
    radius = None
    
    def __init__(self,
     x, y,
     wander_limit=0.0, acceleration_cap=0.0,
     vec_x=0.0, vec_y=0.0,
     sides=7, radius=6.0,
     r=0.25, g=0.25, b=0.05
    ):
        self.x = x
        self.y = y
        self.vec_x = vec_x
        self.vec_y = vec_y
        self.wander_limit = wander_limit
        self.acceleration_cap = acceleration_cap
        self.vertices = _buildBallVertices(sides, radius)
        self.sides = len(self.vertices) // 2
        self.r = r
        self.g = g
        self.b = b
        self.max_r = min(1.0, r * 1.5)
        self.max_g = min(1.0, g * 1.5)
        self.max_b = min(1.0, b * 1.5)
        self.radius = radius
        
    def setRoot(self, x, y):
        self.root_x = x
        self.root_y = y
        
    def tick(self, rnd, colour_rnd):
        old_x = self.x
        old_y = self.y
        accel = self.acceleration_cap
        
        self.r = max(self.max_r * 0.5, min(self.max_r, self.r + colour_rnd.uniform(-0.01, 0.01)))
        self.g = max(self.max_g * 0.5, min(self.max_g, self.g + colour_rnd.uniform(-0.01, 0.01)))
        self.b = max(self.max_b * 0.5, min(self.max_b, self.b + colour_rnd.uniform(-0.01, 0.01)))
        
        if self.wander_limit:
            self.x += self.vec_x
            
            if abs(self.root_x - self.x) >= self.wander_limit:
                if (self.root_x < self.x and self.vec_x > 0) or (self.root_x > self.x and self.vec_x < 0):
                    self.vec_x *= -1.0
            if abs(self.root_y - self.y) >= self.wander_limit:
                if (self.root_y < self.y and self.vec_y > 0) or (self.root_y > self.y and self.vec_y < 0):
                    self.vec_y *= -1.0
                    
            self.x += self.vec_x
            self.y += self.vec_y
            
            if self.vec_x > 0:
                self.vec_x = min(self.vec_x + rnd.uniform(-accel / 2.0, accel), accel)
            else:
                self.vec_x = max(self.vec_x + rnd.uniform(-accel, accel / 2.0), -accel)
            if self.vec_y > 0:
                self.vec_y = min(self.vec_y + rnd.uniform(-accel / 2.0, accel), accel)
            else:
                self.vec_y = max(self.vec_y + rnd.uniform(-accel, accel / 2.0), -accel)
                
        #return [old_x, old_y, self.x, self.y]
        
class BlobGroup(object):
    blobs = None
    
    rnd = None
    
    ball_shader = _buildBallShader()
    
    def __init__(self, seed=0):
        print 'wtf'
        self.rnd = Random(seed)
        
        self.blobs = []
        
        #self.ball_shader = _buildBallShader()
        
    def addBlob(self, blob):
        self.blobs.append(blob)
        
    def removeBlob(self, blob):
        if blob in self.blobs:
            self.blobs.remove(blob)
            return True
        return False
        
    def tick(self):
        _rnd = self.rnd
        _colour_rnd = Random()
        
        for ball in self.blobs:
            ball.tick(_rnd, _colour_rnd)
            #ball.tick(_rnd, _colour_rnd)
            
    def draw(self, width, height):
        _ball_shader = self.ball_shader
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, width, 0.0, height)
        glScalef(1.0, 1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        if self.blobs:
            _ball_shader.enable()
            
            blob = self.blobs[0]
            _ball_shader.setUniform_vec3('core_rgb', blob.r, blob.g, blob.b)
            _ball_shader.setUniform_vec2('core_position', blob.x, blob.y)
            _ball_shader.setUniform_float('core_radius', blob.radius)
            
            for blob in self.blobs:
                _ball_shader.setUniform_vec3('rgb', blob.r, blob.g, blob.b)
                _ball_shader.setUniform_vec2('position', blob.x, blob.y)
                
                glVertexPointer(2, GL_FLOAT, 0, blob.vertices)
                glLoadIdentity()
                glTranslatef(blob.x, blob.y, 0.0)
                glDrawArrays(GL_TRIANGLE_FAN, 0, blob.sides)
            _ball_shader.disable()
            
        glDisableClientState(GL_VERTEX_ARRAY)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
