# Copyright 2020 Arista Networks.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from __future__ import absolute_import, division, print_function
from contextlib import contextmanager
import ctypes
import ctypes.util
import CMock

class CountedFunc( object ):
   ''' Simple functor that counts number of times its invoked. This can be used
   woth PRE mocks to count the number of times a function is called.'''
   def __init__( self ):
      self.calls = 0

   def __call__( self, *args ):
      self.calls += 1

@contextmanager
def verifyCalls( realfunc, expectedCalls ):
   ''' context manager that uses CountedFunc and PRE mock to verify that a
   function is called exactly "expectedCalls" times. '''
   mockfunc = CountedFunc()
   with CMock.mocked( realfunc, mockfunc, method=CMock.PRE ):
      yield
   assert mockfunc.calls == expectedCalls

class FakeSyscall( CMock.mocked ):
   ''' Allows calling a "fake" system call. The first "start" invocations will
   be executed normally, the next count-start invocations will set errno to the
   configured value, and return the returncode with errno set as requested. '''

   def __init__( self, func, rv, errno, start=0, count=10000 ):
      super( FakeSyscall, self ).__init__( func, self )
      self.rv = rv
      self.errno = errno
      self.calls = 0
      self.start = start
      self.count = count

   def __call__( self, *args ):
      if self.calls < self.start or self.calls >= self.start + self.count:
         rv = self.realfunc( *args )
      else:
         ctypes.set_errno( self.errno )
         rv = self.rv
      self.calls += 1
      return rv

def _decorateSyscalls( libc ):
   ''' Decorate libc system calls with type information.  We do this manually,
   as there's no debug information for most syscalls (they are often just
   generated from assembler) '''

   def proto( res, field, args ):
      ''' simple function to reduce stutter below '''
      field.restype = res
      field.argtypes = args

   from ctypes import c_int, c_void_p, POINTER, c_uint, c_long
   proto( c_int, libc.getsockopt,
          [ c_int, c_int, c_int, c_void_p, POINTER( c_uint ) ] )
   proto( c_int, libc.connect, [ c_int, c_void_p, c_uint ] )
   proto( c_int, libc.socket, [ c_int, c_int, c_int ] )
   proto( c_int, libc.getsockname, [ c_int, c_void_p, POINTER( c_uint ) ] )
   proto( c_int, libc.bind, [ c_int, c_void_p, c_uint ] )
   proto( c_int, libc.setsockopt, [ c_int, c_int, c_int, c_void_p, c_uint ] )
   proto( c_long, libc.recv, [ c_int, c_void_p, c_int, c_int ] )
   proto( c_int, libc.sendmsg, [ c_int, c_void_p, c_int ] )
   proto( c_int, libc.accept, [ c_int, c_void_p, POINTER( c_uint ) ] )

def getLibc():
   ''' load and decorate libc functions. Returns reference to libc, and the
   generated ctypes module

   Because syscalls are often not actually written in C, a lot of the
   prototypes for syscalls are unavailable in the debug info, so we augment the
   auto-generated code with the types for common syscalls.
   '''
   # We can't see CMock.libc when we're pylinting, because it's generated.
   # pylint: disable=no-name-in-module
   # pylint: disable=import-error
   # pylint: disable=no-member
   # pylint: disable=redefined-outer-name
   import CMock.libc
   dll = ctypes.CDLL( ctypes.util.find_library( "c" ) )
   CMock.libc.decorateFunctions( dll )
   _decorateSyscalls( dll )
   return dll, CMock.libc
