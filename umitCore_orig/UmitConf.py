##
## UmitConf.py
## Login : <adriano@localhost.localdomain>
## Started on  Sun Apr  9 17:01:43 2006 Adriano Monteiro Marques
## $Id$
## 
## Copyright (C) 2006 Adriano Monteiro Marques
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

import re

from types import StringTypes
from ConfigParser import NoSectionError

from umitCore.Paths import Path
from umitCore.UmitConfigParser import UmitConfigParser
from umitCore.Logging import log
from umitCore.I18N import _

config_file = Path.config_file
scan_profile = Path.scan_profile

def umit_version():
    return open(Path.umit_version).read()

class UmitConf(UmitConfigParser, object):
    def __init__(self, *args):
        UmitConfigParser.__init__(self, *args)
        self.read(config_file)
        
    def get_colored_diff(self):
        try:
            cd = self.get('diff', 'colored_diff')
            if cd == "False" or cd == "false" or cd == "0" or cd == "" or cd == False:
                return False
            return True
        except:return True

    def set_colored_diff(self, enable):
        if not self.has_section('diff'):
            self.add_section('diff')
        
        self.set('diff', 'colored_diff', enable)

    def get_diff_mode(self):
        try: return self.get('diff', 'diff_mode')
        except: return "compare"

    def set_diff_mode(self, diff_mode):
        if not self.has_section('diff'):
            self.add_section('diff')
        
        self.set('diff', 'diff_mode', diff_mode)

    colored_diff = property(get_colored_diff, set_colored_diff)
    diff_mode = property(get_diff_mode, set_diff_mode)


class SearchConfig(UmitConfigParser, object):
    def __init__(self, *args):
        UmitConfigParser.__init__(self, *args)
        self.read(config_file)

        self.section_name = "search"
        if not self.has_section(self.section_name):
            self.create_section()

    def create_section(self):
        self.add_section(self.section_name)
        self.directory = ""
        self.file_extension = "usr"
        self.save_time = "60;days"
        self.store_results = True
        self.search_db = True

    def _get_it(self, p_name, default):
        return self.get(self.section_name, p_name, default)

    def _set_it(self, p_name, value):
        self.set(self.section_name, p_name, value)
        
    def boolean_sanity(self, attr):
        if attr == True or \
           attr == "True" or \
           attr == "true" or \
           attr == "1":
            
            return 1
        
        return 0

    def get_directory(self):
        return self._get_it("directory", "")

    def set_directory(self, directory):
        self._set_it("directory", directory)

    def get_file_extension(self):
        return self._get_it("file_extension", "usr").split(";")

    def set_file_extension(self, file_extension):
        if type(file_extension) == type([]):
            self._set_it("file_extension", ";".join(file_extension))
        elif type(file_extension) in StringTypes:
            self._set_it("file_extension", file_extension)

    def get_save_time(self):
        return self._get_it("save_time", "60;days").split(";")

    def set_save_time(self, save_time):
        if type(save_time) == type([]):
            self._set_it("save_time", ";".join(save_time))
        elif type(save_time) in StringTypes:
            self._set_it("save_time", save_time)

    def get_store_results(self):
        return self.boolean_sanity(self._get_it("store_results", True))

    def set_store_results(self, store_results):
        self._set_it("store_results", self.boolean_sanity(store_results))

    def get_search_db(self):
        return self.boolean_sanity(self._get_it("search_db", True))

    def set_search_db(self, search_db):
        self._set_it("search_db", self.boolean_sanity(search_db))

    def get_converted_save_time(self):
        try:
            return int(self.save_time[0]) * self.time_list[self.save_time[1]]
        except:
            # If something goes wrong, return a save time of 60 days
            return 60 * 60 * 24 * 60

    def get_time_list(self):
        # Time as key, seconds a value
        return {_("Hours"): 60 * 60,
                _("Days"): 60 * 60 * 24,
                _("Weeks"): 60 * 60 * 24 * 7,
                _("Months"): 60 * 60 * 24 * 7 * 30,
                _("Years"): 60 * 60 * 24 * 7 * 30 * 12,
                _("Minutes"): 60,
                _("Seconds"): 1}
    
    directory = property(get_directory, set_directory)
    file_extension = property(get_file_extension, set_file_extension)
    save_time = property(get_save_time, set_save_time)
    store_results = property(get_store_results, set_store_results)
    search_db = property(get_search_db, set_search_db)
    converted_save_time = property(get_converted_save_time)
    time_list = property(get_time_list)


class Profile(UmitConfigParser, object):
    def __init__(self, user_profile=None, *args):
        UmitConfigParser.__init__(self, *args)
        
        if not user_profile:
            user_profile = scan_profile

        fconf = open(user_profile, 'r')
        self.readfp(fconf, user_profile)
        
        fconf.close()
        del(fconf)
        
        self.attributes = {}

    def _get_it(self, profile, attribute):
        if profile:
            self.__verify_profile(profile)
            return self.get(profile, attribute)
        return ""

    def _set_it(self, profile, attribute, value=''):
        if profile:
            self.__verify_profile(profile)
            return self.set(profile, attribute, value)

    def add_profile(self, profile_name, **attributes):
        try: self.add_section(profile_name)
        except: return None
        
        [self._set_it(profile_name, attr, attributes[attr]) for attr in attributes]
        self.save_changes()

    def remove_profile(self, profile_name):
        try: self.remove_section(profile_name)
        except: pass
        self.save_changes()

    def __verify_profile(self, profile_name):
        if profile_name not in self.sections():
            raise ProfileNotFound(profile_name)

class CommandProfile (Profile, object):
    def __init__(self, user_profile=''):
        if not user_profile:
            user_profile = scan_profile
        
        Profile.__init__(self, user_profile)
        
    def get_command(self, profile):
        return self._get_it(profile, 'command')

    def get_hint(self, profile):
        return self._get_it(profile, 'hint')

    def get_description(self, profile):
        return self._get_it(profile, 'description')
    
    def get_annotation(self, profile):
        return self._get_it(profile, 'annotation')

    def get_options(self, profile):
        return self._get_it(profile, 'options').split(',')


    def set_command(self, profile, command=''):
        self._set_it(profile, 'command', command)

    def set_hint(self, profile, hint=''):
        self._set_it(profile, 'hint', hint)
    
    def set_description(self, profile, description=''):
        self._set_it(profile, 'description', description)
    
    def set_annotation (self, profile, annotation=''):
        self._set_it(profile, 'annotation', annotation)
    
    def set_options(self, profile, options=''):
        self._set_it(profile, 'options', options)

    def get_profile(self, profile_name):
        return {'profile':profile_name, \
                'command':self.get_command(profile_name), \
                'hint':self.get_hint(profile_name), \
                'description':self.get_description(profile_name), \
                'annotation':self.get_annotation(profile_name),\
                'options':self.get_options(profile_name)}


class NmapOutputHighlight(UmitConfigParser, object):
    setts = ["bold", "italic", "underline", "text", "highlight", "regex"]
    
    def __init__(self, *args):
        UmitConfigParser.__init__(self, *args)
        self.read(Path.config_file)

    def __get_it(self, p_name):
        property_name = "%s_highlight" % p_name

        try:
            return self.sanity_settings([self.get(property_name, prop, True) \
                                         for prop in self.setts])
        except:
            settings = []
            prop_settings = self.default_highlights[p_name]
            settings.append(prop_settings["bold"])
            settings.append(prop_settings["italic"])
            settings.append(prop_settings["underline"])
            settings.append(prop_settings["text"])
            settings.append(prop_settings["highlight"])
            settings.append(prop_settings["regex"])

            self.__set_it(p_name, settings)

            return settings

    def __set_it(self, property_name, settings):
        property_name = "%s_highlight" % property_name
        settings = self.sanity_settings(settings)

        [self.set(property_name, self.setts[pos], settings[pos]) \
         for pos in xrange(len(settings))]

    def sanity_settings(self, settings):
        """This method tries to convert insane settings to sanity ones ;-)
        If user send a True, "True" or "true" value, for example, it tries to
        convert then to the integer 1.
        Same to False, "False", etc.

        Sequence: [bold, italic, underline, text, highlight, regex]
        """
        log.debug(">>> Sanitize %s" % str(settings))
        
        settings[0] = self.boolean_sanity(settings[0])
        settings[1] = self.boolean_sanity(settings[1])
        settings[2] = self.boolean_sanity(settings[2])

        tuple_regex = "[\(\[]\s?(\d+)\s?,\s?(\d+)\s?,\s?(\d+)\s?[\)\]]"
        if type(settings[3]) == type(""):
            settings[3] = [int(t) for t in re.findall(tuple_regex, settings[3])[0]]

        if type(settings[4]) == type(""):
            settings[4]= [int(h) for h in re.findall(tuple_regex, settings[4])[0]]

        return settings

    def boolean_sanity(self, attr):
        if attr == True or attr == "True" or attr == "true" or attr == "1":
            return 1
        return 0

    def get_date(self):
        return self.__get_it("date")

    def set_date(self, settings):
        self.__set_it("date", settings)

    def get_hostname(self):
        return self.__get_it("hostname")

    def set_hostname(self, settings):
        self.__set_it("hostname", settings)

    def get_ip(self):
        return self.__get_it("ip")

    def set_ip(self, settings):
        self.__set_it("ip", settings)

    def get_port_list(self):
        return self.__get_it("port_list")

    def set_port_list(self, settings):
        self.__set_it("port_list", settings)

    def get_open_port(self):
        return self.__get_it("open_port")

    def set_open_port(self, settings):
        self.__set_it("open_port", settings)

    def get_closed_port(self):
        return self.__get_it("closed_port")

    def set_closed_port(self, settings):
        self.__set_it("closed_port", settings)

    def get_filtered_port(self):
        return self.__get_it("filtered_port")

    def set_filtered_port(self, settings):
        self.__set_it("filtered_port", settings)

    def get_details(self):
        return self.__get_it("details")

    def set_details(self, settings):
        self.__set_it("details", settings)

    def get_enable(self):
        enable = True
        try:
            enable = self.get("output_highlight", "enable_highlight")
        except NoSectionError:
            self.set("output_highlight", "enable_highlight", str(True))
        
        if enable == "False" or enable == "0" or enable == "":
            return False
        return True

    def set_enable(self, enable):
        if enable == False or enable == "0" or enable == None or enable == "":
            self.set("output_highlight", "enable_highlight", str(False))
        else:
            self.set("output_highlight", "enable_highlight", str(True))

    date = property(get_date, set_date)
    hostname = property(get_hostname, set_hostname)
    ip = property(get_ip, set_ip)
    port_list = property(get_port_list, set_port_list)
    open_port = property(get_open_port, set_open_port)
    closed_port = property(get_closed_port, set_closed_port)
    filtered_port = property(get_filtered_port, set_filtered_port)
    details = property(get_details, set_details)
    enable = property(get_enable, set_enable)

    # These settings are made when there is nothing set yet. They set the "factory" \
    # default to highlight colors
    default_highlights = {"date":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s.{1,4}"},
                          "hostname":{"bold":str(True),
                            "italic":str(True),
                            "underline":str(True),
                            "text":[0, 111, 65535],
                            "highlight":[65535, 65535, 65535],
                            "regex":"(\w{2,}://)*\w{2,}\.\w{2,}(\.\w{2,})*(/[\w{2,}]*)*"},
                          "ip":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"},
                          "port_list":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 1272, 28362],
                            "highlight":[65535, 65535, 65535],
                            "regex":"PORT\s+STATE\s+SERVICE(\s+VERSION)?\s.*"},
                          "open_port":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 41036, 2396],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\s+open\s+.*"},
                          "closed_port":{"bold":str(False),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[65535, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\s+closed\s+.*"},
                          "filtered_port":{"bold":str(False),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[38502, 39119, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\s+filtered\s+.*"},
                          "details":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(True),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"^(\w{2,}[\s]{,3}){,4}:"}}

class DiffColors(UmitConfigParser, object):
    def __init__(self, *args):
        UmitConfigParser.__init__(self, *args)
        self.read(Path.config_file)
        self.section_name = "diff_colors"

    def __get_it(self, p_name):
        return self.sanity_settings(self.get(self.section_name, p_name))

    def __set_it(self, property_name, settings):
        settings = self.sanity_settings(settings)
        self.set(self.section_name, property_name, settings)

    def sanity_settings(self, settings):
        log.debug(">>> Sanitize %s" % str(settings))
        
        tuple_regex = "[\(\[]\s?(\d+)\s?,\s?(\d+)\s?,\s?(\d+)\s?[\)\]]"
        if type(settings) == type(""):
            settings = [int(t) for t in re.findall(tuple_regex, settings)[0]]

        return settings

    def get_unchanged(self):
        return self.__get_it("unchanged")

    def set_unchanged(self, settings):
        self.__set_it("unchanged", settings)

    def get_added(self):
        return self.__get_it("added")

    def set_added(self, settings):
        self.__set_it("added", settings)

    def get_modified(self):
        return self.__get_it("modified")

    def set_modified(self, settings):
        self.__set_it("modified", settings)

    def get_not_present(self):
        return self.__get_it("not_present")

    def set_not_present(self, settings):
        self.__set_it("not_present", settings)

    unchanged = property(get_unchanged, set_unchanged)
    added = property(get_added, set_added)
    modified = property(get_modified, set_modified)
    not_present = property(get_not_present, set_not_present)

# Exceptions
class ProfileNotFound:
    def __init__ (self, profile):
        self.profile = profile
    def __str__ (self):
        return "No profile named '"+self.profile+"' found!"

class ProfileCouldNotBeSaved:
    def __init__ (self, profile):
        self.profile = profile
    def __str__ (self):
        return "Profile named '"+self.profile+"' could not be saved!"


if __name__ == "__main__":
    d = DiffColors()

    d.unchanged = [0, 0, 0]
    d.added = [0, 0, 0]
    d.modified = [0, 0, 0]
    d.not_present = [0, 0, 0]

    print d.unchanged
    print d.added
    print d.modified
    print d.not_present
    
    '''
    log.critical(scan_profile)
    p = CommandProfile()
    print p.get_profile("Quick Scan")

    s_conf = SearchConfig()
    print dir(s_conf)
    print s_conf.directory
    print s_conf.file_extension
    print s_conf.save_time
    print s_conf.store_results
    print s_conf.search_db
    print s_conf.converted_save_time


    u = NmapOutputHighlight()
    u.date = [1, 0, 0, [0, 0, 0], [65535, 65535, 65535],
              "\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s.{1,4}"]
    u.hostname = [1, 0, 1, [0, 0, 0], [65535, 65535, 65535], "(\w+[\.]?)+"]
    u.ip = [1, 0, 0, [0, 0, 0], [65535, 65535, 65535],
            "[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}"]
    u.port_list = [1, 0, 0, [0, 0, 0], [65535, 65535, 65535],
                   "PORT\s+STATE\s+SERVICE(\s+VERSION)?"]
    u.open_port = [1, 0, 0, [0, 0, 0], [0, 65535, 0], "\d{1,5}/.{1,5}\sopen\s.*"]
    u.closed_port = [1, 0, 0, [0, 0, 0], [65535, 0, 0], "\d{1,5}/.{1,5}\sclosed\s.*"]
    u.filtered_port = [1, 0, 0, [0, 0, 0], [0, 65535, 65535], "\d{1,5}/.{1,5}\sfiltered\s.*"]
    u.details = [1, 0, 0, [0, 0, 0], [65535, 65535, 65535], ".+:.+"]
    u.enable = True

    print "Date", u.date
    print "Hostname", u.hostname
    print "Ip", u.ip
    print "Port list", u.port_list
    print "Open port", u.open_port
    print "Closed port", u.closed_port
    print "Filtered port", u.filtered_port
    print "Details", u.details

    '''
