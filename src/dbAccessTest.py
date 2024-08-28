'''
------------------------------------------------------------------------------
 *******************************************************************************
 * COPYRIGHT Ericsson 2015
 *
 * The copyright to the computer program(s) herein is the property of
 * Ericsson Inc. The programs may be used and/or copied only with written
 * permission from Ericsson Inc. or in accordance with the terms and
 * conditions stipulated in the agreement/contract under which the
 * program(s) have been supplied.
 *******************************************************************************
'''
import unittest
import dbAccess as DbAccess

class Test(unittest.TestCase):
    dbPropertiesFile = '../etc/db.cfg'
    dbAccess = DbAccess.DbAccess(dbPropertiesFile)
    
    def setUp(self):
        self.dbAccess.openConn()


    def tearDown(self):
        self.dropTable()
        self.dbAccess.closeConn()
    
    def createTable(self):        
        createTableSql = 'drop table if exists test1; create table test1 (col1 as int);'       
        insertDataSql = 'insert into test1 (col1) values (1);'
        
        self.dbAccess.executeSql(createTableSql)
        self.dbAccess.executeSql(insertDataSql)  
    
    def dropTable(self):
        dropTableSql = 'drop table if exists test1;'
        self.dbAccess.executeSql(dropTableSql)
        
    def test_getSQLResults_1(self):
        
        result = self.dbAccess.getSQLResults('select 1')
        
        self.assertEquals(2, len(result))
        
        row = result.get(self.dbAccess.ROWS)
        self.assertEquals(1, row[0][0])
        

    def test_executeSql_1(self):  
        selectSql = 'select col1 from test1;'
        self.createTable()

        result = self.dbAccess.getSQLResults(selectSql)
        
        self.assertEquals(2, len(result))
        
        row = result.get(self.dbAccess.ROWS)
        self.assertEquals(1, row[0][0])
        

    def test_getTableList_1(self):
        tableName = 'test1'
        
        self.createTable()

        ok, tableList = self.dbAccess.getTableList()
        self.assertTrue(ok)
        
        tableExists = False
        if tableName in tableList:
            tableExists = True
        
        self.assertTrue(tableExists)
        
    
    def test_getTableList_2(self):
        tableName = 'test1'        

        ok, tableList = self.dbAccess.getTableList()
        self.assertTrue(ok)
        
        tableExists = False
        if tableName in tableList:
            tableExists = True
        
        self.assertFalse(tableExists)
        
    def test_getFieldList_1(self):
        tableName = 'test1'
        colName = 'col1'
        
        self.createTable()

        ok, fieldList = self.dbAccess.getFieldList(tableName)
        self.assertTrue(ok)
        
        fieldExists = False
        if colName in fieldList:
            fieldExists = True
        
        self.assertTrue(fieldExists)
        
    
    def test_getFieldList_2(self):
        tableName = 'test1'
        colName = 'invalidField'
        
        self.createTable()

        ok, fieldList = self.dbAccess.getFieldList(tableName)
        self.assertTrue(ok)
        
        fieldExists = False
        if colName in fieldList:
            fieldExists = True
        
        self.assertFalse(fieldExists)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()