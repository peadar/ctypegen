#!/usr/bin/env python3
# Copyright 2018 Arista Networks.
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

from setuptools import setup
from setuptools import Extension
from setuptools.command.build_ext import build_ext
import os
import subprocess


class ExtensionBuilder( build_ext ):
    def build_extensions( self ):
        self.compiler.src_extensions.append( ".s" )
        super().build_extensions()


with subprocess.Popen( [ "uname", "-m" ], stdout=subprocess.PIPE ) as pipe:
   ( out, err ) = pipe.communicate()
arch = str( out.decode( "utf-8" ) ).strip()
if arch == "i686":
   arch = "i386"

text = ""

pstack_base = os.getenv( "PSTACK_BASE" )
if pstack_base is None:
   pstack_base = os.getcwd() + "pstack"

pstack_extension_options = {
    'libraries' : [ 'dwelf' ],
    'include_dirs' : [ pstack_base ],
    'library_dirs' : [ pstack_base ],
    'runtime_library_dirs' : [ pstack_base ],
}

setup( name="CTypeGen",
        version="0.9",
        packages=[
           "CMock",
           "CTypeGen",
        ],

        py_modules=[
            "CTypeGenRun",
        ],

        ext_modules=[
            Extension( 'libCTypeGen', [ 'CTypeGen.cpp', ],
                **pstack_extension_options ),
            Extension( 'libCTypeMock', [ 'cmock.cpp', 'thunk-%s.s' % arch ],
                **pstack_extension_options ),
        ],
        scripts=[
            "ctypegen"
        ],
        cmdclass={
            'build_ext': ExtensionBuilder
            }
        )
