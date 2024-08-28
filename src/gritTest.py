''' This is test'''

# ------------------------------------------------------------------------------
#  *******************************************************************************
#  * COPYRIGHT Ericsson 2015
#  *
#  * The copyright to the computer program(s) herein is the property of
#  * Ericsson Inc. The programs may be used and/or copied only with written
#  * permission from Ericsson Inc. or in accordance with the terms and
#  * conditions stipulated in the agreement/contract under which the
#  * program(s) have been supplied.
#  *******************************************************************************
import unittest
import sys

from grit import Grit
from dbAccess import DbAccess

testResourcesDir = '../testresources'
dbPropertiesFile = "../etc/db.cfg"
rulePass = True
ruleFail = False

def _runSqlFromFile(dbPropertiesFile, testDataFile):
    with open (testDataFile, 'r') as data:
        testDataQueries = data.read()

    _runSQL(dbPropertiesFile, testDataQueries)

def _runSQL(dbPropertiesFile, query):
    dbAccess = DbAccess(dbPropertiesFile)
    dbAccess.openConn()
    dbAccess.executeSql(query)
    dbAccess.executeSql("commit;")
    dbAccess.closeConn()

def populateTestData(testDataList):
    for sqlFileName in testDataList:
        _runSqlFromFile(dbPropertiesFile, sqlFileName)

def cleanupTestData(testDataList):
    filesToDrop = ''
    for f in testDataList:
        text = [line.strip() for line in open(f)]
        for line in text:
            if line.startswith('create table '):
                tableName = line.split(' ')[2] # extract the third word
                filesToDrop += 'drop table if exists %s;'% tableName
    print 'about to execute ', filesToDrop
    _runSQL(dbPropertiesFile, filesToDrop)


class Test(unittest.TestCase):
    # set to False to prevent output from being redirected
    allowRedirect = True

    def _checkResults(self, actual, assertTrue):
        i = 0
        while i < len(actual):
            k = 0
            result = actual[i]
            while k < len(result):
                if assertTrue:
                    self.assertTrue(result[k+1], 'Rule: "' + result[k] + '" fails. It should pass')
                else:
                    self.assertFalse(result[k+1], 'Rule: "' + result[k] + '" passes. It should fail')
                k += 2
            i += 1

    def _checkResultsEqual(self, expected, actual):
        for i in range(len(expected)):
            if (actual[i][0]): # is valid
                if actual[i][1]: # is rule
                    if actual[i][2]: # is ok
                        self.assertTrue(expected[i])
                    else:
                        self.assertFalse(expected[i])
                else:
                    self.assertTrue(expected[i])
            else:
                self.assertFalse(expected[i])

    def _cleanupTables(self, tables):
        sqlTemplate = 'drop table if exists %s;'
        for table in tables:
            query = sqlTemplate%table
            _runSQL(self.dbPropertiesFile, query)

    def _runMain(self, argv, redirectOutput):
        outputFileName = testResourcesDir + '/standardOutputRedirect.log'
        originalStdOut = sys.stdout
        with open(outputFileName, 'w') as outputFile:
            if redirectOutput and self.allowRedirect:
                sys.stdout = outputFile
            grit = Grit(argv)
            results = grit.results
            #reset the standard out
            sys.stdout = originalStdOut

        return results

    def test_main_simpleTestTables_4(self):
        file1 = testResourcesDir + '/test_data_2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile, '-t',  '../testresources/test_data_2_table_config.cfg', '-r', '../testresources/test_data_1.rules2', '-v']
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def test_main_1(self):
        file1 = testResourcesDir + '/test_data_2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/test_data_2_table_config.cfg', '-r', '../testresources/test_data_1.rules2', '-D', '2015-04-16' ,'-v']
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def test_main_simpleTestTables_2(self):
        file1 = testResourcesDir + '/test_data_2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/test_data_2_table_config.cfg', '-r', '../testresources/test_data_1.rules', '-v']
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def test_main_simpleTestTables_3(self):
        # check table config not case sensitive
        file1 = testResourcesDir + '/test_data_2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/test_data_2_table_config.cfg', '-r', '../testresources/test_data_1.rules']
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def test_main_dataHandling(self):
        # check table config not case sensitive
        file1 = testResourcesDir + '/basic_test.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/basic_test.cfg', '-r', '../testresources/data_handling.rules', '-N','-v','-e']
        actual = self._runMain(argv, True)
        expected = [[True, True, True]]
        self._checkResultsEqual(expected, actual)


    def atest_main_file_to_raw_test_1(self):
        file1 = testResourcesDir + '/test_data_1.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/test_data_1_table_config.cfg', '-r', '../testresources/test_data_1.rules', '-v', 'showSQL=True' ]
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def atest_main_lookup_test(self):
        file1 = testResourcesDir + '/lookup_test2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/lookup_test.cfg', '-r', '../testresources/lookup_test.rules', '-v', 'showSQL=True' ]
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def atest_main_lookup_test_fails(self):
        file1 = testResourcesDir + '/lookup_test2.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/lookup_test.cfg', '-r', '../testresources/lookup_test_fail.rules' ]
        try:
            self._runMain(argv, True)
            raise "Expected SQL exceptions!"
        except:
            pass

    def atest_main_null_test_pass(self):
        file1 = testResourcesDir + '/null_test.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/null_test.cfg', '-r', '../testresources/null_test_pass.rules', '-N', '-v']
        actual = self._runMain(argv, True)
        expected = [True]*len(actual)
        self._checkResultsEqual(expected, actual)

    def atest_main_null_test_fail(self):
        file1 = testResourcesDir + '/null_test.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/null_test.cfg', '-r', '../testresources/null_test_fail.rules', '-N', '']
        actual = self._runMain(argv, True)
        expected = [False]*len(actual)
        self._checkResultsEqual(expected, actual)

    def badtest_main_basic_1(self):
        # basic tests with floating data
        file1 = testResourcesDir + '/basic_test.sql'
        _runSqlFromFile(dbPropertiesFile, file1)
        argv = ['-d', dbPropertiesFile,'-t',  '../testresources/basic_test.cfg', '-r', '../testresources/basic_test.rules', 'verbose=True' , '-N']
        actual = self._runMain(argv, True)
        expected = [True, False, False,False, False, False, True, True, False]
        self._checkResultsEqual(expected, actual)

