from __future__ import with_statement
# Unit Tests for the grammer module
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

import dbAccess as DbAccess
import dbUtility as DbUtility

dbUtility = DbUtility.DbUtility()
class Overlap(object):
    '''
    Work out date ranges and overlaps
    '''
    def __init__(self, dbAccess, inOptions, outOptions,ruleVal):
        '''
        Constructor
        '''
        self.dbAccess = dbAccess
        self.optionsIn = inOptions
        self.optionsOut = outOptions
        self.rangeIn = self._getRange(inOptions,ruleVal)
        self.rangeOut= self._getRange(outOptions,ruleVal)


    def _getRange(self, optL,ruleVal):
        '''
        Get the date range in the table using the specified fields
        optL[0] = tablename, optL[1] = date field, optL[2] = hour field, optL[3] = minute field
        return list with start date, hour and minute and end date, hour and minute
         date field is string, hour and minute are ints
        '''
        # TODO 1) no data 2) bad fields
        #
        
        dateStr = dbUtility.getDateFormatConversion()
        table = optL[0]
        dt = optL[1]
        hr = optL[2]
        mn = optL[3]

        minDt = -1
        maxDt = -1
        minDy = ''
        maxDy = ''
        whereC = ''
        andC = ''
        if dt: # has a date field been specified?
            whereC = 'where '
            andC = ' and '
            sql = 'select %s(min(%s),\'yyyy-mm-dd\'), %s(max(%s),\'yyyy-mm-dd\') from %s'%(dateStr,dt,dateStr,dt,table)
            res = self.dbAccess.runSQL(sql)
            minDt = str(res[0])
            maxDt = str(res[1])

            minDy = ' %s = \'%s\''%(dt, minDt)
            maxDy = ' %s = \'%s\''%(dt, maxDt)

        sql = 'select min(%s) from %s %s %s '%(hr, table, whereC, minDy)
        res = self.dbAccess.runSQL(sql)
        minHr = res[0]

        sql = 'select max(%s) from %s %s %s '%(hr, table, whereC, maxDy)
        res = self.dbAccess.runSQL(sql)
        maxHr = res[0]

        if minHr == None or maxHr == None:
            print 'Found Null records! Could not establish minimum or maximum Hour!'
            minHr = 0
            maxHr = 24

        sql = 'select min(%s) from %s where %s = %s %s %s'%(mn, table, hr, minHr, andC, minDy)
        res = self.dbAccess.runSQL(sql)
        minMn = res[0]

        sql = 'select max(%s) from %s where %s = %s %s %s '%(mn, table, hr, maxHr, andC, maxDy)
        res = self.dbAccess.runSQL(sql)
        maxMn = res[0]
        if maxMn==0 and ruleVal=="kpi":
            maxMn = 59
            
        res = [ minDt, minHr, minMn, maxDt, maxHr, maxMn]
        return res

    def _setRngForTests(self, res1, res2):
        self.rangeIn = res1
        self.rangeOut = res2
        

    def getOverlap(self, date=None, printRange = True):
        # if right start > left start use right start else left start
        # Ranges are 0- min date, 1 - min houyr, 2- min Minute, 3- max date, 4- max hour, 5 - max minute
        if not date and self.rangeIn[0] == -1:
            return False, 'no date specified and no input data field specified', ''
        if self.rangeIn[0] == -1:
            self.rangeIn[0] = date
            self.rangeIn[3] = date

        if date:
            if self.rangeIn[0] > date or self.rangeIn[3] < date:
                return False, 'no left data for specified date', ''
            if self.rangeOut[0] > date or self.rangeOut[3] < date:
                return False, 'no right data for specified date', ''

        res = [-1]*6
        startIsOut = False # is the highest start date in the Out table

        if self.rangeIn[0]:
            if (self.rangeOut[0] > self.rangeIn[0]
                    or (self.rangeOut[0] == self.rangeIn[0] and self.rangeOut[1] > self.rangeIn[1])
                    or (self.rangeOut[0] == self.rangeIn[0] and self.rangeOut[1] == self.rangeIn[1] and self.rangeOut[2] > self.rangeIn[2])):
                startIsOut = True

            # if right end < left end use right end else left end
            endIsOut = False # is the lowest end date in the out table
            if (self.rangeOut[3] < self.rangeIn[3]
                    or (self.rangeOut[3] == self.rangeIn[3] and self.rangeOut[4] < self.rangeIn[4])
                    or (self.rangeOut[3] == self.rangeIn[3] and self.rangeOut[4] == self.rangeIn[4] and self.rangeOut[5] < self.rangeIn[5])):
                endIsOut = True

        if startIsOut:
            res[0:3] = self.rangeOut[0:3]
        else:
            res[0:3] = self.rangeIn[0:3]
        if endIsOut:
            res[3:6] = self.rangeOut[3:6]
        else:
            res[3:6] = self.rangeIn[3:6]

        # check that start < end
        if (res[0] > res[3]
                or (res[0] == res[3] and res[1] > res[4])
                or (res[0] == res[3] and res[1] == res[4] and res[2] > res[5])):
            return False, 'No overlap found!', ''

        if res[0] < res[3] and not date:
            return False, 'Date range exceeds one day and no date specified', ''

        if date:
            if res[0] < date:
                res[1] = 0
                res[2] = 0
            res[0] = date
            if res[3] > date:
                res[4] = 23
                res[5] = 59
            res[3] = date

        if printRange:
            output = ('%s table (%s) has data from %s %02d:%02d to %s %02d:%02d. ')
            print output % ('In', self.optionsIn[0], self.rangeIn[0], self.rangeIn[1], self.rangeIn[2], self.rangeIn[3], self.rangeIn[4], self.rangeIn[5])
            print output % ('Out', self.optionsOut[0],self.rangeOut[0],self.rangeOut[1],self.rangeOut[2],self.rangeOut[3],self.rangeOut[4],self.rangeOut[5])
            if date:
                print 'Specified date is %s '%date
            print 'Selected date overlap is from %s %02d:%02d to %s %02d:%02d' %(res[0], res[1], res[2], res[3], res[4],res[5])
        inSql = self._getComparisonWhereClause(self.optionsIn, res)
        outSql = self._getComparisonWhereClause(self.optionsOut, res)

        return True, inSql, outSql

    def _getComparisonWhereClause(self, optL, res):
        '''
        base qry is where
             dt = x AND -- only needed if dt is specified
                    ( (hr = minHr and minute >= minMinute) or -- only needed if minMinute > 0
                      (hr > minHr and hr < maxHr) or -- only needed if maxHr > minHr + 1
                      (hr = maxHr and minute <= maxMinute) ) -- only needed if maxMinute < 0

        '''
        dt = ''
        if optL[1]:
            dt = optL[0]+'.'+optL[1]
        hr = optL[0]+'.'+optL[2]
        mn = optL[0]+'.'+optL[3]
        whereC = ''
        if dt: # if date is specified then honour it
            whereC = '%s = \'%s\' AND '%(dt, res[0])

        if res[1] == res[4]: # min and max hour are the same
            whereC += '( %s = %s )' %( hr, res[1])
            if res[2] > 0 or res[5] < 60: # do minutes matter
                whereC += 'and( %s >= %s AND %s <= %s )'%(mn, res[2], mn, res[5])
        elif res[1] < res[4] and res[2] > 0 or res[5] < 60 : # max hour > min hour +1 and minutes matter
            whereC += '( ( %s = %s AND %s >= %s ) '%(hr, res[1], mn, res[2])
            if res[1] +1 < res[4]:
                whereC += 'or( %s > %s AND %s < %s )  '%(hr, res[1], hr, res[4])
            whereC += 'or( %s = %s AND %s <= %s ))'%(hr, res[4], mn, res[5])
        else: #  minutes dont matter
            whereC += '( %s >= %s AND %s <= %s ) '%(hr, res[1], hr, res[4])

        return whereC

if __name__ == '__main__':
    dbPropertiesFile = 'etc/db.cfg'
    dbAccess = DbAccess.DbAccess(dbPropertiesFile)
    dbAccess.openConn()
    print dbAccess.getSQLResults('select @@Version')

    sampleData = '../testresources/simpleTestTables.sql'
    with open (sampleData, 'r') as data:
        testDataQueries = data.read()
    dbAccess.executeSql(testDataQueries)

    inf = ['tableDHM1', '','hourfld','minfld']
    out2 = ['tableDHM2', 'datefld','hourfld','minfld']
    print Overlap(dbAccess.runSQL, inf, out2).getOverlap()
    print

    inf = ['tableDHM1', '','hourfld','minfld']
    out2 = ['tableDHM2', 'datefld','hourfld','minfld']
    print '2'
    print Overlap(dbAccess.runSQL, inf, out2).getOverlap('2015-04-22')
    print


    overlap = Overlap(dbAccess.runSQL, inf, out2)
    res1 = ['2015-04-21',3,2,'2015-04-23',3,6]
    res2 = ['2015-04-21',3,4,'2015-04-22',6,7]
    overlap._setRngForTests(res1, res2)
    # overlap exceeds one day, date must be specified
    res = overlap.getOverlap()

    print res
    print


    inf = ['tableDHM1', 'datefld','hourfld','minfld']
    out2 = ['tableDHM2', 'datefld','hourfld','minfld']
    print Overlap(dbAccess.runSQL, inf, out2).getOverlap('2015-04-22')
    print

    overlap = Overlap(dbAccess.runSQL, inf, out2)
    res1 = ['2015-04-21',3,2,'2015-04-23',3,6]
    res2 = ['2015-04-21',3,4,'2015-04-22',6,7]
    overlap._setRngForTests(res1, res2)
    # overlap exceeds one day, date must be specified
    res = overlap.getOverlap()
    print res
    print

    # date range exceeds one day, so no hour or minute required
    res1 = ['2015-04-21',3,2,'2015-04-23',3,6]
    res2 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap('2015-04-22')
    print '2', res
    print

    # date range on first date, hour required
    res1 = ['2015-04-21',3,2,'2015-04-23',3,6]
    res2 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap('2015-04-21', True)
    print res
    print

    # date range on first date, hour required
    res1 = ['2015-04-21',3,2,'2015-04-21',3,6]
    res2 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap('2015-04-21', True)
    print res
    print

    # date range on first date, hour required
    res1 = ['2015-04-21',3,2,'2015-04-21',4,6]
    res2 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap('2015-04-21', True)
    print res
    print

    # date range on first date, hour required
    res1 = ['2015-04-21',3,2,'2015-04-21',5,6]
    res2 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap('2015-04-21', True)
    print res
    print

    # the whole day
    res2 = ['2015-04-21',3,2,'2015-04-23',3,6]
    res1 = ['2015-04-21',3,4,'2015-04-25',6,7]
    overlap._setRngForTests(res1, res2)
    res = overlap.getOverlap( '2015-04-22', True)
    print res
    print

    dbAccess.closeConn()

