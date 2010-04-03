#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: run_game_debug.py 218 2009-07-18 20:44:59Z dr0iddr0id $'

import sys
import os
import subprocess

try:
    import psyco
    psyco.profile()
except:
    if __debug__:
        print "psyco not found"

# Set Pyglet options now, before anything else can import a sub-module.
import pyglet
pyglet.options['debug'] = True
pyglet.options['audio'] = ('silent',)

# run in right directory
if not sys.argv[0]:
    appdir = os.path.abspath(os.path.dirname(__file__))
else:
    appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(appdir)
if not appdir in sys.path:
    sys.path.insert(0,appdir)

from src.main import run

def run_debug():
    # running in debug mode
    if u"-profile" in sys.argv:
        import cProfile
        import tempfile
        import os
 
        try:
            cProfile.run('run()', 'profile.txt')
        finally:
            pass
    else:
        run()


if __name__ == '__main__':
    run_debug()
