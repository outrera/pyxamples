#
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#

from pyglet.gl import *
from ctypes import c_char_p, cast, pointer, POINTER, c_char, c_int, byref, create_string_buffer, c_float

class Shader:
    # vert, frag and geom take arrays of source strings
    # the arrays will be concattenated into one string by OpenGL
    def __init__(self, vert = [], frag = [], geom = []):
        # create the program handle
        self.handle = glCreateProgram()
        # we are not linked yet
        self.linked = False

        # create the vertex shader
        self.createShader(vert, GL_VERTEX_SHADER)
        # create the fragment shader
        self.createShader(frag, GL_FRAGMENT_SHADER)
        # the geometry shader will be the same, once pyglet supports the extension
        # self.createShader(frag, GL_GEOMETRY_SHADER_EXT)

        # attempt to link the program
        self.link()

    def createShader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (c_char_p * count)(*strings)
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        # compile the shader
        glCompileShader(shader)

        temp = c_int(0)
        # retrieve the compile status
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))

        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            print buffer.value
        else:
            # all is well, so attach the shader to the program
            glAttachShader(self.handle, shader);

    def link(self):
        # link the program
        glLinkProgram(self.handle)

        temp = c_int(0)
        # retrieve the link status
        glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))

        # if linking failed, print the log
        if not temp:
            #    retrieve the log length
            glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            print buffer.value
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        # bind the program
        glUseProgram(self.handle)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        glUseProgram(0)

    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1f,
                2 : glUniform2f,
                3 : glUniform3f,
                4 : glUniform4f
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1i,
                2 : glUniform2i,
                3 : glUniform3i,
                4 : glUniform4i
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
        # obtain the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # upload the 4x4 floating point matrix
        glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))

# Notes from source:

# From : https://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/
# 
# Ever wanted to use GLSL with Pyglet, but became lost in the ctypes
# circumlocutions required to compile and link shaders? If so, then here is the
# class for you - a basic, simple GLSL wrapper class, which takes the leg work
# out of using shaders.
# 
# This provides most of what you will need for simple GLSL programs, allowing you
# to compile and link shaders, bind and unbind them, and set uniforms (integer, 
# float and matrix). It doesn't support custom attributes, but that would be a 
# trivial addition.
# 
# Note that there isn't anything restricting this class to use with Pyglet - a 
# simple change to the import statement should allow it to be used with any setup
# based on OpenGL/ctypes. I hope someone finds this useful, and I would love to 
# hear if you use it to make anything cool/interesting.

# Copy of the boost licence below:

# Boost Software License - Version 1.0 - August 17th, 2003
#
# Permission is hereby granted, free of charge, to any person or organization
# obtaining a copy of the software and accompanying documentation covered by
# this license (the "Software") to use, reproduce, display, distribute,
# execute, and transmit the Software, and to prepare derivative works of the
# Software, and to permit third-parties to whom the Software is furnished to
# do so, all subject to the following:
#
# The copyright notices in the Software and this entire statement, including
# the above license grant, this restriction and the following disclaimer,
# must be included in all copies of the Software, in whole or in part, and
# all derivative works of the Software, unless such copies or derivative
# works are solely in the form of machine-executable object code generated by
# a source language processor.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
# SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
# FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.