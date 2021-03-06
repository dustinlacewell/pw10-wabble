from math import cos, hypot, pi, sin
from random import Random, randint, uniform

import pyglet
from pyglet.gl import *

import shader
import config

def _buildBallShader():
    ball_shader = shader.ShaderProgram(
     shader.VertexShader("""
        void main(){
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }"""
     ),
     shader.FragmentShader("""
        uniform vec2 position;
        uniform float radius;
        uniform vec3 rgb;
        uniform vec3 shimmer;
        uniform vec2 core_position;
        uniform float core_radius;
        
        const float border_width = 1.2;
        const float shimmer_radius = 1.75;
        
        void main(){
            float r = rgb.r;
            float g = rgb.g;
            float b = rgb.b;
            
            //Calculate distance from centre of current blob.
            float distance = sqrt(
             pow((position.x - gl_FragCoord.x), 2.0) +
             pow((position.y - gl_FragCoord.y), 2.0)
            );
            
            //Calculate distance from core blob.
            float core_distance = sqrt(
             pow((core_position.x - gl_FragCoord.x), 2.0) +
             pow((core_position.y - gl_FragCoord.y), 2.0)
            );
            
            if(core_distance >= core_radius - border_width && abs(distance - radius) <= border_width){
                gl_FragColor = vec4(
                 min(1.0, r * 2.0),
                 min(1.0, g * 2.0),
                 min(1.0, b * 2.0),
                 0.95
                );
            }else{
                //Brighten the core of each blob.
                float brightness_mod = 0.05;
                if(distance < 0.75){//Draw a bright dot right in the centre.
                    brightness_mod = 0.25 + sqrt(1.0 / distance);
                }else{//Apply shimmer.
                    float shimmer_x = mod(gl_FragCoord.x + shimmer.x, shimmer[2]);
                    float shimmer_y = mod(gl_FragCoord.y + shimmer.y, shimmer[2]);
                    if(shimmer_x >= shimmer[2] - shimmer_radius){
                        shimmer_x -= shimmer[2] + shimmer_radius;
                    }
                    if(shimmer_y >= shimmer[2] - shimmer_radius){
                        shimmer_y -= shimmer[2] + shimmer_radius;
                    }
                    
                    float shimmer_distance = sqrt(pow(shimmer_x, 2.0) + pow(shimmer_y, 2.0));
                    
                    if(shimmer_distance <= shimmer_radius){
                        brightness_mod += min(0.9, sqrt(
                            shimmer_distance / shimmer_radius
                        ));
                    }else{
                        brightness_mod = 0.3;
                        r = 0.4;
                        g = 0.0;
                        b = 0.6;
                    }
                }
                
                gl_FragColor = vec4(
                 min(1.0, r * brightness_mod),
                 min(1.0, g * brightness_mod),
                 min(1.0, b * brightness_mod),
                 0.95
                );
            }
        }"""
     )
    )
    _shader_message = ball_shader.link()
    if _shader_message and __debug__:
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
    vec_x = 0.0
    vec_y = 0.0
    
    def __init__(self,
     x, y,
     wander_limit=0.0,
     acceleration_max=0.0, acceleration_min=0.0,
     sides=7, radius=6.0,
     initial_accelleration=0.0,
    ):
        self.x = x
        self.y = y
        self.wander_limit = wander_limit
        self.acceleration_max = acceleration_max
        self.acceleration_min = acceleration_min
        self.acceleration = initial_accelleration
        self.vertices = _buildBallVertices(sides, radius)
        self.sides = len(self.vertices) // 2
        self.radius = radius
        
    def tick(self, rnd, root_x, root_y):
        if self.wander_limit:
            old_x = self.x
            old_y = self.y
            accel = self.acceleration = max(self.acceleration_min, self.acceleration * 0.975)
            
            vec_x = self.vec_x
            vec_y = self.vec_y
            
            if abs(root_x - self.x) >= self.wander_limit:
                if (root_x < self.x and vec_x > 0) or (root_x > self.x and vec_x < 0):
                    vec_x *= -1.0
            if abs(root_y - self.y) >= self.wander_limit:
                if (root_y < self.y and vec_y > 0) or (root_y > self.y and vec_y < 0):
                    vec_y *= -1.0
                    
            self.x += vec_x
            self.y += vec_y
            
            if vec_x > 0:
                vec_x = min(vec_x + rnd.uniform(-accel / 2.0, accel), accel)
            else:
                vec_x = max(vec_x + rnd.uniform(-accel, accel / 2.0), -accel)
            if self.vec_y > 0:
                vec_y = min(vec_y + rnd.uniform(-accel / 2.0, accel), accel)
            else:
                vec_y = max(vec_y + rnd.uniform(-accel, accel / 2.0), -accel)
                
            self.vec_x = vec_x
            self.vec_y = vec_y
            
class BlobGroup(object):
    
    blobs = None
    rnd = None
    colour = None
    
    ball_shader = None
    if config.options['SHADE_BLOBS']:
        ball_shader = gl_info.have_version(2) and _buildBallShader()
    
    x = None
    y = None
    
    def __init__(self, x, y, core_radius, colour, seed=None):
        self.colour = colour
        self.x = x
        self.y = y
        self.core_radius = core_radius
        
        if seed is None:
            import time
            self.rnd = Random(time.time())
        else:
            self.rnd = Random(seed)
            
        self.blobs = []
        
    def offsetPosition(self, x, y):
        if x or y:
            self.x += x
            self.y += y
            for blob in self.blobs:
                blob.x += x
                blob.y += y
                blob.acceleration = blob.acceleration_max
                
    def setPosition(self, x, y):
        self.x = x
        self.y = y
        for blob in self.blobs:
            blob.x = x
            blob.y = y
            blob.acceleration = blob.acceleration_max
            
    def addBlob(self, blob):
        self.blobs.append(blob)
        
    def tick(self):
        rnd = self.rnd
        root_x = self.x
        root_y = self.y
        
        for ball in self.blobs:
            ball.tick(rnd, root_x, root_y)
            
    def draw(self, width, height):
        _ball_shader = self.ball_shader
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, width, 0.0, height)
        #glScalef(1.0, 1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        if self.blobs:
            if _ball_shader:
                _ball_shader.enable()
                
                _ball_shader.setUniform_vec3('rgb', *self.colour)
                _ball_shader.setUniform_vec3('shimmer', uniform(-5.0, 5.0), uniform(-5.0, 5.0), uniform(10.0, 50.0))
                _ball_shader.setUniform_vec2('core_position', self.x, self.y)
                _ball_shader.setUniform_float('core_radius', self.core_radius)
            else:
                glColor3f(*[0.8 * c for c in self.colour])
                
            for blob in self.blobs:
                if _ball_shader:
                    _ball_shader.setUniform_vec2('position', blob.x, blob.y)
                    _ball_shader.setUniform_float('radius', blob.radius)
                    
                glVertexPointer(2, GL_FLOAT, 0, blob.vertices)
                glLoadIdentity()
                glTranslatef(blob.x, blob.y, 0.0)
                glDrawArrays(GL_TRIANGLE_FAN, 0, blob.sides)
                
            if _ball_shader:
                _ball_shader.disable()
            else:
                glColor3f(1.0, 1.0, 1.0)
                
        glDisableClientState(GL_VERTEX_ARRAY)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
