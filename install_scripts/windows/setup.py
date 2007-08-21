#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import py2exe
import os.path

from py2exe.build_exe import py2exe as build_exe
from distutils.core import setup
from glob import glob

################################################################################
# Main Variables

VERSION = "0.9.4"
REVISION = "1470"

# Directories for POSIX operating systems
# These are created after a "install" or "py2exe" command
# These directories are relative to the installation or dist directory
# Ex: python setup.py install --prefix=/tmp/umit
# Will create the directory /tmp/umit with the following directories
pixmaps_dir = os.path.join('share', 'pixmaps')
icons_dir = os.path.join('share', 'icons')
locale_dir = os.path.join('share', 'umit', 'locale')
config_dir = os.path.join('share', 'umit', 'config')
docs_dir = os.path.join('share', 'umit', 'docs')
misc_dir = os.path.join('share', 'umit', 'misc')
templates_dir = os.path.join('umitWeb', 'templates')
media_dir = os.path.join('umitWeb', 'media')

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
data_files = [ (pixmaps_dir, glob(os.path.join(pixmaps_dir, '*.png')) +
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
                (templates_dir, glob(os.path.join(templates_dir, '*.html'))) +
                (media_dir, glob(os.path.join(media_dir, 'images', '*.png')) +
                            glob(os.path.join(media_dir, 'images', '*.jpg')) +
                            glob(os.path.join(media_dir, 'images', '*.gif')) +
                            glob(os.path.join(media_dir, 'js', '*.js')) +
                            glob(os.path.join(media_dir, 'css', '*.css')))]
                
# Add i18n files to data_files list
os.path.walk(locale_dir, mo_find, data_files)



class umit_py2exe(build_exe):
    def run(self):
        build_exe.run(self)
        self.finish_banner()

    def finish_banner(self):
        print 
        print "%s The compiled version of Umit %s-%s is in ./dist %s" % \
              ("#"*10, VERSION, REVISION, "#"*10)
        print


##################### Umit banner ###################################
print
print "%s Umit for Windows %s-%s %s" % ("#"*10, VERSION, REVISION, "#"*10)
print
#####################################################################

setup(name = 'umit',
      license = 'GNU GPL (version 2 or later)',
      url = 'http://umit.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=142490',
      author = 'Adriano Monteiro & Cleber Rodrigues',
      author_email = 'py.adriano@gmail.com, cleber@globalred.com.br',
      maintainer = 'Adriano Monteiro',
      maintainer_email = 'py.adriano@gmail.com',
      description = """UMIT is a nmap frontend, developed in Python and GTK \
and was started with the sponsoring of Google's Summer of Code.""",
      long_description = """The project goal is to develop a nmap frontend \
that is really useful for advanced users and easy to be used by newbies. With \
UMIT, a network admin could create scan profiles for faster and easier network \
scanning or even compare scan results to easily see any changes. A regular \
user will also be able to construct powerful scans with UMIT command creator \
wizards.""",
      version = VERSION,
      scripts = ['umit.pyw', 'umitweb.py'],
      packages = ['', 'umitCore', 'umitGUI', 'umitWeb', 'umitWeb.views',
                  'umitWeb.views.html', 'higwidgets'],
      data_files = data_files,
      cmdclass = {"py2exe":umit_py2exe},
      windows = [{"script" : "umit.pyw",
                  "icon_resources" : [(1, os.path.join("share", "icons", "umit_48.ico"))]},
                 {"script": "umitweb.py"}],
      options = {"py2exe":{"compressed":1,
                           "optimize":2,
                           "packages":"encodings",
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
psyco"}})
