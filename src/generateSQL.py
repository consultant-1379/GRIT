'''
Methods and classes for generating the SQL required to implement the rules
'''
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

import os
import re
import dbUtility as DbUtility

dbUtility = DbUtility.DbUtility()
pid = str(os.getpid())
LEFT = 'l'
RIGHT = 'r'
LTRANSFORM = "Left Transform"
RTRANSFORM = "Right Transform"
# the pid is used to give unique names to the transformation tables.
# this allows multiple instances of GRIT to run on the same server.
leftTransformation = 'lts'
rightTransformation = 'rts'
nullTable = '__nl'
notNullTable = 'nonl'
LEFT_NULL_TRANSFORMATION_TABLE = leftTransformation + nullTable + pid
RIGHT_NULL_TRANSFORMATION_TABLE = rightTransformation + nullTable + pid
LEFT_NOT_NULL_TRANSFORMATION_TABLE = leftTransformation + notNullTable + pid
RIGHT_NOT_NULL_TRANSFORMATION_TABLE = rightTransformation + notNullTable + pid


INTABLE = "intable"
OUTTABLE = "outtable"
WHEN = "when"
OVERLAP = "overLap"
IN_PREFIX = r'in.'
OUT_PREFIX = r'out.'


class GenerateSQL:
    _aggregationList = ['sum', 'count', 'max', 'min', 'avg']

    def __init__(self, inTable, outTable, whereIn, whereOut):
        self.inTable = inTable
        self.outTable = outTable
        self.inWhereClause = whereIn
        self.outWhereClause = whereOut
        self.whenClauses = None
        self.isAgg = False
        self._whenCounter = 0

    def _replaceCharacters(self, txt):
        txt = txt.replace('.'+IN_PREFIX, self.inTable )
        txt = txt.replace('.'+OUT_PREFIX, self.outTable )
        txt = txt.replace(IN_PREFIX, self.inTable + '.')
        txt = txt.replace(OUT_PREFIX, self.outTable + '.')
        txt = txt.replace('|', '||')
        return txt

    def getSQL(self, grammar):
        ltransform, rtransform, leftLookup, rightLookup, whenClause, isAgg = grammar.getResults()

        '''
        return a list of SQL commands
        '''
        self.leftPrefix = None
        self.rightPrefix = None
        self.isAgg = isAgg

        if whenClause:
            self.whenClauses = whenClause
        else:
            self.whenClauses = None

        txt = ' '.join(ltransform) # ['in.a','+','in.c'] becomes 'in.a + in.c'

        if IN_PREFIX in txt or IN_PREFIX in leftLookup:
            self.leftTable = self.inTable
            self.rightTable = self.outTable
            self.leftPrefix = IN_PREFIX
            self.rightPrefix = OUT_PREFIX
            self.leftWhereClause = self.inWhereClause
            self.rightWhereClause = self.outWhereClause
        else:
            self.leftTable = self.outTable
            self.rightTable = self.inTable
            self.leftPrefix = OUT_PREFIX
            self.rightPrefix = IN_PREFIX
            self.leftWhereClause = self.outWhereClause
            self.rightWhereClause = self.inWhereClause

        self.leftTransformation = self._replaceCharacters(txt)
        txt = ' '.join(rtransform) # ['in.a','+','in.c'] becomes 'in.a + in.c'
        self.rightTransformation = self._replaceCharacters(txt)

        self.leftLookup = self._replaceCharacters(leftLookup)
        self.rightLookup = self._replaceCharacters(rightLookup)

        sql = []
        sql.append( self._getTransformationSql(LEFT, self.leftPrefix) )
        sql.append( self._getTransformationSql(RIGHT, self.rightPrefix) )
        sql.append( self._getComparisonSql(LEFT) )
        sql.append( self._getComparisonSql(RIGHT) )
        sql.append( self._showPassResults(LEFT))
        sql.append( self._showPassResults(RIGHT))
        sql.append( self._getSQLQuery(LEFT))
        sql.append( self._getSQLQuery(RIGHT))
        sql.append( self._cleanupTablesSQL())

        return sql

    def _cleanupTablesSQL(self):
        template = 'drop table if exists %s;'

        cleanupTablesSQL = template % LEFT_NULL_TRANSFORMATION_TABLE
        cleanupTablesSQL += template % LEFT_NOT_NULL_TRANSFORMATION_TABLE
        cleanupTablesSQL += template % RIGHT_NULL_TRANSFORMATION_TABLE
        cleanupTablesSQL += template % RIGHT_NOT_NULL_TRANSFORMATION_TABLE

        return cleanupTablesSQL

    # each will create a table that will store the transformations specified in the rule.
    # it creates one for the null transformations and non-null transformations.
    # null transformation are dealt with in a separate query because you cannot join tables on null values.
    # it counts the amount of unique instances of the transformation.
    # it will convert the transformation into a unique hash id for the comparisons.
    # these null values will be given a hash id for -1 (any number will do)
    # the lookups are left joins on the given table.
    def _getTransformationSql(self, comparisonSide, prefix):

        sqlTemplate = ('drop table if exists %s; select * into %s from ' +
                                       '(select %s as rowCount, %s as transform, %s as hashid%s from %s%s%s%s) as temp;')

        isNullCheck = True
        comparisonTableName = self._getComparisonTableName(comparisonSide, isNullCheck)
        transform = self._getTransformation(comparisonSide)
        rowCount = self._getRowCount(transform, isNullCheck)
        whenSelectKeys,var = self._getWhenSelectKeys(prefix, self.whenClauses)
        
        hashId = self._getHashID(transform,isNullCheck, var)
        sourceTable = self._getSourceTable(comparisonSide)
        lookup = self._getLookup(comparisonSide)
        whenLookups = self._getWhenLookups(prefix, self.whenClauses)
        lookup += whenLookups
        whereClause = self._getWhereClause(comparisonSide, prefix, self.whenClauses)
        whenKeys = self._getWhenGroupingKeys(prefix, self.whenClauses)
        groupBy = self._getGroupBy(transform, whenKeys)

        #populate template - null checks are done here
        sql = sqlTemplate % (comparisonTableName, comparisonTableName, rowCount, transform, hashId, whenSelectKeys, sourceTable, lookup, whereClause, groupBy)

        isNullCheck = False
        comparisonTableName = self._getComparisonTableName(comparisonSide, isNullCheck)
        rowCount = self._getRowCount(transform, isNullCheck)
        hashId = self._getHashID(transform,isNullCheck, var)

        #populate template - not null checks are done here
        sql += sqlTemplate % (comparisonTableName, comparisonTableName, rowCount, transform, hashId, whenSelectKeys, sourceTable, lookup, whereClause, groupBy)

        return sql

    # this is the sql that will compare the results of the transformations.
    # it compares the number of unique occurrences of the transformations.
    # it compares the null and non null transformations separately - see the union all
    # it also includes the when clauses where you have inputs compared to outputs
    # this will reduce what you are comparing
    # the main part of this is the where condition.
    # this takes the unique count of one side away from the other and show the user what the extra fields are.
    # if this is 0, then there is nothing to show.
    def _getComparisonSql(self, comparisonSide):
        isNullCheck = True
        leftTransformationTable = self._getComparisonTableName(LEFT, isNullCheck)
        rightTransformationTable = self._getComparisonTableName(RIGHT, isNullCheck)
        leftComparisonKeys = self._getComparisonKeys(LEFT)
        rightComparisonKeys = self._getComparisonKeys(RIGHT)
        whereClause = self._getComparisonWhereClause(comparisonSide, self.leftPrefix, self.rightPrefix, self.whenClauses, leftTransformationTable, rightTransformationTable)

        sql = ''

        template = ('select %s.rowCount - (case when %s.rowCount is null then 0 else %s.rowCount end) as "num_excess_records", %s.transform from ' +
                    '(select rowCount, transform%s, hashid from %s) as l ' +
                    '%s outer join (select rowCount, transform%s, hashid from %s) as r ' +
                    'on l.hashid = r.hashid ' +
                    'where %s.rowCount - (case when %s.rowCount is null then 0 else %s.rowCount end) > 0%s')

        if comparisonSide == LEFT:
            sql = template % (LEFT, RIGHT, RIGHT, LEFT, leftComparisonKeys, leftTransformationTable, 'left', rightComparisonKeys, rightTransformationTable, LEFT, RIGHT, RIGHT, whereClause)
        else:
            sql = template % (RIGHT, LEFT, LEFT, RIGHT, leftComparisonKeys, leftTransformationTable, 'right', rightComparisonKeys, rightTransformationTable, RIGHT, LEFT, LEFT, whereClause)


        sql += ' union all '

        isNullCheck = False
        leftTransformationTable = self._getComparisonTableName(LEFT, isNullCheck)
        rightTransformationTable = self._getComparisonTableName(RIGHT, isNullCheck)
        whereClause = self._getComparisonWhereClause(comparisonSide, self.leftPrefix, self.rightPrefix, self.whenClauses, leftTransformationTable, rightTransformationTable)

        if comparisonSide == LEFT:
            sql += template % (LEFT, RIGHT, RIGHT, LEFT, leftComparisonKeys, leftTransformationTable, 'left', rightComparisonKeys, rightTransformationTable, LEFT, RIGHT, RIGHT, whereClause)

        else:
            sql += template % (RIGHT, LEFT, LEFT, RIGHT, leftComparisonKeys, leftTransformationTable, 'right', rightComparisonKeys, rightTransformationTable, RIGHT, LEFT, LEFT, whereClause)


        sql += ';'

        return sql

    #returns sql query in case left table has no input field  but out table has output field or viseversa
    def _getSQLQuery(self,comparisonSide):
        isNullCheck = False
        transformationTable = self._getComparisonTableName(comparisonSide, isNullCheck)
        comparisonKeys = self._getComparisonKeys(comparisonSide)
        sql = ''
        if comparisonSide == LEFT:
            template = ('select %s.rowCount as "Expected Count", %s.transform from ' +
                    '(select rowCount, transform%s, hashid from %s) as l ')
            sql = template % (LEFT, LEFT, comparisonKeys, transformationTable)
        else:
            template = ('select %s.rowCount as "Expected Count", %s.transform from ' +
                    '(select rowCount, transform%s, hashid from %s) as r ')
            sql = template % (RIGHT, RIGHT, comparisonKeys, transformationTable)
        sql += ';'
        return sql

    # returns the transformation result for pass verbose
    def _showPassResults(self,comparisonSide):
        isNullCheck = False
        leftTransformationTable = self._getComparisonTableName(LEFT, isNullCheck)
        rightTransformationTable = self._getComparisonTableName(RIGHT, isNullCheck)
        leftComparisonKeys = self._getComparisonKeys(LEFT)
        rightComparisonKeys = self._getComparisonKeys(RIGHT)
        sql = ''
        template = ('select %s.rowCount as "Expected Count", %s.transform from ' +
                    '(select rowCount, transform%s, hashid from %s) as l ' +
                    '%s outer join (select rowCount, transform%s, hashid from %s) as r ' +
                    'on l.hashid = r.hashid ')

        if comparisonSide == LEFT:
            sql = template % (LEFT, LEFT, leftComparisonKeys, leftTransformationTable, 'left', rightComparisonKeys, rightTransformationTable)

        else:
            sql = template % (RIGHT, RIGHT, leftComparisonKeys, leftTransformationTable, 'right', rightComparisonKeys, rightTransformationTable)

        sql += ';'
        return sql


    # returns the name of the table used for the current comparison
    def _getComparisonTableName(self, comparisonSide, isNullCheck):
        comparisonTableName = None

        if comparisonSide == LEFT:
            if isNullCheck:
                comparisonTableName = LEFT_NULL_TRANSFORMATION_TABLE
            else:
                comparisonTableName = LEFT_NOT_NULL_TRANSFORMATION_TABLE
        elif comparisonSide == RIGHT:
            if isNullCheck:
                comparisonTableName = RIGHT_NULL_TRANSFORMATION_TABLE
            else:
                comparisonTableName = RIGHT_NOT_NULL_TRANSFORMATION_TABLE

        return comparisonTableName

    # get the names of the temp tables
    def getTableNames(self):
        return LEFT_NULL_TRANSFORMATION_TABLE, LEFT_NOT_NULL_TRANSFORMATION_TABLE, RIGHT_NULL_TRANSFORMATION_TABLE, RIGHT_NOT_NULL_TRANSFORMATION_TABLE

    # returns the transformation for the selected side of the rule
    def _getTransformation(self, comparisonSide):
        transform = None

        if comparisonSide == LEFT:
            transform = self.leftTransformation
        elif comparisonSide == RIGHT:
            transform = self.rightTransformation

        return transform

    # this will check for when clauses that have both an input and an output (on either side of the comparison)
    # it will then add the fieldnames that match the current prefix to the list of when keys
    # e.g.
    #    prefix = in
    #    when(in.field1 = out.field1) will produce a when key for in.field1
    #
    # If a when term includes in and out then append the prefix matching term to update the transform
    # in.x <=> out.y when(in.a = out.b, in.c=out.d,in.e=otherstuff, out.f=otherstuff)
    # Processing IN
    #   tu = '||in.a||in.c'
    # Processing  OUT
    #   tu = '||out.b||out.d'
    # This is appended to the transform value that gets hashed

    def _getWhenSelectKeys(self, prefix, whenClauses):
        selectKeys = ''
        transformUpdate = []

        leftTransPos = 0
        rightTransPos = 2
        leftLookupPos = 3
        rightLookupPos = 4

        if whenClauses is not None:
            for clause in whenClauses:
                tmpLTrans = ' '.join(clause[leftTransPos])
                tmpRTrans = ' '.join(clause[rightTransPos])
                tmpLLookup = clause[leftLookupPos]
                tmpRLookup = clause[rightLookupPos]

                if prefix == IN_PREFIX:
                    # a key is needed if there is an input and an output specified on each side
                    if (IN_PREFIX in tmpLTrans or IN_PREFIX in tmpLLookup) and (OUT_PREFIX in tmpRTrans or OUT_PREFIX in tmpRLookup):
                        clause = tmpLTrans
                        selectKeys += ', ' + clause + ' as when_' + str(self._whenCounter)
                        self._whenCounter += 1
                        #transformUpdate.append(clause)
                    elif (OUT_PREFIX in tmpLTrans or OUT_PREFIX in tmpLLookup) and (IN_PREFIX in tmpRTrans or IN_PREFIX in tmpRLookup):
                        clause = tmpRTrans
                        selectKeys += ', ' + clause + ' as when_' + str(self._whenCounter)
                        self._whenCounter += 1
                    if (IN_PREFIX in tmpLTrans and OUT_PREFIX in tmpRTrans) or (OUT_PREFIX in tmpLTrans and IN_PREFIX in tmpRTrans):
                        transformUpdate.append(clause)
                if prefix == OUT_PREFIX:
                    if (OUT_PREFIX in tmpLTrans or OUT_PREFIX in tmpLLookup) and (IN_PREFIX in tmpRTrans or IN_PREFIX in tmpRLookup):
                        clause = tmpLTrans
                        selectKeys += ', ' + clause + ' as when_' + str(self._whenCounter)
                        self._whenCounter += 1
                        transformUpdate.append(clause)
                    elif (IN_PREFIX in tmpLTrans or IN_PREFIX in tmpLLookup) and (OUT_PREFIX in tmpRTrans or OUT_PREFIX in tmpRLookup):
                        clause = tmpRTrans
                        selectKeys += ', ' + clause + ' as when_' + str(self._whenCounter)
                        self._whenCounter += 1
                        #transformUpdate.append(clause)
                    if (OUT_PREFIX in tmpLTrans and IN_PREFIX in tmpRTrans) or (IN_PREFIX in tmpLTrans and OUT_PREFIX in tmpRTrans):
                        transformUpdate.append(clause)


            selectKeys = self._replaceCharacters(selectKeys)

            # reset the counter as it will be used else where.
            self._whenCounter = 0

        var = ''
        if transformUpdate:
            var = '|'+'|'.join(transformUpdate)
            var = self._replaceCharacters(var)
        return selectKeys, var

    def _getWhenGroupingKeys(self, prefix, whenClauses):
        keys = ''
        leftTransPos = 0
        rightTransPos = 2
        leftLookupPos = 3
        rightLookupPos = 4

        if whenClauses is not None:
            for clause in whenClauses:
                tmpLTrans = ' '.join(clause[leftTransPos])
                tmpRTrans = ' '.join(clause[rightTransPos])
                tmpLLookup = clause[leftLookupPos]
                tmpRLookup = clause[rightLookupPos]

                if prefix == IN_PREFIX:
                    # a key is needed if there is an input and an output specified on each side
                    if (IN_PREFIX in tmpLTrans or IN_PREFIX in tmpLLookup) and (OUT_PREFIX in tmpRTrans or OUT_PREFIX in tmpRLookup):
                            clause = tmpLTrans
                            keys += ', ' + 'when_' + str(self._whenCounter)
                            self._whenCounter += 1

                    elif (OUT_PREFIX in tmpLTrans or OUT_PREFIX in tmpLLookup) and (IN_PREFIX in tmpRTrans or IN_PREFIX in tmpRLookup):
                            clause = tmpRTrans
                            keys += ', ' + 'when_' + str(self._whenCounter)
                            self._whenCounter += 1


                if prefix == OUT_PREFIX:
                    if (OUT_PREFIX in tmpLTrans or OUT_PREFIX in tmpLLookup) and (IN_PREFIX in tmpRTrans or IN_PREFIX in tmpRLookup):
                        clause = tmpLTrans
                        keys += ', ' + 'when_' + str(self._whenCounter)
                        self._whenCounter += 1

                    elif (IN_PREFIX in tmpLTrans or IN_PREFIX in tmpLLookup) and (OUT_PREFIX in tmpRTrans or OUT_PREFIX in tmpRLookup):
                            clause = tmpRTrans
                            keys += ', ' + 'when_' + str(self._whenCounter)
                            self._whenCounter += 1

            keys = self._replaceCharacters(keys)

            # reset the counter as it will be used else where.
            self._whenCounter = 0
        return keys


    def _getWhenLookups(self, prefix, whenClauses):
        leftLookupPos = 3
        rightLookupPos = 4
        lookup = ''

        if whenClauses is not None:
            for clause in whenClauses:
                tmpLLookup = clause[leftLookupPos]
                tmpRLookup = clause[rightLookupPos]

                if prefix == IN_PREFIX:
                    # a key is needed if there is an input and an output specified on each side
                    if IN_PREFIX in tmpLLookup:
                            lookup += tmpLLookup
                    elif IN_PREFIX in tmpRLookup:
                            lookup += tmpRLookup
                if prefix == OUT_PREFIX:
                    # a key is needed if there is an input and an output specified on each side
                    if OUT_PREFIX in tmpLLookup:
                            lookup += tmpLLookup
                    elif OUT_PREFIX in tmpRLookup:
                            lookup += tmpRLookup

        lookup = self._replaceCharacters(lookup)

        return lookup


    # the hashid's are used to create a unique value for the transformation.
    # there are two comparisons - transformations that are null, and transformations that are not.
    # if the transformation is null, it will create a hash id for -1 because you cannot create a hashid for null.
    def _getHashID(self, transform,isNullCheck, var = ''):
        
        alias=dbUtility.getAlias(transform)
        castStr=dbUtility.getDataTypeInCharConversion(isNullCheck,alias,var)
        if isNullCheck:
            hashId = '(case when %s is null then %s end )'%(alias,castStr)
        else:
            castInMD5=dbUtility.getMD5Conversion(castStr)
            hashId = '(case when ((%s)) is not null then %s end )'%(alias,castInMD5) 

        return hashId

    # gets the source table for the left or right hand side of the rule.
    # the input or the output can be on either side of the rule.
    # the getSQL() works out which tables are used on the left and right hand sides of the rules.
    def _getSourceTable(self, comparisonSide):
        sourceTable = None

        if comparisonSide == LEFT:
            sourceTable = self.leftTable
        elif comparisonSide == RIGHT:
            sourceTable = self.rightTable

        return sourceTable

    # gets the lookup for the left or the right hand side of the rule.
    # the input or the output can be on either side of the rule.
    # the getSQL() works out which tables are used on the left and right hand sides of the rules.
    def _getLookup(self, comparisonSide):

        lookup = None

        if comparisonSide == LEFT:
            lookup = self.leftLookup
        elif comparisonSide == RIGHT:
            lookup = self.rightLookup

        return lookup

    # this adds the where clause (that contains the date information) to the when clause information.
    def _getWhereClause(self, comparisonSide, prefix, whenClauses):

        whereClauseStart = ' where '
        AND = ' and'

        whereClause = ''

        if comparisonSide == LEFT:
            if self.leftWhereClause:
                whereClause = self.leftWhereClause
        else:
            if self.rightWhereClause:
                whereClause = self.rightWhereClause

        whenClause = self._getWhenClause(prefix, whenClauses)


        if whereClause:
            whereClause = whereClauseStart + whereClause
            if whenClause:
                whereClause += AND + whenClause
        else:
            if whenClause:
                whereClause = whereClauseStart + whenClause

        return whereClause

    # this gets the conditions from the when clause.
    # these will be added to the where clause in _getWhereClause()
    # this will get the when conditions that apply to the current prefix e.g. the in. prefix
    def _getWhenClause(self, prefix, whenClauses):
        AND = ' and'
        whenClause = ''
        leftTransPos = 0
        comparatorPos = 1
        rightTransPos = 2
        leftLookupPos = 3
        rightLookupPos = 4

        if whenClauses is not None:
            for clause in whenClauses:
                tmpLTrans = ' '.join(clause[leftTransPos])
                tmpComparator = clause[comparatorPos]
                tmpRTrans = ' '.join(clause[rightTransPos])
                tmpLLookup = clause[leftLookupPos]
                tmpRLookup = clause[rightLookupPos]

                if prefix == IN_PREFIX:
                    # a key is needed if there is an input and an output specified on each side

                    if (IN_PREFIX in tmpLTrans or IN_PREFIX in tmpLLookup) and not(OUT_PREFIX in tmpRTrans or OUT_PREFIX in tmpRLookup):
                        if tmpComparator == r'=' and tmpRTrans == 'null':
                            clause = tmpLTrans + ' is null'
                        elif tmpComparator == r'!=' and tmpRTrans == 'null':
                            clause = tmpLTrans + ' is not null'
                        else:
                            clause = tmpLTrans + ' ' + tmpComparator + ' ' + tmpRTrans

                        whenClause += ' ' + clause + AND

                elif prefix == OUT_PREFIX:
                    if (OUT_PREFIX in tmpLTrans or OUT_PREFIX in tmpLLookup) and not (IN_PREFIX in tmpRTrans or IN_PREFIX in tmpRLookup):
                        if tmpComparator == r'=' and tmpRTrans == 'null':
                            clause = tmpLTrans + ' is null'
                        elif tmpComparator == r'!=' and tmpRTrans == 'null':
                            clause = tmpLTrans + ' is not null'
                        else:
                            clause = tmpLTrans + ' ' + tmpComparator + ' ' + tmpRTrans

                        whenClause += ' ' + clause + AND

        if whenClause != '':
            whenClause = whenClause[:-len(AND)] # remove last 'and'
            whenClause = self._replaceCharacters(whenClause)

        return whenClause

    # gets the value for the row count
    # for non-aggregation rules this will count the number of unique instances.
    # for rules with aggregations defined, there should be only 1 unique instance of that attribute
    # this will also be 1 if the unique method has been applied to a non-aggregation column - used when comparing non-aggregation fields to aggregation fields
    def _getRowCount(self, transform, isNullCheck):

        nullCheck = 'is not null'
        if isNullCheck:
            nullCheck = 'is null'

        rowCountSyntax = 'count(*)' # counts the number of unique instances of a row

        for agg in self._aggregationList:
            if agg + '(' in transform:
                rowCountSyntax = '1' # for an aggregation there will always be one unique instance for each row
                
        alias=dbUtility.getAlias(transform)       
        rowCount = '(case when %s %s then %s end)' % (alias,nullCheck, rowCountSyntax)
      

        return rowCount

    #Returns list of indices where substring begins in string
    #find_substring('me', "The cat says meow, meow")
    #[13, 19]
    def find_substring(self,substring, string):

        indices = []
        index = -1  # Begin at -1 so index + 1 is 0
        while True:
            # Find next index of substring, by starting search from index + 1
            index = string.find(substring, index + 1)
            if index == -1:
                break  # All occurrences have been found
            indices.append(index)
        return indices

    # returns the group by for the comparison.
    # for non-aggregations it will group by the transformation and the number of instances.
    # if there are any when keys it will group by those.
    def _getGroupBy(self, transform, whenKeys):

        nonAggFields=''
        groupByKeyword = ' group by '
        groupBy = groupByKeyword + 'transform'
        for agg in self._aggregationList:
            if agg + '(' in transform:
                groupBy=''
                nonAggFields = self._handleAggrField(agg,transform)
                tokens=re.split('[,]|\*|\n|\+|\-|\/|\%|\|\(|\)',nonAggFields)
                nonAggFields=''
                for word in tokens:
                    if word !='' and self.inTable in word or 'lookup_' in word:
                        nonAggFields=nonAggFields+word.strip("()")
                        nonAggFields=nonAggFields+','
                if nonAggFields !='':
                    groupBy = groupByKeyword + nonAggFields.rstrip(',')
                else:
                    groupBy=''
        if whenKeys != '':
            if groupBy == '':
                groupBy = groupByKeyword + whenKeys.lstrip(',') # remove leading comma from keys
            else:
                groupBy += whenKeys

        return groupBy
    
    def _handleAggrField(self,agg,transform):
        nonAggFields = ''
        bracketStart = '('
        bracketEnd = ')'
        bracketStartCount = 0
        bracketEndCount = 0
        isAggInTransform=False
        isOpenBracketFound = False
        isCloseBracketFound = False
        chartset=''
        indices = self.find_substring(agg +'(',transform)
        for  index, char in enumerate(transform):
            if index in indices or isAggInTransform:
                isAggInTransform=True
                if char == bracketStart :
                    bracketStartCount = bracketStartCount + 1
                    isOpenBracketFound = True
                elif char == bracketEnd :
                    bracketEndCount = bracketEndCount + 1
                    isCloseBracketFound = True
                    isAggInTransform = False
                elif(isCloseBracketFound and bracketStartCount == bracketEndCount )  :
                    isOpenBracketFound = False
                    isCloseBracketFound = False
                    
                    
            else :
                nonAggFields=nonAggFields+char
       
        return nonAggFields
    # this adds the whenkeys to the comparison queries
    # they need to know what to select from the transformation tables.
    def _getComparisonKeys(self, comparisonSide):
        comparisonKeys = ''

        if self.whenClauses is not None:
            if comparisonSide == LEFT:
                keys = self._getWhenGroupingKeys(self.leftPrefix, self.whenClauses)
            elif comparisonSide == RIGHT:
                keys = self._getWhenGroupingKeys(self.rightPrefix, self.whenClauses)

            comparisonKeys = self._removeTableNames(keys)

        return comparisonKeys

    # adds the where clauses needed in the comparison queries
    # takes in the when clauses and extracts the needed when keys
    # when checking if the in and out columsn are the same,
    # this uses a subquery to find the distinct occurrences of the value in the other transformation table.
    # This is a left or right join so you also need to check if there is a value for that field as part of the join condition #may be redundant - see comment below
    # the second "and" condition makes sure you get all possible values returned.
    def _getComparisonWhereClause(self, comparisonSide, leftPrefix, rightPrefix, whenClauses, leftTransformationTable, rightTransformationTable):
        #whereClauseTemplate = ' and %s in (select distinct %s from %s) and (%s %s %s)'
        whereClauseTemplate = ' and %s in (select distinct %s from %s) and (%s %s %s)'
        # TODO change
        #
        #whereClauseTemplate = ' and %s in (select distinct %s from %s) and (%s %s %s)'
        # to
        # whereClauseTemplate = ' and (%s = %s)'

        #e.g.
        # and r.subcausecode in (select distinct subcausecode from leftTransformation_not_null_57024)
        # and (l.subcausecode = r.subcausecode)
        # or
        # and (l.subcausecode > r.subcausecode)

        #
        # the select query may be redundant - the change to checking the null values in a separate query may have made this redundant
        #
        #leftTransPos = 0
        comparatorPos = 1
        #rightTransPos = 2
        leftLookupPos = 3
        rightLookupPos = 4

        leftWhen = ''
        comparator = ''
        rightWhen = ''
        subQueryTable = ''
        subqueryField = ''
        whereClause = ''

        isLeftClause = False

        if comparisonSide == LEFT:
            isLeftClause = True

        # the sub query will be run checking data in the table from the other side of the comparison
        if isLeftClause:
            subQueryTable = leftTransformationTable
        else:
            subQueryTable = rightTransformationTable

        if whenClauses is not None:
            for clause in whenClauses:
                #tmpLTrans = ' '.join(clause[leftTransPos])
                tmpComparator = clause[comparatorPos]
                #tmpRTrans = ' '.join(clause[rightTransPos])
                tmpLLookup = clause[leftLookupPos]
                tmpRLookup = clause[rightLookupPos]

                if (leftPrefix in tmpLLookup) and (rightPrefix in tmpRLookup):
                        leftWhen = leftPrefix + 'when_' + str(self._whenCounter)
                        comparator = tmpComparator # need to make sure this is an =
                        rightWhen = rightPrefix + 'when_' + str(self._whenCounter)

                        self._whenCounter += 1
                elif (leftPrefix in tmpRLookup) and (rightPrefix in tmpLLookup):
                        leftWhen = leftPrefix + 'when_' + str(self._whenCounter)
                        comparator = tmpComparator # need to make sure this is an equals
                        rightWhen = rightPrefix + 'when_' + str(self._whenCounter)

                        self._whenCounter += 1
#                 if (leftPrefix in tmpLTrans or leftPrefix in tmpLLookup) and (rightPrefix in tmpRTrans or rightPrefix in tmpRLookup):
#                         leftWhen = leftPrefix + 'when_' + str(self._whenCounter)
#                         comparator = tmpComparator # need to make sure this is an =
#                         rightWhen = rightPrefix + 'when_' + str(self._whenCounter)
#
#                         self._whenCounter += 1
#                 elif (leftPrefix in tmpRTrans or leftPrefix in tmpRLookup) and (rightPrefix in tmpLTrans or rightPrefix in tmpLLookup):
#                         leftWhen = leftPrefix + 'when_' + str(self._whenCounter)
#                         comparator = tmpComparator # need to make sure this is an equals
#                         rightWhen = rightPrefix + 'when_' + str(self._whenCounter)
#
#                         self._whenCounter += 1
                else:
                    continue

                if isLeftClause:
                    subqueryField = rightWhen.replace(rightPrefix, '')
                else:
                    subqueryField = leftWhen.replace(leftPrefix, '')

                if isLeftClause:
                    whereClause += whereClauseTemplate % (leftWhen, subqueryField, subQueryTable, leftWhen, comparator, rightWhen)
                    #whereClause += whereClauseTemplate % (leftWhen, subqueryField, subQueryTable)
                else:
                    whereClause += whereClauseTemplate % (rightWhen, subqueryField, subQueryTable, leftWhen, comparator, rightWhen)
                    #whereClause += whereClauseTemplate % (rightWhen, subqueryField, subQueryTable)

        whereClause = whereClause.replace(leftPrefix, 'l.')
        whereClause = whereClause.replace(rightPrefix, 'r.')

        self._whenCounter = 0

        return whereClause

    # removes the table names from the keys
    def _removeTableNames(self, keys):
        keys = keys.replace(self.inTable + '.', '')
        keys = keys.replace(self.outTable + '.', '')

        return keys


