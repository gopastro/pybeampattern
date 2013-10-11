#from distutils.core import setup
from setuptools import setup, find_packages, Extension
import os, glob

__version__ = '0.1'

setup(
    name = "pybeampattern",
    version = __version__,
    description = "pybeampattern: Package to use GPIB modules to do beam pattern measurements",
    author = "Gopal Narayanan",
    author_email = "gopal@astro.umass.edu",
    packages = find_packages(),
    setup_requires=['nose', 'sphinx'],
    scripts = ['bin/pyrange', 'bin/pyplotrange', 'bin/pyrangephase', 'bin/pyplotrangephase']
    )
