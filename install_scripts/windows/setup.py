#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import sys
import os.path
import os

from py2exe.build_exe import py2exe as build_exe
from distutils.core import setup
from glob import glob

from umitCore.Version import VERSION

################################################################################
# Main Variables

# Directories for POSIX operating systems
# These are created after a "install" or "py2exe" command
# These directories are relative to the installation or dist directory
# Ex: python setup.py install --prefix=/tmp/umit
# Will create the directory /tmp/umit with the following directories
pixmaps_dir = os.path.join('share', 'pixmaps', 'umit')
icons_dir = os.path.join('share', 'icons', 'umit')
locale_dir = os.path.join('share', 'locale')
config_dir = os.path.join('share', 'umit', 'config')
docs_dir = os.path.join('share', 'doc', 'umits')
misc_dir = os.path.join('share', 'umit', 'misc')
templates_dir = os.path.join('share', 'umit', 'templates')
media_dir = os.path.join('share', 'umit', 'umitweb_media')

def mo_find(result, dirname, fnames):
    files = []
    for f in fnames:
        p = os.path.join(dirname, f)
        if os.path.isfile(p) and f.endswith(".mo"):
            files.append(p)
        
    if files:
        result.append((dirname, files))


################################################################################
# Installation variables

# What to copy to the destiny
# Here, we define what should be put inside the directories set in the beginning
# of this file. This list contain tuples where the first element contains
# a path to where the other elements of the tuple should be installed.
# The first element is a path in the INSTALLATION PREFIX, and the other elements
# are the path in the source base.
# Ex: [("share/pixmaps", "/umit/trunk/share/pixmaps/test.png")]
# This will install the test.png file in the installation dir share/pixmaps.
data_files = [ (pixmaps_dir, glob(os.path.join(pixmaps_dir, '*.svg')) +
                             glob(os.path.join(pixmaps_dir, '*.png')) +
                             glob(os.path.join(pixmaps_dir, 'umit.o*'))),

               (config_dir, [os.path.join(config_dir, 'umit.conf')] +
                            [os.path.join(config_dir, 'scan_profile.usp')] +
                            [os.path.join(config_dir, 'umit_version')] +
                            [os.path.join(config_dir, 'umitweb.conf')] +
                            glob(os.path.join(config_dir, '*.xml'))+
                            glob(os.path.join(config_dir, '*.txt'))),

               (misc_dir, glob(os.path.join(misc_dir, '*.dmp'))), 

               (icons_dir, glob(os.path.join('share', 'icons', '*.ico'))+
                           glob(os.path.join('share', 'icons', '*.png'))),

               (docs_dir, glob(os.path.join(docs_dir, '*.html'))+
                          glob(os.path.join(docs_dir,
                                            'comparing_results', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'profile_editor', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'scanning', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'searching', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'wizard', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'screenshots', '*.png'))),
                (os.path.join(media_dir, 'js'),
                          glob(os.path.join(media_dir, 'js', '*.js'))), 
               (os.path.join(media_dir, 'css'),
                          glob(os.path.join(media_dir, 'css', '*.css'))),
               (os.path.join(media_dir, 'images'), 
                          glob(os.path.join(media_dir, 'images', '*.jpg')) +
                          glob(os.path.join(media_dir, 'images', '*.png')) +
                          glob(os.path.join(media_dir, 'images', '*.gif'))),
               (templates_dir, glob(os.path.join(templates_dir, '*.html'))),
               (os.path.join(templates_dir, 'html'),
                          glob(os.path.join(templates_dir, 'html', '*.html')))]
                
# Add i18n files to data_files list
os.path.walk(locale_dir, mo_find, data_files)


class umit_py2exe(build_exe):
    def run(self):
        build_exe.run(self)
        self.finish_banner()

    def finish_banner(self):
        print 
        print "%s The compiled version of Umit %s is in ./dist %s" % \
              ("#"*10, VERSION, "#"*10)
        print


##################### Umit banner ###################################
print
print "%s Umit for Windows %s %s" % ("#"*10, VERSION, "#"*10)
print
#####################################################################

setup(name = 'umit',
      license = 'GNU GPL (version 2 or later)',
      url = 'http://www.umitproject.org',
      download_url = 'http://www.umitproject.org',
      author = 'Adriano Monteiro & Cleber Rodrigues',
      author_email = 'adriano@umitproject.org, cleber@globalred.com.br, rodolfo@umitproject.org',
      maintainer = 'Adriano Monteiro',
      maintainer_email = 'adriano@umitproject.org',
      description = """Umit is a network scanning frontend, developed in \
Python and GTK and was started with the sponsoring of Google's Summer of \
Code.""",
      long_description = """The project goal is to develop a network scanning \
frontend that is really useful for advanced users and easy to be used by \
newbies. With Umit, a network admin could create scan profiles for faster and \
easier network scanning or even compare scan results to easily see any \
changes. A regular user will also be able to construct powerful scans with \
Umit command creator wizards.""",
      version = VERSION,
      scripts = ['umitweb.py'],
      packages = ['', 'umitCore', 'umitWeb', 'umitWeb.views',
                  'umitWeb.views.html', 'higwidgets'],
      data_files = data_files,
      zipfile=None,
      cmdclass = {"py2exe":umit_py2exe},
      windows = [{"script": "management_console.pyw",
                  "icon_resources" : [(1, os.path.join("share", "icons", "umit_48.ico"))]}],
      console = [{"script": "umitweb.py",
                  "icon_resources" : [(1, os.path.join("share", "icons", "umit_48.ico"))]}],
      options = {"py2exe":{"compressed": 1,
                           "optimize": 2,
                           "packages": "encodings",
                           "includes" : "pango,\
atk,\
gobject,\
pickle,\
bz2,\
encodings,\
encodings.*,\
cairo,\
pangocairo,\
atk,\
psyco,\
umitWeb.*,\
umitWeb.views.*,\
umitWeb.views.html.*"}})
