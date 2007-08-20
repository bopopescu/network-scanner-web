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


from difflib import Differ, restore
from umitCore.I18N import _
from NmapParser import HostInfo

class Diff(Differ):
    def __init__(self, result1=[''], result2=[''], junk = "\n"):
        self.result1 = result1
        self.result2 = result2
        self.junk = junk
        
        self.umit_top_banner = ['|'+'-'*70+'|\n',
            '|'+_('UMIT - The nmap frontend').center (70)+'|\n',
            '|'+_('http://umit.sourceforge.net').center(70)+'|\n',
            '|'+' '*70+'|\n',
            '|'+_('This diff was generated by UMIT').center(70)+'|\n',
            '|'+_("(Changes to this file can make UMIT unable to read it.)").center(70)+'|\n',
            '|'+'-'*70+'|\n',
            '\n',
            '-'*10+_(' Start of diff ')+'-'*10+'\n']
        
        self.end_diff = ['\n'+'-'*10+_(' End of diff ')+'-'*10+'\n']
        
        Differ.__init__ (self, self.line_junk)
    
    def generate (self):
        diff_result = []
        for line in self.compare(self.result1, self.result2):
            diff_result.append (line)
        
        return self.umit_top_banner + diff_result + self.end_diff

    def generate_without_banner (self):
        diff_result = []
        for line in self.compare(self.result1, self.result2):
            diff_result.append (line)
        return diff_result
    
    def save (self, file):
        open (file, 'w').writelines (self.generate())
    
    def open (self, file):
        diff_file = open (file).readlines()
        
        return self.restore ('\n'.join(diff_file))
    
    def restore (self, string_to_restore):
        diffie = string_to_restore.split('\n')[len(self.umit_top_banner):-(len\
                                                            (self.end_diff)+1)]

        self.restored1 = []
        for i in restore (diffie, 1):
            self.restored1.append (i+'\n')
        
        self.restored2 = []
        for i in restore (diffie, 2):
            self.restored2.append (i+'\n')
        
        return self.restored1, self.restored2

    def line_junk (self, junk):
        if junk == self.junk:
            return True
        else:
            return False
    
    
class ParserDiff(object):
    """This class generates a tree-based dictionary by taking the differences
    between to parsed scans (instances of NmapParser).
    """
    
    def __init__(self, parsed1, parsed2):
        self.parsed1 = parsed1
        self.parsed2 = parsed2
        self.root_sections = []
    
    def clear_diff_tree(self):
        self.diff_tree = DiffTree(None, "", "")
        
    def append_parent(self, parent, section, state):
        child = DiffTree(parent, state, section, "")
        if parent is not None:
            assert parent.__class__ is DiffTree
            parent.add_child(child)
        return child
        
    def set_parent_status(self, parent, state):
        assert parent.__class__ is DiffTree
        parent.state = state
        return parent
    
    def make_diff(self):
        self.clear_diff_tree()
        self.root_sections = []
        section = _("Umit Info")
        parent = self.append_parent(None, section, "")
        self.root_sections.append(parent)
        self.diff_it(parent, "", _("Profile"), self.parsed1.profile, self.parsed2.profile)
        self.diff_it(parent, "", _("Profile Name"), self.parsed1.profile_name,
                     self.parsed2.profile_name)
        self.diff_it(parent, "", _("Profile Options"), self.parsed1.profile_options,
                     self.parsed2.profile_options)
        self.diff_it(parent, "", _("Target"), self.parsed1.target, self.parsed2.target)

        section = _("Nmap Info")
        parent = self.append_parent(None, section, "")
        self.root_sections.append(parent)
        
        self.diff_it(parent, "", _("Debugging"), self.parsed1.debugging_level,
                     self.parsed2.debugging_level)
        self.diff_it(parent, "", _("Verbosity"), self.parsed1.verbose_level,
                     self.parsed2.verbose_level)
        self.diff_it(parent, "", _("Command"), self.parsed1.nmap_command,
                     self.parsed2.nmap_command)
        self.diff_it(parent, "", _("Scanner version"), self.parsed1.scanner_version,
                     self.parsed2.scanner_version)

        section = _("Scan Info")
        parent = self.append_parent(None, section, "")
        self.root_sections.append(parent)
        
        self.diff_it(parent, "", _("Open Ports"), self.parsed1.open_ports,
                     self.parsed2.open_ports)
        self.diff_it(parent, "", _("Filtered Ports"), self.parsed1.filtered_ports,
                     self.parsed2.filtered_ports)
        self.diff_it(parent, "", _("Closed Ports"), self.parsed1.closed_ports,
                     self.parsed2.closed_ports)
        self.diff_it(parent, "", _("Hosts Up"), self.parsed1.hosts_up,
                     self.parsed2.hosts_up)
        self.diff_it(parent, "", _("Hosts Down"), self.parsed1.hosts_down,
                     self.parsed2.hosts_down)
        self.diff_it(parent, "", _("Hosts Scanned"), self.parsed1.hosts_scanned,
                     self.parsed2.hosts_scanned)
        self.diff_it(parent, "", _("Finish date"), self.parsed1.formated_finish_date,
                     self.parsed2.formated_finish_date)

        hosts1 = self.parsed1.hosts[:]
        hosts2 = self.parsed2.hosts[:]
        while hosts1:
            host = hosts1.pop()
            
            second_host = HostInfo(0)
            host_state = "N"
            for host2 in hosts2:
                if (host.mac and host.mac == host2.mac) or \
                       (host.ip and host.ip == host2.ip) or \
                       (host.ipv6 and host.ipv6 == host2.ipv6):
                    second_host = host2
                    host_state = ""
                    
                    del(hosts2[hosts2.index(host2)]) # Remove it from the hosts2
                    break

            self.add_host_diff(host_state, host, second_host)

        for host in hosts2:
            self.add_host_diff("A", host, host)
            
        return self.root_sections

    def add_host_diff(self, host_state, host, host2=None):
            section = _("Host")
            if host.ip:
                section = _("Host %s") % (host.ip["addr"])
            elif host.ipv6:
                section = _("Host %s") % (host.ipv6["addr"])
            elif host.mac:
                section = _("Host %s") % (host.mac["addr"])

            parent = self.append_parent(None, section, host_state)
            self.root_sections.append(parent)

            self.diff_it(parent, "", _("Comment"), host.comment,
                         host2.comment)
            self.diff_it(parent, "", _("LastBoot"), host.uptime.get("lastboot", ""),
                         host2.uptime.get("lastboot", ""))
            self.diff_it(parent, "", _("OS Match"), host.osmatch.get("name", ""),
                         host2.osmatch.get("name", ""))


            host_ports = host.ports[:]
            host2_ports = host2.ports[:]
            for port in xrange(len(host_ports)):
                # Making sure that extraports1 will get a sanity value to be processed
                try:
                    extraports1 = host_ports[port].get("extraports", [])
                except:
                    extraports1 = {}
                else:
                    if len(extraports1) == 0:
                        extraports1 = {}
                    elif len(extraports1) == 1:
                        extraports1 = extraports1[0]

                # Making sure that extraports2 will get a sanity value to be processed
                try:
                    extraports2 = host2_ports[port].get("extraports", [])
                except:
                    extraports2 = {}
                else:
                    if len(extraports2) == 0:
                        extraports2 = {}
                    elif len(extraports2) == 1:
                        extraports2 = extraports2[0]

                
                if extraports1 and extraports2:
                    self.add_extraports_diff(parent, "", extraports1, extraports2)
                elif extraports1 and not extraports2:
                    self.add_extraports_diff(parent, "N", extraports1, extraports2)
                elif not extraports1 and extraports2:
                    self.add_extraports_diff(parent, "A", extraports1, extraports2)
                

                section =  _("Ports")
                parent = self.append_parent(parent, section, "")


                # Making sure that ports1 will get a sanity value to be processed
                try:
                    ports1 = host_ports[port].get("port", [])
                except:
                    ports1 = {}
                else:
                    if len(ports1) == 0:
                        ports1 = {}
                    elif len(ports1) == 1:
                        ports1 = ports1[0]

                # Making sure that ports2 will get a sanity value to be processed
                try:
                    ports2 = host2_ports[port].get("port", [])
                except:
                    ports2 = {}
                else:
                    if len(ports2) == 0:
                        ports2 = [{}]
                    elif len(ports2) == 1:
                        ports2 = ports2[0]
                
                if type(ports2)!= type([]):
                    ports2 = [ports2]

                if type(ports1) != type([]):
                    ports1 = [ports1]

                for p1 in ports1:
                    if not p1:
                        continue

                    p2 = [port2 for port2 in ports2 \
                          if port2.get("portid", "a") == p1.get("portid", "b")]
                    
                    if p2: # Removing found port
                        ports2.remove(p2[0])

                    if p1 and p2:
                        self.add_port_diff(parent, "", p1, p2[0])
                    elif p1 and not p2:
                        self.add_port_diff(parent, "N", p1, {})

                for p2 in ports2: # If there is something left...
                    self.add_port_diff(parent, "A", {}, p2)
            

    def add_port_diff(self, port_parent, state, port1, port2):
        if (port1 or port2) and (type(port1) == type({})) and (type(port2) == type({})):
            section = port1.get("portid", False)
            if not section: # If port1 is empty, then, try port2
                section = port2.get("portid", "")
            
            parent = self.append_parent(port_parent, section, state)

            self.diff_it(parent, "",
                         _("State"), port1.get("port_state", ""),
                         port2.get("port_state", ""))
            
            self.diff_it(parent, "",
                         _("Service Name"), port1.get("service_name", ""),
                         port2.get("service_name", ""))
                
            self.diff_it(parent, "",
                         _("Product"), port1.get("service_product", ""),
                         port2.get("service_product", ""))
            
            self.diff_it(parent, "",
                         _("Service Version"), port1.get("service_version", ""),
                         port2.get("service_version", ""))
            
            self.diff_it(parent, "",
                         _("Protocol"), port1.get("protocol", ""),
                         port2.get("protocol", ""))
                
            self.diff_it(parent, "",
                         _("Extra Info"), port1.get("service_extrainfo", ""),
                         port2.get("service_extrainfo", ""))
            
            self.diff_it(parent, "",
                         _("Service Conf"), port1.get("service_conf", ""),
                         port2.get("service_conf", ""))

            # Last parent status modification
            if state.upper() == "A":
                self.set_parent_status(parent, "A")

    def add_extraports_diff(self, host_parent, state, extraports1, extraports2):
        if extraports1 or extraports2:
            section =  _("Extraports")
            parent = self.append_parent(host_parent, section, state)
            self.set_parent_status(parent, state)
            
            self.diff_it(parent, "", _("Count"), extraports1.get("count"),
                         extraports2.get("count"))
            self.diff_it(parent, "", _("State"), extraports1.get("state"),
                         extraports2.get("state"))


    def diff_it(self, parent, section, prop_name, prop1, prop2):
        if prop1 or prop2:
            state = self.diff_state(prop1, prop2)
            self.set_parent_status(parent, state)
            child = DiffTree(parent, state, section, prop_name, prop1, prop2)
            parent.childs.append(child)
            return state
        
        
    def diff_state(self, prop1, prop2):
        if prop1 == prop2:
            return "U" # Property remained "Unchanged" at the second scan
        elif prop1 == "" and prop2 != "":
            return "A" # Property "Added" at the second scan
        elif prop1 != "" and prop2 != "":
            return "M" # Property "Modified" at the second scan
        else:
            return "N" # Property "Not present" at the second scan


class DiffTree(object):
    """A Diff tree node.
    """

    is_head = property(lambda self: self.parent is None)
    is_leaf = property(lambda self: len(self.childs) == 0)
    
    def __init__(self, parent, state, section, property="", value1="", value2=""):
        self.parent = parent
        self.state = state
        self.section = section
        self.property = property
        self.value1 = value1
        self.value2 = value2
        self.childs = []
        
    def add_child(self, child):
        assert child.__class__ is DiffTree
        self.childs.append(child)
        
        
    def to_dict(self):
        dic = dict(state=str(self.state), section=str(self.section), 
                   property=str(self.property), value1=str(self.value1), 
                   value2=str(self.value2), childs=[c.to_dict() for c in self.childs])
        return dic