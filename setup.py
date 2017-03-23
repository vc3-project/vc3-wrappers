#!/usr/bin/env python
#
# Setup prog for vc3-wrappers
#

import commands
import os
import re
import sys

release_version='0.0.1'

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

systemd_files   = [ ]
etc_files       = [ ]
logrotate_files = [ ]
initd_files     = [ ]
rpm_data_files  = [ ]
home_data_files = [ ]

def choose_data_files():
    rpminstall = True
    userinstall = False
     
    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True
                
    if rpminstall:
        return rpm_data_files
    elif userinstall:
        return home_data_files
    else:
        # Something probably went wrong, so punt
        return rpm_data_files
       
# ===========================================================

# setup for distutils
setup(
    name="vc3-wrappers",
    version=release_version,
    description='vc3-wrappers package',
    long_description='''This package contains the VC3 wrappers''',
    license='GPL',
    author='Ben Tovar',
    author_email='btovar@nd.edu',
    maintainer='Ben Tovar',
    maintainer_email='btovar@nd.edu',
    url='https://github.com/vc3-project',
    packages=['vc3'
              ],
    scripts = [ # Utilities and main script
               'scripts/vc3-cctools-catalog-server',
               'scripts/vc3-makeflow',
              ],
    
    data_files = choose_data_files()
)
