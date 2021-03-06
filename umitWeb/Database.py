#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Rodolfo da Silva Carvalho <rodolfo.ueg@gmail.com>
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

import re
import os
import pickle
from types import ListType
from traceback import print_exc
from umitWeb.WebPaths import WPath as Path

try:
    from sqlite3 import dbapi2 as dbmodule
    import sqlite3 as sqlite
except ImportError:
    from pysqlite2 import dbapi2 as dbmodule
    import pysqlite2 as sqlite

try:
    webdb = Path.web_db
except:
    webdb = os.path.join(Path.config_dir, "web.db")
    Path.web_db = webdb
    
__connection__ = dbmodule.connect(Path.web_db)


class DBError(Exception):
    pass


class Model(object):
    """This is a basic representation of a Table in UmitWeb database. It cannot be directly instantiated.
    
    To create a model, you need to do the following steps:
    
    * Create a class inheriter from `Model`
    * Overrides `_sqlfields` and `_table` attributes
    * Write a `save` method.
    
    
    Example:
    
    >>> class SampleModel(Model):
    ...    _sqlfields = [ 
    ...        "a_field VARCHAR(32) NOT NULL", 
    ...        "another_field INT DEFAULT -1"
    ...    ]
    ...    _table = "samples"
    
    """
    _sqlfields = []
    _table = None
    _id_field = "id"
    
    def __init__(self):
        self._connection = __connection__
        self.__setattr__(self._id_field, None)

    @classmethod
    def _process_result(self, cursor, result):
        cols = [e[0] for e in cursor.description]
        ret_data = None
        if result:
            ret_data = []
            for i in xrange(len(result)):
                res_row = {}
                for j in xrange(len(cols)):
                    res_row[cols[j]] = result[i][j]
                ret_data.append(self(**res_row))
                
        if ret_data:
            if len(ret_data) == 1:
                return ret_data[0]
            else:
                return ret_data
        else:
            return None

    @classmethod
    def get(self, id):
        """Get a single object, given its id."""
        cursor = __connection__.cursor()
        cursor.execute("SELECT * FROM %s where %s=?" % (self._table, self._id_field), (id,))
        return self._process_result(cursor, cursor.fetchall())

    @classmethod
    def get_list(self, **params):
        """Get a list of objects that match with params."""
        operation_patterns = (
            (r"^(?P<field>.+)__gt$", "%s > %s"),
            (r"^(?P<field>.+)__gte$", "%s >= ?"),
            (r"^(?P<field>.+)__lt$", "%s < ?"),
            (r"^(?P<field>.+)__lte$", "%s <= ?"),
            (r"^(?P<field>.+)__contains$", "%s LIKE ?"),
            (r"^(?P<field>.+)__icontains$", "%s ILIKE ?"),
            (r"^.*$", "%s = ?")
        )
        where_list = []
        param_list = []
        for k in params.keys():
            
            match = None
            strfmt = ""
            for p in operation_patterns:
                match = re.match(p[0], k)
                if match:
                    col = match.groupdict()['field']
                    strfmt = p[1]

            if match:
                where_list.append(strfmt % col)
                param_list.append(params[k])

        query = "SELECT * FROM %s WHERE 1=1" % self._table
        query += " AND ".join(where_list)
        cursor = __connection__.cursor()
        cursor.execute(query, param_list)
        result = self._process_result(cursor, cursor.fetchall())
        if type(result) == ListType:
            return result
        elif result is not None:
            return [result]

    def delete(self):
        """Removes the current object from the database."""
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM %s WHERE %s=?" % (self._table, self._id_field), self.id)
        self._connection.commit()

    def _create(self):
        cursor = self._connection.cursor()
        creation_sql = "CREATE TABLE %s(%s)" % (self._table, ",\n".join(self._sqlfields))
        cursor.execute(creation_sql)
        
    def save(self):
        raise DBError("Not Implemented.")
    

class SessionData(Model):
    """Model for handle data stored in http sessions."""
    
    _sqlfields = [
        "id CHAR(32) not null",
        "pickled_data BLOB",
        "primary key(id)"
        ]
    
    _table = "session"
    
    def __init__(self, id=None, pickled_data=None):
        Model.__init__(self)
        self.id = id
        pickled_data = pickled_data or pickle.dumps({})
        try:
            self.pickled_data = pickle.loads(pickled_data)
        except Exception, ex:
            print_exc()
            raise DBError("Error loading pickled data: %s" % str(ex))
        

    def save(self):
        if self.get(self.id):
            sql = "UPDATE session SET pickled_data=? WHERE id=?"
        else:
            sql = "INSERT INTO session(pickled_data, id) VALUES (?, ?)"
        cursor = self._connection.cursor()
        pickled_data = sqlite.Binary(pickle.dumps(self.pickled_data))
        cursor.execute(sql, (pickled_data, self.id))
        self._connection.commit()
        
    def delete(self):
        if self.get(self.id):
            cursor = self._connection.cursor()
            sql = "DELETE FROM session WHERE id=?"
            cursor.execute(sql, (self.id,))
            self._connection.commit()
    

def __init():
    classes = Model.__class__.__subclasses__(Model)
    for Class in classes:
        Class()._create()
    __connection__.commit()

def __clean():
    classes = Model.__class__.__subclasses__(Model)
    drop_sql = "DROP TABLE %s"
    for Class in classes:
        obj = Class()
        cursor = __connection__.cursor()
        cursor.execute(drop_sql % obj.table)

def __verify():
    cursor = __connection__.cursor()
    try:
        cursor.execute("SELECT * FROM session")
    except dbmodule.OperationalError, ex:
        __init()

__verify()
