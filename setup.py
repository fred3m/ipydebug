import os
import sys
import glob
#from pybp import version
from setuptools import setup
from setuptools import find_packages

# Package info
PACKAGE_NAME = "ipydebug"
DESCRIPTION = "Breakpoints and logging class for python debugging"
LONG_DESC = "Function wrappers and breakpoint class to insert breakpoints into a python script"
AUTHOR = "Fred Moolekamp"
AUTHOR_EMAIL = "fred.moolekamp@gmail.com"
LICENSE = "BSD 3-clause"
URL = "http://fred3m.github.io/pybp/"

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.0'

#if 'dev' not in VERSION:
#    VERSION += version.get_git_devstr(False)

scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']

packages = find_packages()

setup(name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=packages,
    scripts=scripts,
    install_requires=[
        'ipython'
    ],
    #provides=[PACKAGE_NAME],
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    long_description=LONG_DESC,
    zip_safe=False,
    use_2to3=True,
    include_package_data=True
)