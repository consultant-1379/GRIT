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


import sys
import ConfigParser
import os.path
import parser as Parser
import grammar as Grammar
import generateSQL as GenerateSQL
import dbAccess as DbAccess
import overlap as Overlap



class Grit:
    version = '1.14.21'

    def __init__(self, argv = [], action = ''):
        self.ruleVal=''
        self.inTable = {}
        self.outTable = {}
        self.inFields = []
        self.tableData = {}
        self.outFields = []
        self.outputCSVFileLocation = ''
        self.leftVerbose = []
        self.rightVerbose = []
        self.whereIn = None  # where clause to select overlapping data from 'in' table
        self.whereOut = None # where clause to select overlapping data from 'out' table
        self.aliasDict = {}
        self.rulesFile = ''
        self.results = []
        self.dbAccess = None
        self.noDate, self.config, self.section, self.date = '','','',''
        self.isVerbose = False # show results of queries
        self.showSQL = False  # show SQL used to to run queries.
        self.failOnError = False
        self.testInputExistsFlag = False
        if len(argv) == 0:
            argv = sys.argv # get them from the environment
        self.rule = []
        self.leftStatus = []
        self.rightStatus = []
        self.leftVerboseIndex=0
        self.rightVerboseIndex=0
        self.isInputFieldExist=False
        self.isOutputFieldExist=False
        self.errMsg='Ignoring rule as it contains unknown input and output field'
        self.errInputMsg='Input field is not present'
        self.errOutputMsg='Output field is not present'
        self.main(argv, action)

    def _setupArguments(self, argv, action):
        tableDetailsFile = 'etc/new_table.cfg'
        if not os.path.exists(tableDetailsFile):
            tableDetailsFile = '../etc/new_table.cfg'
        dbPropertiesFile = 'etc/db.cfg'
        if not os.path.exists(dbPropertiesFile):
            dbPropertiesFile = '../etc/db.cfg'
        rulesFile = 'etc/rules.rules'
        if not os.path.exists(rulesFile):
            rulesFile = '../etc/rules.rules'
        
        hostname = ''
        src = ''
        dst = ''
        self.date = ''
        self.noDate = False
        for arg in argv:
            if '=' in arg:
                if arg.startswith('hostname='):
                    hostname = arg.split('=')[1]
                if arg.startswith('section='): # overide which section of the table_config to use
                    self.section = arg.split('=')[1]
                if arg.startswith('tableconfig='):
                    tableDetailsFile = arg.split('=')[1]
                if arg.startswith('rules='):
                    rulesFile = arg.split('=')[1]
                if arg.startswith('dbproperties='):
                    dbPropertiesFile = arg.split('=')[1]
                if arg.startswith('in='):
                    src = arg.split('=')[1]
                if arg.startswith('out='):
                    dst = arg.split('=')[1]
                if arg.startswith('verbose='):
                    self.isVerbose = True if arg.split('=')[1] == 'True' else False
                if arg.startswith('showSQL='):
                    self.showSQL = True if arg.split('=')[1] == 'True' else False
                if arg.startswith('fail='):
                    self.failOnError = True if arg.split('=')[1] == 'True' else False
                if arg.startswith('noDate='):
                    self.noDate = True if arg.split('=')[1] == 'True' else False
                if arg.startswith('date='):
                    self.date = arg.split('=')[1]
                if arg.startswith('csvFileLoc='):
                    self.outputCSVFileLocation = arg.split('=')[1]
                
        # -- or -- for options without '='
        numArgs = len(argv) 
        i = 0
        while i < numArgs:
            opt = argv[i]
            arg = ''
            if (i+1) < numArgs :
                arg = argv[i+1]
            if arg in ('-?', '--help', 'help'):
                usage()
                return 0
            elif opt in ('-h', '--hostname'): # override which host to use
                hostname = arg
            elif opt in ('-t', '--tableconfig'):
                tableDetailsFile = arg
            elif opt in ('-r', '--rules'):
                rulesFile = arg
            elif opt in ('-d', '--dbproperties'):
                dbPropertiesFile = arg
            elif opt in ('-v', '--verbose'):
                self.isVerbose = not self.isVerbose
            elif opt in ('-s', '--showSQL'):
                self.showSQL = True
            elif opt in ('-f', '--failOnError'):
                self.failOnError = True
            elif opt in ('-e', '--InputExists'):
                self.testInputExistsFlag = True
            elif opt in ('-I', '--in') :
                src = arg
            elif opt in ('-O', '--out'):
                dst = arg
            elif opt in ('-N', '--noDate'):
                self.noDate = True
            elif opt in ('-D', '--date'):
                self.date = arg
            elif opt in ('-csv', '--csvFileLoc'):
                self.outputCSVFileLocation = arg
            elif opt in ('-ruleType', '--ruleTypes'):
                self.ruleVal = arg
            i += 1
        # check file specified exists and is readable
        if os.path.isfile(dbPropertiesFile) and os.access(dbPropertiesFile, os.R_OK):
            self.dbAccess = DbAccess.DbAccess(dbPropertiesFile)
        else:
            usage()
            raise ValueError('Specified database properties file %s, does not exist or can not be read. ' % dbPropertiesFile)

        if action == 'analyse':
            self.noDate = True # prevent Metadata check from looking for data
            print 'Analysis for %s with %s:'%(rulesFile, tableDetailsFile)

        if not os.path.isfile(tableDetailsFile) or not os.access(tableDetailsFile, os.R_OK):
            usage()
            raise ValueError( 'Specified table properties file %s, does not exist or can not be read. ' % tableDetailsFile)

        if not self.loadTableConfig(tableDetailsFile, src, dst):
            raise ValueError( 'Specified table properties file %s does not contain valid configuration. ' % tableDetailsFile)

        # command line overrides
        if hostname != '':
            self.dbAccess.updateHostname(hostname)
#         if src != '':
#             self.inTable = src
#         if dst != '':
#             self.outTable = dst

        if os.path.isfile(rulesFile) and os.access(rulesFile, os.R_OK):
            self.rulesFile = rulesFile
        else:
            usage()
            raise ValueError( 'Specified rules file %s, does not exist or can not be read. ' % rulesFile)

        return 0

    def setRange(self, date, inTab, outTab):
        inOptions = [inTab, self.tableData[inTab]['date'], self.tableData[inTab]['hour'], self.tableData[inTab]['min']]
        outOptions = [outTab, self.tableData[outTab]['date'], self.tableData[outTab]['hour'], self.tableData[outTab]['min']]
        try:
            overlap = Overlap.Overlap(self.dbAccess, inOptions, outOptions,self.ruleVal)
        except:
            return False
        #print date
        ok, whereIn, whereOut = overlap.getOverlap(date)
        self.whereIn = whereIn
        self.whereOut= whereOut
        return ok

    def loadTableConfig(self, cfgFile, src, dst):
        ''' Read the specified table configuration file
        '''
        config = ConfigParser.RawConfigParser()
        config.optionxform = str  # make keys case sensitive

        config.read(cfgFile)
        if not self.section or not config.has_section(self.section):
            self.section = 'run_comparisons'

        try:
            # get the keys from the main section
            options = config.options(self.section)
        except:
            # there is no [run_comparisions] section (or its override)
            return False

        i = 0
        for opt in options:
            if config.has_section(opt):
                self._getTableDateInfo(config, opt)
            else:
                print "No section found for input %s"%opt
                return False
            tmpOut = config.get(self.section, opt)
            if config.has_section(tmpOut):
                self._getTableDateInfo(config, tmpOut)
            self.inTable[i] = opt
            self.outTable[i] = tmpOut
            i += 1
        return True

    def _getTableDateInfo(self, config, table):
        if table not in self.tableData:
            d,h,m = '','',''
            try:
                h = config.get(table, 'hour')
                m = config.get(table, 'min')
                d = config.get(table, 'date')
            except:
                pass
            self.tableData[table]={'date': d, 'hour': h,'min': m}


    def getMetaData(self, inTable, outTable):
        # check tables exist in db (and that we can access db!)
        ok, tableList = self.dbAccess.getTableList()
        if not ok:
            print 'Failed to get list of tables from database. Error reported is ',tableList
            return False
        if inTable.lower() not in tableList:
            print 'Specified input table %s not found in database'%inTable
            return False

        if outTable.lower() not in tableList:
            print 'Specified output table %s not found in database'%inTable
            return False

        ok, self.inFields = self.dbAccess.getFieldList(inTable)
        if not ok:
            print 'Failed to get list of fields in specified input table tables from database. Error reported is ',self.inFields
            return False

        ok, self.outFields = self.dbAccess.getFieldList(outTable)
        if not ok:
            print 'Failed to get list of fields in specified output table tables from database. Error reported is ',self.outFields
            return False

        # find data overlap
        # Check data exists
        if not self.noDate:
            ok = self.setRange(self.date, inTable, outTable)
            if not ok:
                print 'No data found to test with!', self.whereIn
                return ok

        return True

    def _getRules(self):
        error = False
        rules = []
        lineNum = 0

        text = [line.strip() for line in open(self.rulesFile)]
        parser = Parser.Parser()

        for line in text:
            lineNum +=1

            ok = False
            ok, offset, err = parser.checkRule(line)
            if ok:
                rules.append(line)
            else:
                print ' Syntax error detected on line %d of %s. Rule will be excluded:'%(lineNum, self.rulesFile)
                print '  '+line
                print '  '+' '*offset+'^ '+err
                error = True

        return error, rules

    def _runRules(self, rules, inTable, outTable):
        lineNum = 0
        invalidRule = False
        failedRule = False
        ok = True
        genSQL = GenerateSQL.GenerateSQL(inTable, outTable, self.whereIn, self.whereOut)
        tab1eNames = genSQL.getTableNames()

        for rule in rules:
            self.rule.append(rule)
            lineNum +=1
            print lineNum,':',rule
            grammar = Grammar.Grammar(rule, self.aliasDict, self.isVerbose )
            isValid,isRule = self._verifyGrammar(grammar)
            if isValid:
                if isRule:
                    comparisonQueries = genSQL.getSQL(grammar)
                    if self.isVerbose and self.showSQL:
                        self._printQueries(comparisonQueries)
                    ok = self._runComparisons(comparisonQueries, tab1eNames)
                    if not ok:
                        failedRule = True
            else:
                invalidRule = True # invalid rule

            tmpResult = [isValid, isRule, ok]
            self.results.append(tmpResult)

            if self.failOnError and (invalidRule or failedRule) :
                print ' Failing on error'
                break
        retCode = 0 # all is good
        if invalidRule:
            retCode = 3
        if failedRule: # has precedents over invalid rule
            retCode = 2
        return retCode

    def _analyseRules(self, rules, inTable, outTable, inFlds, outFlds):
        for rule in rules:
            grammar = Grammar.Grammar(rule, self.aliasDict, self.isVerbose )
            if grammar.isAlias():
                self.aliasDict = grammar.aliasDict
            else:
                if grammar.isRule() and grammar.testInFields(self.inFields) and grammar.testOutFields(self.outFields):
                    for fld in grammar.inChkFld:
                        if fld in inFlds:
                            inFlds[fld] += 1
                    for fld in grammar.outChkFld:
                        if fld in outFlds:
                            outFlds[fld] += 1

    def _outputAnalysis(self, tableDict):
        ''' Output the rules of rules analysis '''
        for table in tableDict:
            print ' %s'%table
            unref = []
            for fld, cnt in tableDict[table].iteritems():
                if cnt > 0:
                    print ' %24s : %4d'%(fld, cnt)
                else:
                    unref.append(fld)
            print 'unreferenced fields : %4d out of %d (%.2f%%)' % (len(unref), len(tableDict[table]), len(unref)*100.0/len(tableDict[table]))
            print ','.join(unref)

    def _verifyGrammar(self, grammar):
        ''' return isValid, isExecutable
        '''
        isValid = True
        isRule = True
        isInRule = True
        isOutRule = True
        self.isInputFieldExist=False
        self.isOutputFieldExist=False

        if not grammar.isValid():
            print 'Not a valid Rule'
            self.leftStatus.append('Not a valid Rule')
            self.rightStatus.append('Not a valid Rule')
            isValid = False
            isRule = False
            return isValid, isRule

        if not grammar.testInFields(self.inFields):
            isInRule = False

        if not grammar.testOutFields(self.outFields):
            isOutRule = False

        if grammar.isAlias():
            self.aliasDict = grammar.aliasDict
            print 'Updating alias dictionary'
            self.leftStatus.append('Updating alias dictionary')
            self.rightStatus.append('Updating alias dictionary')
            isRule = False
            return isValid, isRule

        if(not(isInRule) and not(isOutRule)):
            isRule=False
            print self.errMsg
            self.leftStatus.append(self.errMsg)
            self.rightStatus.append(self.errMsg)
            return isValid, isRule

        if(not(isInRule) and isOutRule):
            isRule=True
            self.isOutputFieldExist=True
            self.isInputFieldExist=False
            self.leftStatus.append(self.errInputMsg)
            return isValid, isRule

        if(not(isOutRule) and isInRule):
            isRule=True
            self.isInputFieldExist=True
            self.isOutputFieldExist=False
            self.rightStatus.append(self.errOutputMsg)
            return isValid, isRule

        return isValid, isRule

    def _runComparisons(self, sql, tableNames):
        leftTableQueryPos = 0
        rightTableQueryPos = 1
        leftRightQueryPos = 2
        rightLeftQueryPos = 3
        passDataQueryPosLeft = 4
        passDataQueryPosRight = 5
        queryPosLeft=6
        queryPosRight=7
        cleanupTablesPos = 8
        LEFT = 'Left'
        RIGHT = 'Right'
        if(self.isOutputFieldExist):
            self._transformData(sql[rightTableQueryPos])
        elif(self.isInputFieldExist):
            self._transformData(sql[leftTableQueryPos])
        else:
            self._transformData(sql[leftTableQueryPos])
            self._transformData(sql[rightTableQueryPos])
        if self.testInputExistsFlag:
            if (not self.isInputFieldExist) and self.isOutputFieldExist:
                    print '  Left Side : Input field is not present'
                    okLeft = False
            elif not self._checkDataExists(LEFT,tableNames):
                    print '  Left Side : No input data'
                    okLeft = False
                    self.leftStatus.append('No Input Data')
            else:
                if(self.isInputFieldExist):
                    self._displayTable(LEFT, sql[queryPosLeft])
                    okLeft = False
                else:
                    okLeft = self._compareTables(LEFT, sql[leftRightQueryPos], sql[passDataQueryPosLeft])
                if okLeft:
                    self.leftStatus.append('PASS')
                else:
                    self.leftStatus.append('FAIL')

            if(not self.isOutputFieldExist) and self.isInputFieldExist:
                    print '  Right Side : Output field is not present'
                    okRight = False

            elif not self._checkDataExists(RIGHT,tableNames):
                    print '  Right Side : No Output data'
                    okRight = False
                    self.rightStatus.append('No Output Data')

            else:
                if (self.isOutputFieldExist):
                    self._displayTable(RIGHT, sql[queryPosRight])
                    okRight = False
                else:
                    okRight = self._compareTables(RIGHT, sql[rightLeftQueryPos], sql[passDataQueryPosRight])
                if okRight:
                    self.rightStatus.append('PASS')
                else:
                    self.rightStatus.append('FAIL')
        else:
            okLeft = self._compareTables(LEFT, sql[leftRightQueryPos], sql[passDataQueryPosLeft])
            if okLeft:
                self.leftStatus.append('PASS')
            else:
                self.leftStatus.append('FAIL')
            okRight = self._compareTables(RIGHT, sql[rightLeftQueryPos], sql[passDataQueryPosRight])

            if okRight:
                self.rightStatus.append('PASS')
            else:
                self.rightStatus.append('FAIL')
        self._cleanupTables(sql[cleanupTablesPos])
        return okLeft and okRight
        
    # Test for the presence of input and output data in  left and right Transforms
    def _checkDataExists(self,side,tableNames):
        sqlTemplate = 'select sum(cnt) from (select count(*) as cnt from %s union all select count(*) as cnt from %s) as tmp'
        if side=='Left':
            sql = sqlTemplate%(tableNames[0], tableNames[1])
        elif side=='Right':
            sql = sqlTemplate%(tableNames[2], tableNames[3])
        try:
            inputCnt = self.dbAccess.getSQLResults(sql)
            return inputCnt[self.dbAccess.ROWS][0][0]>0
        except:
            return False

    def _printQueries(self, queries):
        for query in queries:
            print query

    def _transformData(self, table):
        self.dbAccess.executeSql(table)

    def _cleanupTables(self, sql):
        self.dbAccess.executeSql(sql)

    def _compareTables(self, ruleSide, failDataQuery, passDataQuery):
        ok = True
        comparisonResults = self.dbAccess.getSQLResults(failDataQuery)

        if len(comparisonResults[self.dbAccess.ROWS]) == 0 :
            print '  %-5s Side : PASS'%ruleSide
            if self.isVerbose:
                passComparisonResults = self.dbAccess.getSQLResults(passDataQuery)
                self._printResults(passComparisonResults, ruleSide)
        else:
            print '  %-5s Side : FAIL'%ruleSide
            ok = False
            if self.isVerbose:
                self._printResults(comparisonResults, ruleSide)
        return ok

    def _displayTable(self, ruleSide, failDataQuery):
        results = self.dbAccess.getSQLResults(failDataQuery)
        print '  %-5s Side : FAIL'%ruleSide
        if self.isVerbose:
            self._printResults(results, ruleSide)


    def _printResults(self, results, ruleSide):
        print '   Num_excess: Transform value'

        rows = results.get(self.dbAccess.ROWS)
        for row in rows:
            print '  %10s : %s'%(row[0], row[1])

            if ruleSide == 'Left':
                self.leftVerbose.append(str(row[0]))
                self.leftVerbose.append(str(row[1]))
            else:
                self.rightVerbose.append(str(row[0]))
                self.rightVerbose.append(str(row[1]))
        if ruleSide == 'Left':
            self.leftVerbose.extend(';')
        else:
            self.rightVerbose.extend(';')

    def main(self, argv, action):
        retCode, text = self.main2(argv, action)
        if retCode != 0 and action != 'analyse':
            raise RuntimeError('Errors Detected. '+text)

    def main2(self, argv, action):
        '''
        return 0 for success, 1 for rule(s) failed, 2 data not accessible, 3 rules(s) invalid, 3+ other error
        '''
        retCode = self._setupArguments(argv, action) # initialise everything
        if retCode > 0:
            self.dbAccess.closeConn()
            return retCode, 'Unable to setup test environment. Aborting.'

        errorDetected, rules = self._getRules()
        if len(rules) < 1:
            #self.dbAccess.closeConn()
            return 3, 'Failed to get any valid rules to run'

        if self.failOnError and errorDetected:
            return 3, 'Invalid rules detected' # invalid rule

        tableDict = {}
        # for each table pair

        try:
            retCode = 0
            for i in range(len(self.inTable)):
                inTable = self.inTable[i]
                outTable = self.outTable[i]

                self.dbAccess.openConn()
                if not self.getMetaData(inTable, outTable):

                    self.dbAccess.closeConn()
                    return 4, 'ERROR detected. Could not Access data.' # could not access the data

                if action == 'analyse':
                    if inTable not in tableDict:
                        tableDict[inTable] = {fld:0 for fld in self.inFields}
                    if outTable not in tableDict:
                        tableDict[outTable] = {fld:0 for fld in self.outFields}
                    self._analyseRules(rules, inTable, outTable, tableDict[inTable], tableDict[outTable])

                else:
                    retCode += self._runRules(rules, inTable, outTable)

                self.dbAccess.closeConn()
                if retCode > 0 and self.failOnError:

                    break
            if('-csv' in argv):
                self._writeToCSVFile()

            if retCode > 0:
                self.dbAccess.closeConn()
                return retCode, 'Failed rule(s) detected.' # failed rule or invalid rule
        except:
            raise 'here'
        finally:
            self.dbAccess.closeConn()

        if action == 'analyse':
            self._outputAnalysis(tableDict)

        print 'Finished'
        return 0, 'Done'


    #To generate output in CSV file
    def _writeToCSVFile(self):

        columnName = []
        csv = open(self.outputCSVFileLocation, "w")
            #fetch out field
        for rule in self.rule:
            grammar = Grammar.Grammar(rule, self.aliasDict, self.isVerbose )
            if grammar.isRule():

                if grammar.outFld[0] != []:
                    columnName.append(grammar.outFld[0])
                else:
                    columnName.append("none")
            else:
                    columnName.append("none")
        try:
            LEFT = 'Left'
            RIGHT = 'Right'
            result=' '
            with open(self.outputCSVFileLocation, "w") as csv:
                #if -v show verbose is given in args list
                if(self.isVerbose):
                    csv.write("Expected(In Table), Actual(Out Table), Field_Tested, Rule, Result,Left Status,Right Status, Left_Verbose, Right_Verbose \n")
                #if -v  is not given in args list
                else:
                    csv.write("Expected(In Table), Actual(Out Table), Field_Tested, Rule, Result \n")

                for tableIndex in range(0, len(self.inTable)):
                    for listIndex in range(0, len(self.rule)):
                        grammar = Grammar.Grammar(self.rule[listIndex], self.aliasDict, self.isVerbose )
                        if (not grammar.isRule()):
                            listIndex=listIndex+1
                        else:
                            if((self.leftStatus[listIndex]=='PASS') and self.rightStatus[listIndex]=='PASS'):
                                result='PASS'
                            elif((self.leftStatus[listIndex]=='FAIL') or self.rightStatus[listIndex]=='FAIL'):
                                result='FAIL'
                            elif((self.leftStatus[listIndex]=='PASS') and  self.rightStatus[listIndex]!= 'PASS'):
                                result='FAIL'
                            elif((self.rightStatus[listIndex]=='PASS') and  self.leftStatus[listIndex]!= 'PASS'):
                                result='FAIL'
                            elif((self.leftStatus[listIndex]==self.errMsg) and self.rightStatus[listIndex]==self.errMsg):
                                result='Not Executed'
                            elif((self.leftStatus[listIndex]==self.errInputMsg) and self.rightStatus[listIndex]==self.errInputMsg):
                                result='Not Executed'
                            elif((self.leftStatus[listIndex]==self.errOutputMsg) and self.rightStatus[listIndex]==self.errOutputMsg):
                                result='Not Executed'
                            elif ((self.leftStatus[listIndex]=='No Input Data') and self.rightStatus[listIndex]=='No Output Data'):
                                result='Not Executed'
                            elif ((self.leftStatus[listIndex]=='No Input Data') and self.rightStatus[listIndex]==self.errOutputMsg):
                                result='Not Executed'
                            elif ((self.leftStatus[listIndex]==self.errInputMsg) and self.rightStatus[listIndex]=='No Output Data'):
                                result='Not Executed'
                            row_data=self.inTable[tableIndex] + "; " + self.outTable[tableIndex] + "; " + columnName[listIndex] + "; " + self.rule[listIndex] + "; " +result
                            result=''
                            for val in row_data.split(";"):
                                if "," not in val:
                                    csv.write(val)
                                    csv.write(",")
                                else:
                                    new_val=val.replace("," ," and ")
                                    csv.write(new_val)
                                    csv.write(",")
                            if(self.isVerbose):
                                csv.write(self.leftStatus[listIndex])
                                csv.write(",")
                                csv.write(self.rightStatus[listIndex])
                                csv.write(",")
                                self.writeVerboseInCSV(listIndex,csv,LEFT,self.leftVerbose,self.leftStatus)
                                self.writeVerboseInCSV(listIndex,csv,RIGHT,self.rightVerbose,self.rightStatus)
                            #if -v is not given in argv
                            else:
                                csv.write("\n")
        except:
            msg = ("Unable to create file on disk.")
            print msg
            csv.close()
            return
        finally:
            csv.close()

    #to display left and right verbose in CSV File
    def writeVerboseInCSV(self,listIndex,csv,ruleSide,verbose,status):
        if(ruleSide=='Left'):
            counter=self.leftVerboseIndex
        else:
            counter= self.rightVerboseIndex
        newVerbose=[]
        strNew=' '
        if (status[listIndex] == "PASS" or status[listIndex] == "FAIL"):
            for index in range(counter,len(verbose)):
                if verbose[index]!= ";":
                    newVerbose.append(verbose[index])
                else:
                    strNew = ' : '.join(str(e) for e in newVerbose)
                    strNew = strNew.replace(","," ; ")
                    # Separate on ":"
                    value = strNew.split(":")
                    # Loop and print each value
                    counterOne=0
                    for val in value:
                        counterOne=counterOne+1
                        csv.write(val)
                        if(counterOne%2!=0) :
                            csv.write(":")
                        elif (counterOne <(len(value)-1)):
                            csv.write(";")
                    if(ruleSide=='Left'):
                        csv.write(",")
                    else:
                        csv.write("\n")
                    newVerbose=[]
                    for val in range(index,len(verbose)):
                        if(verbose[val]==";"):
                            counter=index+1
                            index=index+1
                            if(ruleSide=='Left'):
                                self.leftVerboseIndex=counter
                            else:
                                self.rightVerboseIndex=counter
                        else:
                            break
                    strNew=' '
                    break
        else:
            csv.write(status[listIndex])
            if(ruleSide=='Left'):
                csv.write(",")
            else:
                csv.write("\n")

def runSqlFromFile(dbPropertiesFile, testDataFile, blocksize = 48):
    print 'About to execute SQL statements from %s using database config file %s'%(testDataFile, dbPropertiesFile)
    f = None
    try :
        f = open (testDataFile, 'r')
        testDataQueries = f.read()

        _runSQL(dbPropertiesFile, testDataQueries, blocksize)
    except:
        raise
    finally:
        if f:
            f.close()

def _runSQL(dbPropertiesFile, query, blocksize = 48):

    dbAccess = DbAccess.DbAccess(dbPropertiesFile)
    dbAccess.openConn()
    statementCnt = query.count(';')
    maxBuff = blocksize*1024 # max out at 64k buffer
    if  len(query) > maxBuff:
        chunk = 0
        print 'SQL query is too long to execute in one go. Breaking into chunks of %d k.'%blocksize
        qlist = query.split(';')
        curRec = 0

        while curRec < statementCnt:
            buf = ''
            recInBuf = 0
            while len(buf) <= maxBuff and curRec < statementCnt and recInBuf < 32:
                buf += qlist[curRec] + ';'
                curRec += 1
                recInBuf += 1
            chunk += 1
            print 'Executing chunk %d with %d statements'%(chunk, recInBuf)
            dbAccess.executeSql(buf+'\n;commit;')
    else:
        dbAccess.executeSql(query+'\n;commit;')
    dbAccess.closeConn()
    dbAccess = None

def cleanupTestData(dbPropertiesFile, testDataFile):
    print 'About to drop tables created by SQL statements from %s using database config file %s'%(testDataFile, dbPropertiesFile)
    filesToDrop = ''
    text = [line.strip() for line in open(testDataFile)]
    for line in text:
        if line.startswith('create table '):
            tableName = line.split(' ')[2] # extract the third word
            filesToDrop += 'drop table if exists %s;\n'% tableName
    print 'about to execute:\n', filesToDrop
    _runSQL(dbPropertiesFile, filesToDrop)
    # Now clean up any old temp files
    dbAccess = DbAccess.DbAccess(dbPropertiesFile)
    dbAccess.openConn()

    results = dbAccess.runSQLs("select 'drop table '+ob.name+';' from sysobjects ob where ob.type='U' and (ob.name like 'lts__nl%' or ob.name like 'rts__nl%' ) order by ob.name")
    for sql in results:
        print sql[0]
        dbAccess.executeSql(sql[0])

    dbAccess.closeConn()

def usage():
        txt = '''
Welcome to Grit version %s
use the -a option to tell Grit what you want to do.

Grit can parse 10dash documents
        -a 10dash
        -t <name_of_10dash.xml_to_parse>
        -s <name_of_schema_to_produce>
        -f {CTRS|GPEH|SGEH|CTUM}  - required to work out fields offsets
        -q <file_with_sql_cmds> default = makeTables.sql
        -p <tableName> default = 'aTable'
        -v {True|False} default = True
		-outsql output location to extract sql files for excel/counter/topology files
        -eparse <path of file to parse>
        -parsetype <type of parser  for which parsing is required>
	eg Eniq Events schema parsing:
    java -jar Grit.jar -a 10dash -t CXC1735777_22_R5A.xml -s CTRS -f CTRS

    eg to parse different type of files:
    java -jar Grit.jar -a 10dash -outsql /eniq/home/dcuser/cpp_output -eparse /eniq/home/dcuser/cpp_input -parsetype <cppcounter/ecimcounter/excel/counter/topology>


Auto generate rule(EniqStats):
        -a autorule
        -r <mention the path where rule needs to be generated>

    eg to auto generate rule files:
    java -jar Grit.jar -a autorule -r /eniq/home/dcuser/cppRules/rules


It can execute a set of sql commands (to create or populate tables etc.)
        -a sql
        -f <name_of_file_of_SQL_statements>
        -d <name_of_db_config_file> default is ../etc/db.cfg]
    eg.
    java -jar Grit.jar -a sql -f makeTables.sql

It can parse raw data:
        -a raw
        -i <name_of_Raw_file>
        -s <name_of_schema>
        -o <file_with_sql_cmds> defaults to inFile+'.sql'
        -v {True|False} default = True
    eg.
    java -jar Grit.jar -a raw -s CTRS -i LTEtest2.bin

It can run rules with
        -a rules (or grit)
        -t <Table Configuration File>  [etc/table.cfg]
        -r <Rules File>                      [etc/rules.rules]
        -d <Database Properties File> [etc/db.cfg]
        -h <HostName of Server>]
        -v verbose
        -s show generated SQL
        -D <Date to test data for>] e.g. 2015-05-21
        -N do not use dates
        -f {True|False} fail on error default [False]
        -e report if no input data exists
        -csv to create output CSV file
    eg.
    java -jar Grit.jar -a rules -r CFA_ERR.rules -t CFA_ERR.cfg

	Rules execution for Eniq_Stats counter verification:
    java -jar Grit.jar -a rules -r /eniq/home/dcuser/rules/DC_E_ERBS_BBPROCESSINGRESOURCE_FLEX_RAW.rules -e -D 2017-09-22 -v

It can analyse rules to check which fields are covered and which are not with:
        -a analyse
        -t <Table Configuration File>  [etc/table.cfg]
        -r <Rules File>                [etc/rules.rules]
        -d <Database Properties File>  [etc/db.cfg]
    eg.
    java -jar Grit.jar -a anlayse -r CFA_ERR.rules -t CFA_ERR.cfg

And finally, Grit can clean up tables it has created with: [It will "replace create table X ... " with "drop table if exists X;"
        -a cleanup
        -f <name_of_file_of_SQL_statements>
        -d <Database Properties File> [etc/db.cfg]
    eg.
    java -jar Grit.jar -a cleanup -f makeTables.sql

        ''' %(Grit.version)
        print txt


def main(argv = None):
    dbPropertiesFile = 'etc/db.cfg'
    if not os.path.exists(dbPropertiesFile):
        dbPropertiesFile = '../etc/db.cfg'
    testDataFile = ''
    blocksize = 48 #
    # print 'Starting Grit with ',sys.argv

    action = 'help'
    if argv is None:
        argv = sys.argv

    for arg in argv:
        if arg.startswith("action="):
            action=arg.split('=')[1]
        if arg.startswith("file="):
            testDataFile=arg.split('=')[1]
        if arg.startswith("db="):
            dbPropertiesFile=arg.split('=')[1]
        if arg.startswith("help"):
            action='help'
    # -- or --
    numArgs = len(argv)
    i = 0
    while i < numArgs:
        arg = argv[i]
        if arg == '-a' and (i+1) < numArgs :
            i += 1
            action=argv[i]
        if arg == '-f' and (i+1) < numArgs :
            i += 1
            testDataFile=argv[i]
        if arg == '-b' and (i+1) < numArgs :
            i += 1
            try:
                blocksize = int(argv[i])
                if blocksize > 63 or blocksize < 0:
                    print "Out of Range blocksize specified, defaulting to 48"
                    blocksize = 48
            except ValueError:
                print "Invalid blocksize specified, defaulting to 48"
                blocksize = 48

        if arg == '-d' and (i+1) < numArgs :
            i += 1
            dbPropertiesFile=argv[i]
        if arg == '-h' or arg == '-?':
            action='help'
        i+=1

    if action=='help' :
        usage()
        sys.exit(5)

    if action=='sql':
        runSqlFromFile(dbPropertiesFile, testDataFile, blocksize)

    if action=='cleanup':
        cleanupTestData(dbPropertiesFile, testDataFile)

    if action=='10dash':
        import parse10dash
        parse10dash.main(argv)

    if action=='raw':
        import parseRaw
        parseRaw.main(argv)

    if action=='autorule':
        import autoRules
        autoRules.main(argv)

    if action=='grit' or action=='rules': # default action
        Grit(argv)

    if action=='analyse': # default action
        Grit(argv, action)

    print 'Done.'
