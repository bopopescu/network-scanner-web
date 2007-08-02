# Copyright (C) 2007 Insecure.Com LLC.
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
# USA

from umitCore.I18N import _

from umitDB.Store import RawStore
from umitDB.Retrieve import InventoryRetrieve

class UpdateChanges(InventoryRetrieve, RawStore):
    """
    Updates list of changes for a given Inventory id.
    """
    
    def __init__(self, database, fk_inventory=None):
        
        InventoryRetrieve.__init__(self, database)
        RawStore.__init__(self, self.conn, self.cursor)
        self.fk_inventory = fk_inventory
        
        if fk_inventory:
            self.do_update(fk_inventory)

        
    def do_update(self, inv_id):
        """
        Perform update for Inventory id.
        """
        addresses = [ ]
        
        # get scan ids and finish time for especified inventory
        finish_data = self.get_finish_data_for_inventory_from_db(inv_id)
        
        
        # retrieve host addresses for especified inventory id
        for scan in finish_data:
            # retrieve host ids for each scan
            for host in self.get_hosts_id_for_scan_from_db(scan[0]):
                # retrieve ipv4 address for host
                addr = self.get_ipv4_for_host_from_db(host[0])
                
                if addr in addresses:
                    continue
                
                addresses.append(addr)
                
                
        # generate changes list for each address in especified inventory
        for addr in addresses:
            
            # get all host pks for especified inventory and for each address 
            # in addresses
            base_data = self.get_hosts_base_data_for_inventory_from_db(addr, 
                                                                       inv_id)
            
            if not base_data:
                print "Inventory id %d has no data for host \
address '%s' yet." % (inv_id, addr)
                continue
            
            # dict where all data will be stored
            data_dict = { }
        
            # get host and scan ids
            scan_ids = [item[0] for item in finish_data]
            host_ids = [item[0] for item in base_data]
            
            indexes = [ ]
            count = 0
            # get indexes where there is host data
            for indx, item in enumerate(scan_ids):
                try:
                    host_ids[count]
                except IndexError:
                    continue
                else:
                    indexes.append(scan_ids.index(host_ids[count]))
                    count += 1
                    
            down_time = self._check_for_downtime(finish_data, base_data)
            for item in down_time[1]:
                data_dict[item] = (_("Availability"), _("Host down"), 
                                   down_time[0][item], -1, -1)
                
            # load initial data for doing comparison
            date = finish_data[indexes[0]][1]
            hostA = base_data[0]
            self.use_dict_cursor()
            pdata1 = self.get_portid_and_state_for_host_from_db(hostA[1])
            self.use_standard_cursor()
            fpinfo1 = self.get_fingerprint_info_for_host_from_db(hostA[1])
            osmatch1 = self.get_osmatch_for_host_from_db(hostA[1])
            osclasses1 = self.get_osclasses_for_host_from_db(hostA[1])
            
            host_count = 1
            
            # now, load following data and compare against hostA
            for indx, item in enumerate(base_data[host_count:]):
                hostB = item
                
                # load data to compare against hostA
                self.use_dict_cursor()
                pdata2 = self.get_portid_and_state_for_host_from_db(hostB[1])
                self.use_standard_cursor()
                fpinfo2 = self.get_fingerprint_info_for_host_from_db(hostB[1])
                osmatch2 = self.get_osmatch_for_host_from_db(hostB[1])
                osclasses2 = self.get_osclasses_for_host_from_db(hostB[1])
                
                # compare old data against new data
                category, diff_text = self._compare_data(pdata2, fpinfo2, 
                                                         osmatch2, osclasses2,
                                                         pdata1, fpinfo1, 
                                                         osmatch1, osclasses1)

                # store in data_dict current result
                data_dict[hostA[0]] = (category, diff_text, date, hostA[1], 
                                       hostB[1])
                
                # swap data
                pdata1 = pdata2
                fpinfo1 = fpinfo2
                osmatch1 = osmatch2
                osclasses1 = osclasses2
                hostA = hostB
                
                # get next date
                date = finish_data[indexes[indx+1]][1]
            
            # now load the first entry
            data_dict[hostA[0]] = (_("Inventory"), 
                                   _("Host added to the Inventory."), date,
                                   hostA[1], hostA[1])
            
            self._insert_changes(data_dict, addr, inv_id)
            
            
    def _insert_changes(self, data_dict, addr_id, inventory_id):
        """
        Insert changes in database.
        """
        # sort dict keys in descendent order
        dict_keys = data_dict.keys()
        dict_keys.sort()
        dict_keys.reverse()
            
        # insert data into database
        fk_address = self.get_address_id_for_address_from_db(addr_id)
        for key in dict_keys:
            affected = data_dict[key][0]
            text = data_dict[key][1]
            date = data_dict[key][2]
            new_hostid = data_dict[key][3]
            old_hostid = data_dict[key][4]
            
            # check if category 'affected' already exists on database
            fk_category = self.get_inventory_change_category_id(affected)
            if not fk_category:
                # didn't exist, create it now
                self.insert_inventory_change_category_db(affected)
                fk_category = self.get_id_for("inventory_change_category")
                    
            # check if comparison is already in database
            # (this should have been done at earlier stage, but for now
            #  it is being done here)
            ret = self.get_inventory_comparison(old_hostid, new_hostid, 
                                                date, inventory_id)
                    
            if not ret:
                # need to insert new comparison
                self.insert_inventory_comparison_db(old_hostid, new_hostid, 
                                                    date, text, inventory_id, 
                                                    fk_category, fk_address)
                
            
    def _compare_data(self, pdata2, fpinfo2, osmatch2, osclasses2,
                      pdata1, fpinfo1, osmatch1, osclasses1):
        """
        Compare two sets of data.
        """
        host_diff = ''
        common_text = ''
        ports_only = None # ports diff only 
        fp_only = None # fingerprint diff only

        # compare pdataNs
        if pdata1 != pdata2:
            host_diff += self._ports_diff(pdata2, pdata1)
            fp_only = False
            ports_only = True

        # compare fpinfoNs
        # dont consider uptime and lastboot in fingerprint (will probably
        # not consider others too)
        if fpinfo1 and (fpinfo1[2:] != fpinfo2[2:]):
            space = host_diff and ' ' or ''
            common_text = _('%sFingerprint, ') % space
            ports_only = False
            if fp_only is None:
                fp_only = True

        # compare osmatchNs
        if osmatch1 != osmatch2:
            space = host_diff and ' ' or ''
            common_text += _("OS Match, ")
            fp_only = False
            ports_only = False

        # compare osclassesNs
        if osclasses1 != osclasses2:
            space = host_diff and ' ' or ''
            if len(common_text) == len("Fingerprint, "):
                common_text = common_text[:-2] + " "
            if common_text:
                common_text += _("and OS Classes")
            else:
                common_text += _("OS Classes")
            fp_only = False
            ports_only = False
                
        if common_text:
            if fp_only or len(common_text) == len(" Fingerprint, "):
                common_text = common_text[:-2]
            host_diff += common_text + _(" changed.")

        # check diff
        if host_diff:
            if ports_only:
                affected = _("Ports")
            elif fp_only:
                affected = _("Fingerprint")
            else:
                affected = _("Several")
                
        else:
            # Nothing here means "Almost nothing", there could be
            # changes in extraports for example.
            affected = _("Nothing")
            host_diff = _("No noticeables changes since last sucessfull scan.")
            
            
        return (affected, host_diff)
  

    def conjugate(self, alist):
        """
        Do conjugation based on alist size.
        It expects that alist is not empty.
        """
        if len(alist) > 1:
            verb = _('are')
            plural = _('s')
        else:
            verb = _('is')
            plural = _('')
    
        return verb, plural


    def _ports_diff(self, old, new):
        """
        Return a prettier difference between pdata.
        """
        closed_text = _("closed")
        open_text = _("open")
        now_text = _("now")
        port_text = _("Port")
        and_text = _("and")
        
        # first build dict where portid is the key
        old_dict = { }
        new_dict = { }

        for d in old:
            old_dict[d['portid']] = d['state']
        
        for d in new:
            new_dict[d['portid']] = d['state']

        # check for port changes now
        closed_ports = [ ]
        open_ports = [ ]

        for key, value in old_dict.items():
            #if new_dict.has_key(key):
            if key in new_dict:
                new_value = new_dict[key]

                if value != new_value:
                    print value, new_value, 'differs but Im not doing nothing'

            else:
                closed_ports.append(key)

        for key, value in new_dict.items():
            #if old_dict.has_key(key):
            if key in old_dict:
                old_value = old_dict[key]

                if value != old_value:
                    print value, old_value, 'differs but Im not doing nothing'

            else:
                open_ports.append(key)

        text = ''
        if closed_ports:
            verb, plural = self.conjugate(closed_ports)
            closed_ports = ', '.join([str(p) for p in closed_ports])
            closed_ports = "%s%s %s %s %s %s." % (port_text, plural, 
                                                  closed_ports, verb, 
                                                  closed_text, now_text)

        if open_ports:
            verb, plural = self.conjugate(open_ports)
            open_ports = ', '.join([str(p) for p in open_ports])
            open_ports = "%s%s %s %s %s %s." % (port_text, plural, 
                                                open_ports, verb, 
                                                open_text, now_text)

        if open_ports and closed_ports:
            text = open_ports[:-1 -len(now_text) -1] + ' ' + and_text + \
                   ' ' + closed_ports
        elif open_ports:
            text = open_ports
        elif closed_ports:
            text = closed_ports

        return text
    
  
    def _check_for_downtime(self, all_scans, host_scans):
        """
        Return scan id associated to a date showing in what scans a host
        was down.
        """
        down_d = { }
        down_order = [ ]
        d = 0
        for item in all_scans:
            try:
                host_scans[d][0]
            except IndexError:
                down_order.append(item[0])
                down_d[item[0]] = item[1]
            else:
                if item[0] == host_scans[d][0]:
                    d += 1
                else:
                    down_order.append(item[0])
                    down_d[item[0]] = item[1]
        
        return (down_d, down_order)


class ChangesRetrieve(InventoryRetrieve):
    """
    Retrieves changes from database in many ways.
    """
    
    def __init__(self, database):
        InventoryRetrieve.__init__(self, database)
        

    def get_categories_id_name(self):
        """
        Return all category_id, category_name from database.
        """
        self.cursor.execute("SELECT * FROM inventory_change_category")
        data = self.cursor.fetchall()
        
        return data
    
        
    def get_categories_name(self):
        """
        Return all categories name from database.
        """
        self.cursor.execute("SELECT name FROM inventory_change_category")
        ctg = self.cursor.fetchall()
        
        return ctg
    
    
    def get_category_name_by_id(self, cid):
        """
        Return category name with especified id.
        """
        name = self.cursor.execute("SELECT name FROM inventory_change_category\
                                    WHERE pk=?", (cid, )).fetchone()

        if name:
            return name[0]
    
    
    def get_category_id_by_name(self, name):
        """
        Return category id with especified name.
        """
        cid = self.cursor.execute("SELECT pk FROM inventory_change_category \
                                   WHERE name=?", (name, )).fetchone()[0]
        
        return cid
        

    def timerange_changes_data(self, start, end):
        """
        Retrieve changes data in a timerange.
        """
        data = self.cursor.execute("SELECT fk_category, short_description, \
        entry_date, fk_inventory, fk_address, old_hostid, new_hostid \
        FROM _inventory_changes WHERE entry_date >= ? AND \
        entry_date < ? ORDER BY entry_date DESC", (start, end)).fetchall()
        
        return data
        
    def timerange_changes_categoryid_data(self, fk_category, start, end):
        """
        Retrieve changes data in a timerange for an especific category id.
        """
        data = self.cursor.execute("SELECT fk_category, short_description, \
        entry_date, fk_inventory, fk_address, old_hostid, new_hostid \
        FROM _inventory_changes WHERE fk_category=? AND entry_date >= ? AND \
        entry_date < ? ORDER BY entry_date DESC", (fk_category, start, 
                                                   end)).fetchall()
        
        return data
    
    
    def timerange_changes_categoryname_data(self, category, start, end):
        """
        Retrieve changes data in a timerange for an especific category name.
        """
        data = self.cursor.execute("SELECT fk_category, short_description, \
        entry_date, fk_inventory, fk_address, old_hostid, new_hostid \
        FROM _inventory_changes JOIN inventory_change_category as icc ON \
        (_inventory_changes.fk_category = icc.pk) WHERE icc.name=? AND \
        entry_date >= ? AND entry_date < ? \
        ORDER BY entry_date DESC", (category, start, end)).fetchall()
        
        return data
        

    def timerange_changes_count(self, start, end):
        """
        Get number of changes in a timerange.
        """
        count = self.cursor.execute("SELECT pk FROM _inventory_changes WHERE \
                           entry_date >= ? AND entry_date < ?", (start, 
                                                                end)).fetchall()
        
        return len(count)
    
    
    def timerange_changes_categoryid_count(self, fk_category, start, end):
        """
        Get number of changes in a timerange for an especific category id.
        """
        self.cursor.execute("SELECT pk FROM _inventory_changes WHERE \
                             fk_category=? AND entry_date >= ? AND \
                             entry_date < ?", (fk_category, start, end))
        count = self.cursor.fetchall()
        
        return len(count)
        
        
    def timerange_changes_categoryname_count(self, category, start, end):
        """
        Get number of changes in a timerange for an especific category name.
        """
        count = self.cursor.execute("SELECT pk FROM _inventory_changes JOIN \
                           inventory_change_category as icc ON \
                           (_inventory_changes.fk_category = icc.pk) WHERE \
                           icc.name=? AND entry_date > ? AND entry_date < ?", 
                           (category, start, end)).fetchall()
        
        return len(count)

    
