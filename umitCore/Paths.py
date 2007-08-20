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

from os import R_OK, W_OK, access, mkdir, getcwd
from os.path import exists, join, split, abspath
import sys

from umitCore.UmitLogging import log
from umitCore.UmitConfigParser import UmitConfigParser
from umitCore.BasePaths import base_paths, HOME
from umitCore.I18N import _

VERSION = "0.9.4"
REVISION = "1453"

CONFIG_DIR = join("share", "umit", "config")
UMIT_ICON = join("share", "icons", "umit_48.ico")
LOCALE_DIR = join("share", "umit", "locale")
MISC_DIR = join("share", "umit", "misc")
ICONS_DIR = join("share", "icons")
PIXMAPS_DIR = join("share", "pixmaps")
DOCS_DIR = join("share", "umit", "docs")


#######
# Paths
class Paths(object):
    """Paths
    """
    config_parser = UmitConfigParser()
    paths_section = "paths"

    hardcoded = ["locale_dir",
                 "pixmaps_dir",
                 "icons_dir",
                 "misc_dir",
                 "docs_dir",
                 "umit_icon"]

    config_files_list = ["config_file",
                         "target_list",
                         "profile_editor",
                         "wizard",
                         "scan_profile",
                         "recent_scans",
                         "options",
                         "umitdb",
                         "umit_version",
                         "webconfig_file",
                         "security_file",
                         "umitdb_web"]
    
    share_files_list = ["umit_op",
                        "umit_opi",
                        "umit_opt",
                        "umit_opf"]

    misc_files_list = ["services_dump",
                       "os_dump",
                       "os_classification"]

    other_settings = ["nmap_command_path"]

    config_file_set = False
    
    def set_umit_conf(self, base_dir):
        main_config_dir = ""
        main_config_file = ""
        if exists(CONFIG_DIR) and \
            exists(join(CONFIG_DIR, base_paths['config_file'])):
            main_config_dir = CONFIG_DIR

        elif exists(join(base_dir, CONFIG_DIR)) and\
            exists(join(base_dir,
                                        CONFIG_DIR,
                                        base_paths['config_file'])):
            main_config_dir = join(base_dir, CONFIG_DIR)

        elif exists(join(split(base_dir)[0], CONFIG_DIR)) and \
            exists(join(split(base_dir)[0],
                                        CONFIG_DIR,
                                        base_paths['config_file'])):
            main_config_dir = join(split(base_dir)[0], CONFIG_DIR)

        else:
            raise Exception("Couldn't find the Umit's Config Directory! \
Aborting...")

        # Main config file, based on the main_config_dir got above
        main_config_file = join(main_config_dir, base_paths['config_file'])

        # This is the expected place in which umit.conf should be placed
        supposed_file = join(base_paths['user_dir'], base_paths['config_file'])
        config_dir = ""
        config_file = ""

        if exists(supposed_file)\
               and check_access(supposed_file, R_OK and W_OK):
            config_dir = base_paths['user_dir']
            config_file = supposed_file
            log.debug(">>> Using config files in user home \
directory: %s" % config_file)

        elif not exists(supposed_file)\
             and not check_access(base_paths['user_dir'],
                                  R_OK and W_OK):
            try:
                result = create_user_dir(join(main_config_dir,
                                              base_paths['config_file']),
                                         HOME)
                if type(result) == type({}):
                    config_dir = result['config_dir']
                    config_file = result['config_file']
                    log.debug(">>> Using recently created config files in \
user home: %s" % config_file)
                else:
                    raise Exception()
            except:
                log.debug(">>> Failed to create user home")

        if config_dir and config_file:
            # Checking if the version of the configuration files are the same
            # as this Umit's version
            if not self.check_version(config_dir):
                log.debug(">>> The config files versions are different!")
                log.debug(">>> Running update scripts...")
                self.update_config_dir(config_dir)

        else:
            log.debug(">>> There is no way to create nor use home connfigs.")
            log.debug(">>> Trying to use main configuration files...")

            config_dir = main_config_dir
            config_file = main_config_file

        # Parsing the umit main config file
        self.config_parser.read(config_file)

        # Should make the following only after reading the umit.conf file
        self.config_dir = config_dir
        self.config_file = config_file
        self.config_file_set = True
        self.locale_dir = LOCALE_DIR
        self.pixmaps_dir = PIXMAPS_DIR
        self.icons_dir = ICONS_DIR
        self.misc_dir = MISC_DIR
        self.docs_dir = DOCS_DIR
        self.umit_icon = UMIT_ICON

        log.debug(">>> Config file: %s" % config_file)

    def update_config_dir(self, config_dir):
        pass

    def check_version(self, config_dir):
        ver = open(join(config_dir,
                        base_paths['umit_version'])).readlines()[0].\
                                                     split("\n")[0].\
                                                     split("\r")[0]

        log.debug(">>> This Umit Version: %s" % VERSION)
        log.debug(">>> Version of the files in %s: %s" % (config_dir, ver))

        if VERSION == ver:
            return True
        return False

    def root_dir(self):
        """Retrieves root dir on current filesystem"""
        curr_dir = getcwd()
        while True:
            splited = split(curr_dir)[0]
            if curr_dir == splited:
                break
            curr_dir = splited

        log.debug(">>> Root dir: %s" % curr_dir)
        return curr_dir


    def __getattr__(self, name):
        if self.config_file_set:
            if name in self.other_settings:
                return self.config_parser.get(self.paths_section, name)

            elif name in self.hardcoded:
                return self.__dict__[name]

            elif name in self.config_files_list:
                return return_if_exists(join(self.__dict__['config_dir'],
                                             base_paths[name]))

            elif name in self.share_files_list:
                return return_if_exists(join(self.__dict__['pixmaps_dir'],
                                             base_paths[name]))

            elif name in self.misc_files_list:
                return return_if_exists(join(self.__dict__["misc_dir"],
                                                     base_paths[name]))

            try:
                return self.__dict__[name]
            except:
                raise NameError(name)
        else:
            raise Exception("Must set config file location first")

    def __setattr__(self, name, value):
        if name in self.other_settings:
            self.config_parser.set(self.paths_section, name, value)
        else:
            self.__dict__[name] = value
    

####################################
# Functions for directories creation

def create_user_dir(config_file, user_home):
    log.debug(">>> Create user dir at given home: %s" % user_home)
    log.debug(">>> Using %s as source" % config_file)

    main_umit_conf = UmitConfigParser()
    main_umit_conf.read(config_file)
    paths_section = "paths"

    user_dir = join(user_home, base_paths['config_dir'])

    if exists(user_home)\
           and access(user_home, R_OK and W_OK)\
           and not exists(user_dir):
        mkdir(user_dir)
        log.debug(">>> Umit user dir successfully created! %s" % user_dir)
    else:
        log.warning(">>> No permissions to create user dir!")
        return False

    main_dir = split(config_file)[0]
    copy_config_file("options.xml", main_dir, user_dir)
    copy_config_file("profile_editor.xml", main_dir, user_dir)
    copy_config_file("recent_scans.txt", main_dir, user_dir)
    copy_config_file("scan_profile.usp", main_dir, user_dir)
    copy_config_file("target_list.txt", main_dir, user_dir)
    copy_config_file("umit_version", main_dir, user_dir)
    copy_config_file("wizard.xml", main_dir, user_dir)
    copy_config_file("umitweb.conf", main_dir, user_dir)
    copy_config_file("security.xml", main_dir, user_dir)

    return dict(user_dir = user_dir,
                config_dir = user_dir,
                config_file = copy_config_file("umit.conf",
                                               split(config_file)[0],
                                               user_dir))

def copy_config_file(filename, dir_origin, dir_destiny):
    log.debug(">>> copy_config_file %s to %s" % (filename, dir_destiny))

    origin = join(dir_origin, filename)
    destiny = join(dir_destiny, filename)

    if not exists(destiny):
        # Quick copy
        open(destiny, 'w').write(open(origin).read())
    return destiny

def check_access(path, permission):
    return exists(path) and access(path, permission)

def return_if_exists(path):
    if exists(path):
        return abspath(path)
    raise Exception("File '%s' does not exist or could not be found!" % path)

############
# Singleton!
Path = Paths()

if __name__ == '__main__':
    Path.set_umit_conf(split(sys.argv[0])[0])

    print ">>> SAVED DIRECTORIES:"
    print ">>> LOCALE DIR:", Path.locale_dir
    print ">>> PIXMAPS DIR:", Path.pixmaps_dir
    print ">>> CONFIG DIR:", Path.config_dir
    print
    print ">>> FILES:"
    print ">>> CONFIG FILE:", Path.config_file
    print ">>> TARGET_LIST:", Path.target_list
    print ">>> PROFILE_EDITOR:", Path.profile_editor
    print ">>> WIZARD:", Path.wizard
    print ">>> SCAN_PROFILE:", Path.scan_profile
    print ">>> RECENT_SCANS:", Path.recent_scans
    print ">>> OPTIONS:", Path.options
    print
    print ">>> UMIT_OP:", Path.umit_op
    print ">>> UMIT_OPI:", Path.umit_opi
    print ">>> UMIT_OPT:", Path.umit_opt
    print ">>> UMIT_OPF:", Path.umit_opf
    print ">>> UMITDB:", Path.umitdb
    print ">>> SERVICES DUMP:", Path.services_dump
    print ">>> OS DB DUMP:", Path.os_dump
    print ">>> UMIT VERSION:", Path.umit_version
    print ">>> OS CLASSIFICATION DUMP:", Path.os_classification
    print ">>> NMAP COMMAND PATH:", Path.nmap_command_path
