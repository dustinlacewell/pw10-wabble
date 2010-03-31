"""
module: shader

Purpose
=======
 Convenience functions and management for GLSL shaders.
 
Legal
=====
 Copyright (c) 2010, Jonathan Hartley, Neil Tallim
 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.
     * The names of its contributors may not be used to endorse or promote
       products derived from this software without specific prior written
       permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from ctypes import (
    byref, c_char, c_char_p, c_int, c_float, cast, create_string_buffer,
    pointer, POINTER
)
from pyglet.gl import *

_SHADER_ERRORS = {
 GL_INVALID_VALUE: 'GL_INVALID_VALUE (bad 1st arg)',
 GL_INVALID_OPERATION: 'GL_INVALID_OPERATION (bad id or immediate mode drawing in progress)',
 GL_INVALID_ENUM: 'GL_INVALID_ENUM (bad 2nd arg)',
} #: A collection of error-value-to-human-readable-string mappings.

class _Shader(object):
    """
    A wrapper for a GLSL shader, which is part of a GLSL program.
    """
    _id = None #: The ID of the compiled GLSL shader managed by this object.
    _shader_type = None #: The type of shader represented by this object.
    _sources = None #: A list of strings made up of GLSL source code.
    
    def __init__(self, sources):
        """
        Accepts source code for a GLSL shader.
        
        @type sources: basestring|sequence
        @param sources: One or many GLSL shader elements in source form.
        """
        assert (
         isinstance(sources, basestring) or
         type(sources) in (list, tuple) and
         not [None for source in sources if not isinstance(source, basestring)]
        )
        
        if isinstance(sources, basestring):
            self._sources = (sources,)
        else:
            self._sources = tuple(sources)
        self._id = None
        
    def _get(self, param_id):
        """
        Requests a specific detail about the shader element managed by this
        object.
        
        @type param_id: GLenum
        @param param_id: The type of parameter being looked up; allowed values:
            C{GL_SHADER_TYPE}, C{GL_DELETE_STATUS}, C{GL_COMPILE_STATUS},
            C{GL_INFO_LOG_LENGTH}, C{GL_SHADER_SOURCE_LENGTH}
        
        @rtype: GLint
        @return: A pointer to the requested information
        
        @raise ValueError: It was impossible to look up the requested parameter.
        """
        outvalue = c_int(0)
        glGetShaderiv(self._id, param_id, byref(outvalue))
        value = outvalue.value
        if value in _SHADER_ERRORS:
            raise ValueError('%(message)s from glGetShader(%(id)s, %(param_id)s, &value)' % {
             'message': _SHADER_ERRORS[value],
             'id': self._id,
             'param_id': param_id,
            })
        return value
        
    def _getInfoLogLength(self):
        """
        Provides the length of the GLSL compilation log.
        
        @rtype: GLint
        @return: The length of the log.
        
        @raise ValueError: It was impossible to resolve the log length.
        """
        return self._get(GL_INFO_LOG_LENGTH)
        
    def _srcToArray(self):
        """
        Groups all shader element source managed by this object into a single
        array for compilation.
        
        @rtype: tuple(2)
        @return: The number of elements, and a pointer to the character array.
        """
        count = len(self._sources)
        all_source = (c_char_p * count)(*self._sources)
        return (count, cast(pointer(all_source), POINTER(POINTER(c_char))))
        
    def compile(self):
        """
        Compiles the GLSL shader source managed by this object, producing a GLSL
        shader element.
        
        This function is not meant to be called by developers; it is invoked
        automatically by L{ShaderProgram.link}().
        
        @raise CompileError: Something went wrong during compilation.
        @raise ValueError: It was impossible to determine the compilation state.
        """
        self._id = glCreateShader(self._shader_type)
        (count, source) = self._srcToArray()
        glShaderSource(self._id, count, source, None)
        glCompileShader(self._id)
        
        if not self.getCompileStatus():
            raise CompileError(self.getInfoLog())
            
    def destroy(self):
        """
        Releases this GLSL shader from OpenGL's memory.
        
        Note that no active GLSL programs will be directly affected by this
        action and that this shader will continue to consume resources until it
        is no longer in use.
        """
        glDeleteShader(self._id)
        
    def flushSource(self):
        """
        Allows the GLSL source strings managed by this object to be
        garbage-collected.
        """
        self._sources = None
        
    def getCompileStatus(self):
        """
        Indicates whether the shader elements managed by this object were
        compiled successfully.
        
        @rtype: bool
        @return: True if compilation succeeded.
        
        @raise ValueError: It was impossible to determine the compilation state.
        """
        return bool(self._get(GL_COMPILE_STATUS))
        
    def getID(self):
        """
        Provides the GLSL ID of the compiled shader managed by this object.
        
        @rtype: GLuint|None
        @return: The compiled shader ID or None if not yet compiled.
        """
        return self._id
        
    def getInfoLog(self):
        """
        Provides the GLSL compilation log.
        
        @rtype: str
        @return: The GLSL compilation log.
        
        @raise ValueError: It was impossible to access the compilation log.
        """
        length = self._getInfoLogLength()
        if length == 0:
            return ''
        buffer = create_string_buffer(length)
        glGetShaderInfoLog(self._id, length, None, buffer)
        return buffer.value
        
class FragmentShader(_Shader):
    """
    A stub class used to manage GLSL fragment shader elements.
    """
    _shader_type = GL_FRAGMENT_SHADER
    
class VertexShader(_Shader):
    """
    A stub class used to manage GLSL vertex shader elements.
    """
    _shader_type = GL_VERTEX_SHADER
    
    
class ShaderProgram(object):
    """
    A wrapper for a GLSL program, which is comprised of at least one GLSL
    shader.
    """
    _active = False #: True while this GLSL program is in use; used to prevent accidental deactivation of other programs.
    _id = None #: The ID of the compiled GLSL program managed by this object.
    _shaders = None #: A collection of all GLSL shaders that comprise this GLSL program.
    
    def __init__(self, *shaders):
        """
        Accepts GLSL shaders.
        
        @type *shaders: tuple
        @param *shaders: All GLSL shaders to be linked.
        """
        assert (
         len(shaders) > 0 and
         not [None for shader in shaders if not isinstance(shader, _Shader)]
        )
        
        self._shaders = shaders
        self._id = None
        
    def _get(self, param_id):
        """
        Requests a specific detail about the shader program managed by this
        object.
        
        @type param_id: GLenum
        @param param_id: The type of parameter being looked up; allowed values:
            C{GL_DELETE_STATUS}, C{GL_LINK_STATUS}, C{GL_VALIDATE_STATUS},
            C{GL_INFO_LOG_LENGTH}, C{GL_ATTACHED_SHADERS},
            C{GL_ACTIVE_ATTRIBUTES}, C{GL_ACTIVE_ATTRIBUTE_MAX_LENGTH},
            C{GL_ACTIVE_UNIFORMS}, C{GL_ACTIVE_UNIFORM_MAX_LENGTH}
        
        @rtype: GLint
        @return: A pointer to the requested information
        
        @raise ValueError: It was impossible to look up the requested parameter.
        """
        outvalue = c_int(0)
        glGetProgramiv(self._id, param_id, byref(outvalue))
        value = outvalue.value
        if value in _SHADER_ERRORS:
            raise ValueError('%(message)s from glGetProgram(%(id)s, %(param_id)s, &value)' % {
             'message': _SHADER_ERRORS[value],
             'id': self._id,
             'param_id': param_id,
            })
        return value
        
    def _getInfoLogLength(self):
        """
        Provides the length of the GLSL linking log.
        
        @rtype: GLint
        @return: The length of the log.
        
        @raise ValueError: It was impossible to resolve the log length.
        """
        return self._get(GL_INFO_LOG_LENGTH)
        
    def _getMessage(self):
        """
        Assembles all compilation logs from all GLSL shaders that make up the
        GLSL program managed by this object, and caps the list with the link
        log; the result is returned, separated by linebreaks.
        
        @rtype: str|None
        @return: A summary of all events that occurred during compilation or
            None if nothing noteworthy occurred.
        
        @raise ValueError: It was impossible to access a log.
        """
        messages = []
        for shader in self._shaders:
            log = shader.getInfoLog()
            if log:
                messages.append(log)
        log = self.getInfoLog()
        if log:
            messages.append(log)
            
        if messages:
            return '\n\n'.join(messages)
        else:
            return None
            
    def destroy(self):
        """
        Releases this GLSL program from OpenGL's memory.
        
        Note that while all shaders will be detached, none will be deleted until
        individually destroyed; call L{getShaders}() to handle this process
        manually.
        """
        glDeleteProgram(self._id)
        
    def disable(self):
        """
        Disables the active GLSL program, but only if this program was
        previously activated.
        
        Caution: It is the developer's responsibility to keep track of which
        program is currently active.
        """
        if self._active:
            glUseProgram(0)
            self._active = False
            
    def enable(self):
        """
        Sets this program as the active GLSL program and enables its
        L{disable}() method.
        """
        glUseProgram(self._id)
        self._active = True
        
    def getID(self):
        """
        Provides the GLSL ID of the compiled program managed by this object.
        
        @rtype: GLuint|None
        @return: The compiled program ID or None if not yet compiled.
        """
        return self._id
        
    def getInfoLog(self):
        """
        Provides the GLSL linking log.
        
        @rtype: str
        @return: The GLSL linking log.
        
        @raise ValueError: It was impossible to access the linking log.
        """
        length = self._getInfoLogLength()
        if length == 0:
            return ''
        buffer = create_string_buffer(length)
        glGetProgramInfoLog(self._id, length, None, buffer)
        return buffer.value
        
    def getLinkStatus(self):
        """
        Indicates whether the shader program managed by this object was linked
        successfully.
        
        @rtype: bool
        @return: True if linking succeeded.
        
        @raise ValueError: It was impossible to determine the link state.
        """
        return bool(self._get(GL_LINK_STATUS))
        
    def getShaders(self):
        """
        Returns all shaders attached to the GLSL program this object manages.
        
        @rtype: tuple
        @return: A collection of L{_Shader} objects.
        """
        return self._shaders
        
    def link(self, flush_source=True):
        """
        Links all GLSL shader elements managed by this object into a single GLSL
        shader program.
        
        @type flush_source: bool
        @param flush_source: If True, post-compilation, all source code
            associated with the shaders that make up this program will be
            dereferenced.
        
        @rtype: str|None
        @return: A summary of all events that occurred during compilation or
            None if nothing noteworthy occurred.
        
        @raise CompileError: Something went wrong during compilation.
        @raise LinkError: Something went wrong during linking.
        @raise ValueError: It was impossible to determine the compilation state,
            the link state, or to access a log.
        """
        self._id = glCreateProgram()
        for shader in self._shaders:
            shader.compile()
            glAttachShader(self._id, shader.getID())
            if flush_source:
                shader.flushSource()
        glLinkProgram(self._id)
        
        message = self._getMessage()
        if not self.getLinkStatus():
            raise LinkError(message)
        return message
        
    def setUniform_float(self, name, value):
        """
        Sets the value of a uniform float in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value: float
        @param value: The value to set.
        """
        glUniform1f(
         glGetUniformLocation(self._id, name),
         c_float(value)
        )
        
    def setUniform_vec2(self, name, value_1, value_2):
        """
        Sets the value of a uniform vec2 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: float
        @param value_1: The value to set in element 0.
        @type value_2: float
        @param value_2: The value to set in element 1.
        """
        glUniform2f(
         glGetUniformLocation(self._id, name),
         c_float(value_1), c_float(value_2)
        )
        
    def setUniform_vec3(self, name, value_1, value_2, value_3):
        """
        Sets the value of a uniform vec3 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: float
        @param value_1: The value to set in element 0.
        @type value_2: float
        @param value_2: The value to set in element 1.
        @type value_3: float
        @param value_3: The value to set in element 2.
        """
        glUniform3f(
         glGetUniformLocation(self._id, name),
         c_float(value_1), c_float(value_2), c_float(value_3)
        )
        
    def setUniform_vec4(self, name, value_1, value_2, value_3, value_4):
        """
        Sets the value of a uniform vec4 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: float
        @param value_1: The value to set in element 0.
        @type value_2: float
        @param value_2: The value to set in element 1.
        @type value_3: float
        @param value_3: The value to set in element 2.
        @type value_4: float
        @param value_4: The value to set in element 3.
        """
        glUniform4f(
         glGetUniformLocation(self._id, name),
         c_float(value_1), c_float(value_2), c_float(value_3), c_float(value_4)
        )
        
    def setUniform_int(self, name, value):
        """
        Sets the value of a uniform int in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value: int
        @param value: The value to set.
        """
        glUniform1i(
         glGetUniformLocation(self._id, name),
         c_int(value)
        )
        
    def setUniform_ivec2(self, name, value_1, value_2):
        """
        Sets the value of a uniform ivec2 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: int
        @param value_1: The value to set in element 0.
        @type value_2: int
        @param value_2: The value to set in element 1.
        """
        glUniform2i(
         glGetUniformLocation(self._id, name),
         c_int(value_1), c_int(value_2)
        )
        
    def setUniform_ivec3(self, name, value_1, value_2, value_3):
        """
        Sets the value of a uniform ivec3 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: int
        @param value_1: The value to set in element 0.
        @type value_2: int
        @param value_2: The value to set in element 1.
        @type value_3: int
        @param value_3: The value to set in element 2.
        """
        glUniform3i(
         glGetUniformLocation(self._id, name),
         c_int(value_1), c_int(value_2), c_int(value_3)
        )
        
    def setUniform_ivec4(self, name, value_1, value_2, value_3, value_4):
        """
        Sets the value of a uniform ivec4 in the GLSL shader program managed
        by this object.
        
        @type name: basestring
        @param name: The name of the variable to be set.
        @type value_1: int
        @param value_1: The value to set in element 0.
        @type value_2: int
        @param value_2: The value to set in element 1.
        @type value_3: int
        @param value_3: The value to set in element 2.
        @type value_4: int
        @param value_4: The value to set in element 3.
        """
        glUniform4i(
         glGetUniformLocation(self._id, name),
         c_int(value_1), c_int(value_2), c_int(value_3), c_int(value_4)
        )
        
        
class ShaderError(Exception):
    """
    A stub class used to identify errors originating from this module.
    """
    pass
    
class CompileError(ShaderError):
    """
    A stub class used to identify errors originating during compilation.
    """
    pass
    
class LinkError(ShaderError):
    """
    A stub class used to identify errors originating during linking.
    """
    pass
    
