from __future__ import with_statement
# ------------------------------------------------------------------------------
#  *******************************************************************************
#  * COPYRIGHT Ericsson 2018
#  *
#  * The copyright to the computer program(s) herein is the property of
#  * Ericsson Inc. The programs may be used and/or copied only with written
#  * permission from Ericsson Inc. or in accordance with the terms and
#  * conditions stipulated in the agreement/contract under which the
#  * program(s) have been supplied.
#  *******************************************************************************
'''
 Access the database
'''
from com.ziclix.python.sql import zxJDBC
import ConfigParser
import os

class DbAccess:

    def __init__(self, dbPropertiesFile):
        self.hostName = ''
        self.port = ''
        self.dbName = ''
        self.dbUrl = ''
        self.rawUrl = ''
        self.userName = ''
        self.password = ''
        self.driver = ''
        self.COLUMNS = 'COLUMNS'
        self.ROWS = 'ROWS'        
        self.getConnectionDetails(dbPropertiesFile)
        self.conn = None
    

    def openConn(self):
        self.conn = zxJDBC.connect(self.dbUrl, self.userName, self.password, self.driver)

    def closeConn(self):
        # make best effort to close connection. 
        # don't worry if it fails
        try:
            self.conn.close()
        except:
            pass
        
    def updateHostname(self, hostname):
        self.hostName = hostname
        self.dbUrl = self.rawUrl + self.hostName + ':' +self.port + '/' + self.dbName 
            
    def executeSql(self, sql):
        try:
            # dynamic !=0 => faster access but does not update rowcount
            with self.conn.cursor() as c:
                c.execute(sql)
        except:
            self.closeConn()
            self.openConn()
            with self.conn.cursor() as c:
                try:
                    c.execute(sql)
                except:
                    print 'Tried twice and failed\n',sql
                    raise
                                                                 
    def getSQLResults(self, sql):
        
        columnNames = []
        rows = []
        allvalues = {self.COLUMNS : columnNames, self.ROWS : rows}
        
        with self.conn.cursor() as c:
            c.execute(sql)
            
            for column in c.description:
                columnNames.append(column[0])
                
            for result in c.fetchall():
                rows.append(result)
        return allvalues

    def runSQL(self, sql):
        try:
            with self.conn.cursor() as c:
                c.execute(sql)
                return c.fetchone()
        except:
            print 'SQL exception detected when running:',sql
            raise

    def runSQLs(self, sql):
        try:
            with self.conn.cursor() as c:
                c.execute(sql)
                return c.fetchall()
        except:
            print 'SQL exception detected when running:',sql
            raise

    def getTableList(self):
        tableList = []
        
        try:
            with self.conn.cursor() as c:
                c.tables(None, None, '%', ('VIEW',))
                for view in c.fetchall():
                    tableList.append( view[2].lower() )
                
                c.tables(None, None, '%', ('TABLE',))
                for table in c.fetchall():
                    tableList.append( table[2].lower())
        except:
            return False, 'Unable to connect to database at URL %s, with user %s and driver %s '%(self.dbUrl, self.userName, self.driver)
        return True, tableList

    def getFieldList(self, table):
        columnList= set([])
        
        try:
            with self.conn.cursor() as c:
                colSet = set([])
                c.columns(None, None, table, '%')
                for col in c.fetchall(): 
                    colSet.add( col[3].lower() )
                columnList = list(colSet)
                            
        except:
            return False, 'Unable to get fields in table %s'%table
        return True, columnList
   
    def getConnectionDetails(self, dbPropertiesFile):
        section = 'DATABASE_INFO'
        
        try :
            f = open(dbPropertiesFile)
            f.close()
        except:
            print "DB configuration file: %s not found or not readable"%dbPropertiesFile
            raise

            
        config = ConfigParser.RawConfigParser()
        config.read(dbPropertiesFile)
        try:
            self.hostName = config.get(section, 'hostName')
            self.port = config.get(section, 'port')
            self.rawUrl = config.get(section, 'dbUrl')
            self.userName = config.get(section, 'userName')
            self.password = config.get(section, 'password')
            self.driver = config.get(section, 'driver')
            self.dbName =  config.get(section, 'dbName')
            self.dbUrl = self.rawUrl+self.hostName + ':' +self.port + '/' + self.dbName 
        except Exception:
            print 'Invalid database configuration'
            raise
        
if __name__ == '__main__': 
    dbPropertiesFile = 'etc/db.cfg'
    if not os.path.exists(dbPropertiesFile):
        dbPropertiesFile = '../etc/db.cfg'
    dbAccess = DbAccess(dbPropertiesFile)
    dbAccess.openConn()
    print dbAccess.getSQLResults('select @@Version')
    
    sampleData = '../testresources/simpleTestTables.sql'    
    with open (sampleData, 'r') as data:
        testDataQueries = data.read()
    dbAccess.executeSql(testDataQueries)
    
    sql = 'select DATEFORMAT(min(datefld),\'dd-mm-yyyy\'), DATEFORMAT(min(datefld),\'yyyy-mm-dd\') from tableDHM1'
    print dbAccess.runSQL(sql)
    dbAccess.closeConn()  
    