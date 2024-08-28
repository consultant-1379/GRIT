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
import generateSQL as GenerateSQL
import grammar as Grammar
from parser import TokenType

class Test(unittest.TestCase):

    verbose = False
    inTable = 'aTable_1234'
    outTable = 'raw_table'
    whereIn = None
    whereOut = None

    def base(self, rule):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        genSQL = GenerateSQL.GenerateSQL(self.inTable, self.outTable, self.whereIn, self.whereOut)
        aliasDict = {}
        grammar = Grammar.Grammar(rule, aliasDict)
        self.assertTrue(grammar.isValid())
        genSQL.getSQL(grammar)
        return genSQL

    def doStuff(self, genSQL, rule):
        aliasDict = {}
        grammar = Grammar.Grammar(rule, aliasDict)
        self.assertTrue(grammar.isValid())
        sqlList = genSQL.getSQL(grammar)
        return sqlList

    def testName(self):
        pass

    def _getVariables(self, rule):
        aliasDict = {}
        grammar = Grammar.Grammar(rule, aliasDict)
        return grammar

    def _getGenSQLObject(self, rule, whereIn = None, whereOut = None):
        genSql = GenerateSQL.GenerateSQL(self.inTable, self.outTable, whereIn, whereOut)
        grammar = self._getVariables(rule)

        genSql.getSQL(grammar)
        return genSql

    def _getGenSQLObject2(self, grammar):
        genSql = GenerateSQL.GenerateSQL(self.inTable, self.outTable, self.whereIn, self.whereOut)

        genSql.getSQL(grammar)
        return genSql

    def _replaceCharacters(self, transformation, genSql):
        transformation = genSql._replaceCharacters(' '.join(transformation))

        return transformation

    def _getToken(self, code, name, transformation = '', extra = ''):
        token = TokenType()

        token.code = code
        token.name = name
        token.transformation = transformation
        token.extra = extra

        return token

    def test_rule1(self):
        # do it all
        genSQL = GenerateSQL.GenerateSQL(self.inTable, self.outTable, self.whereIn, self.whereOut)
        aliasDict = {}
        rule = 'in.a <=> out.b'
        grammar = Grammar.Grammar(rule, aliasDict)
        self.assertTrue(grammar.isValid())
        sqlList = genSQL.getSQL(grammar)
        if self.verbose:
            for txt in sqlList:
                print txt

    def test_rule2(self):
        # do it all changing defaults
        whereIn = 'in.a = 1'
        whereOut = None
        genSQL = GenerateSQL.GenerateSQL(self.inTable, self.outTable, whereIn, whereOut)

        aliasDict = {}
        rule = 'in.a <=> out.b'
        grammar = Grammar.Grammar(rule, aliasDict)
        self.assertTrue(grammar.isValid())
        sqlList = genSQL.getSQL(grammar)
        if self.verbose:
            for txt in sqlList:
                print txt

    def test_rule3(self):
        # change defaults, let system do rest
        whereIn = None
        whereOut = 'out.b = 3'
        genSQL = GenerateSQL.GenerateSQL(self.inTable, self.outTable, whereIn, whereOut)

        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        self.doStuff(genSQL, rule)

        actualLeft = genSQL._getWhenClause(GenerateSQL.IN_PREFIX, genSQL.whenClauses)
        actualRight = genSQL._getWhenClause(GenerateSQL.OUT_PREFIX, genSQL.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5', actualLeft)
        self.assertFalse(actualRight)

    def test_rule3a(self):
        # change defaults, let system do rest
        whereIn = 'in.a = 1'
        whereOut = 'out.b = 3'
        genSQL = GenerateSQL.GenerateSQL(self.inTable, self.outTable, whereIn, whereOut)

        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        self.doStuff(genSQL, rule)

        actualLeft = genSQL._getWhenClause(GenerateSQL.IN_PREFIX, genSQL.whenClauses)
        actualRight = genSQL._getWhenClause(GenerateSQL.OUT_PREFIX, genSQL.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5', actualLeft)
        self.assertFalse(actualRight)

    def test_rule4(self):
        # do stuff using defaults
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        genSQL = self.base(rule)

        actualLeft = genSQL._getWhenClause(GenerateSQL.IN_PREFIX, genSQL.whenClauses)
        actualRight = genSQL._getWhenClause(GenerateSQL.OUT_PREFIX, genSQL.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5', actualLeft)
        self.assertFalse(actualRight)


    def test_getComparisonTableName_leftTable_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = GenerateSQL.LEFT_NULL_TRANSFORMATION_TABLE
        isNullCheck = True
        actual = genSql._getComparisonTableName(GenerateSQL.LEFT, isNullCheck)
        self.assertEquals(expected, actual)

    def test_getComparisonTableName_leftTable_2(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = GenerateSQL.LEFT_NOT_NULL_TRANSFORMATION_TABLE
        isNullCheck = False
        actual = genSql._getComparisonTableName(GenerateSQL.LEFT, isNullCheck)
        self.assertEquals(expected, actual)


    def test_getComparisonTableName_rightTable_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = GenerateSQL.RIGHT_NULL_TRANSFORMATION_TABLE
        isNullCheck = True
        actual = genSql._getComparisonTableName(GenerateSQL.RIGHT, isNullCheck)
        self.assertEquals(expected, actual)

    def test_getComparisonTableName_rightTable_2(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = GenerateSQL.RIGHT_NOT_NULL_TRANSFORMATION_TABLE
        isNullCheck = False
        actual = genSql._getComparisonTableName(GenerateSQL.RIGHT, isNullCheck)
        self.assertEquals(expected, actual)

    def test_getComparisonTableName_Fail(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        isNullCheck = False
        actual = genSql._getComparisonTableName('Invalid', isNullCheck)
        self.assertFalse(actual)

    def test_getTransformation_left_1(self):
        rule = 'in.field1 <=> out.field2'
        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        expected = self._replaceCharacters(grammar.ltransform, genSql)
        actual = genSql._getTransformation(GenerateSQL.LEFT)
        self.assertEquals(expected, actual)

    def test_getTransformation_left_2(self):
        rule = 'out.field1 <=> in.field2'
        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        expected = self._replaceCharacters(grammar.ltransform, genSql)
        actual = genSql._getTransformation(GenerateSQL.LEFT)
        self.assertEquals(expected, actual)

    def test_getTransformation_right_1(self):
        rule = 'in.field1 <=> out.field2'
        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        expected = self._replaceCharacters(grammar.rtransform, genSql)
        actual = genSql._getTransformation(GenerateSQL.RIGHT)
        self.assertEquals(expected, actual)

    def test_getTransformation_right_2(self):
        rule = 'out.field1 <=> in.field2'
        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        expected = self._replaceCharacters(grammar.rtransform, genSql)
        actual = genSql._getTransformation(GenerateSQL.RIGHT)
        self.assertEquals(expected, actual)

    def test_getTransformation_fail(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        actual = genSql._getTransformation('Invalid')
        self.assertFalse(actual)


    def test_getHashID_1(self):
        rule = 'in.field1 <=> out.field2 '
        genSql = self._getGenSQLObject(rule)
        isNullCheck = False
        actualLeft = genSql._getHashID(isNullCheck)
        actualRight = genSql._getHashID(isNullCheck)
        self.assertEquals('(case when transform is not null then cast(HASH (convert(varchar, transform), \'md5\') as char(32)) end )', actualLeft)
        self.assertEquals('(case when transform is not null then cast(HASH (convert(varchar, transform), \'md5\') as char(32)) end )', actualRight)

    def test_getHashID_2(self):
        rule = 'in.field1 <=> out.field2 '
        genSql = self._getGenSQLObject(rule)
        isNullCheck = True
        actualLeft = genSql._getHashID(isNullCheck)
        actualRight = genSql._getHashID(isNullCheck)
        self.assertEquals('(case when transform is null then cast(-1 as char(32)) end )', actualLeft)
        self.assertEquals('(case when transform is null then cast(-1 as char(32)) end )', actualRight)


    def test_getSourceTable_left_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = genSql.inTable
        actual = genSql._getSourceTable(GenerateSQL.LEFT)
        self.assertEquals(expected, actual)

    def test_getSourceTable_left_2(self):
        rule = 'out.field1 <=> in.field2'
        genSql = self._getGenSQLObject(rule)
        expected = genSql.outTable
        actual = genSql._getSourceTable(GenerateSQL.LEFT)
        self.assertEquals(expected, actual)

    def test_getSourceTable_right_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        expected = genSql.outTable
        actual = genSql._getSourceTable(GenerateSQL.RIGHT)
        self.assertEquals(expected, actual)

    def test_getSourceTable_right_2(self):
        rule = 'out.field1 <=> in.field2'
        genSql = self._getGenSQLObject(rule)
        expected = genSql.inTable
        actual = genSql._getSourceTable(GenerateSQL.RIGHT)
        self.assertEquals(expected, actual)

    def test_getSourceTable_fail(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        actual = genSql._getSourceTable('Invalid')
        self.assertFalse(actual)

    def test_getLookup_1(self):
        rule = 'lookup(dim_e_test, field_x, in.field1 = lookup.field1) <=> out.field1'
        genSql = self._getGenSQLObject(rule)
        actualLookup = genSql._getLookup(GenerateSQL.LEFT)
        actualLeftTransformtion = genSql._getTransformation(GenerateSQL.LEFT)
        expectedLeft = ' left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_0 on cast(aTable_1234.field1 as varchar)=cast(lookup_0.field1 as varchar) '
        self.assertEquals(expectedLeft, actualLookup)
        self.assertEquals('lookup_0.field_x', actualLeftTransformtion)

    def test_getLookup_1a(self):
        rule = 'lookup(dim_e_test, field_x, in.field1/256 = lookup.field1) <=> out.field1'
        genSql = self._getGenSQLObject(rule)
        actualLookup = genSql._getLookup(GenerateSQL.LEFT)
        actualLeftTransformtion = genSql._getTransformation(GenerateSQL.LEFT)
        expectedLeft = ' left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_0 on cast(aTable_1234.field1/256 as varchar)=cast(lookup_0.field1 as varchar) '
        self.assertEquals(expectedLeft, actualLookup)
        self.assertEquals('lookup_0.field_x', actualLeftTransformtion)

    def test_getLookup_2(self):
        rule = 'out.field1 <=> lookup(dim_e_test, field_x, in.field1 = lookup.field1)'
        genSql = self._getGenSQLObject(rule)
        actualLookup = genSql._getLookup(GenerateSQL.RIGHT)
        actualLeftTransformtion = genSql._getTransformation(GenerateSQL.RIGHT)
        expected = ' left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_0 on cast(aTable_1234.field1 as varchar)=cast(lookup_0.field1 as varchar) '
        self.assertEquals(expected, actualLookup)
        self.assertEquals('lookup_0.field_x', actualLeftTransformtion)


    def test_getLookup_3(self):
        rule = 'in.field1 <=> lookup(dim_e_test, field_x, out.field1 = lookup.field1)'
        genSql = self._getGenSQLObject(rule)
        actualLookup = genSql._getLookup(GenerateSQL.RIGHT)
        actualLeftTransformtion = genSql._getTransformation(GenerateSQL.RIGHT)
        expected = ' left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_0 on cast(raw_table.field1 as varchar)=cast(lookup_0.field1 as varchar) '
        self.assertEquals(expected, actualLookup)
        self.assertEquals('lookup_0.field_x', actualLeftTransformtion)


    def test_getLookup_4(self):
        rule = 'in.field1 <=> lookup(dim_e_test, field_x, out.field1 = lookup.field1) + lookup(dim_e_test, field_x, out.field1 = lookup.field1)'
        genSql = self._getGenSQLObject(rule)
        actualLookup = genSql._getLookup(GenerateSQL.RIGHT)
        actualLeftTransformtion = genSql._getTransformation(GenerateSQL.RIGHT)
        expected = ' left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_0 on cast(raw_table.field1 as varchar)=cast(lookup_0.field1 as varchar)  left join (select dim_e_test.field_x,dim_e_test.field1 from dim_e_test group by dim_e_test.field_x,dim_e_test.field1 ) as lookup_1 on cast(raw_table.field1 as varchar)=cast(lookup_1.field1 as varchar) '
        self.assertEquals(expected , actualLookup)
        self.assertEquals('lookup_0.field_x + lookup_1.field_x', actualLeftTransformtion)


    def test_getWhenGroupingKeys_empty_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)


    def test_getWhenGroupingKeys_empty_2(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenGroupingKeys_empty_3(self):
        rule = 'in.field1 <=> out.field2 when(out.field2 = 5)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenGroupingKeys_empty_4(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field2 = 5)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenSelectKeys_1(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field2)'
        genSql = self._getGenSQLObject(rule)
        actualLeft,_ = genSql._getWhenSelectKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight,_ = genSql._getWhenSelectKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(', aTable_1234.field1 as when_0', actualLeft)
        self.assertEquals(', raw_table.field2 as when_0', actualRight)

    def test_getWhenSelectKeys_2(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field2, out.field3 = in.field4)'
        genSql = self._getGenSQLObject(rule)
        actualLeft,_ = genSql._getWhenSelectKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight,_ = genSql._getWhenSelectKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(', aTable_1234.field1 as when_0, aTable_1234.field4 as when_1', actualLeft)
        self.assertEquals(', raw_table.field2 as when_0, raw_table.field3 as when_1', actualRight)

    def test_getWhenSelectKeys_3(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field2, out.field3 = in.field4, in.field1 = 5, out.field2 = 5)'
        genSql = self._getGenSQLObject(rule)
        actualLeft,_ = genSql._getWhenSelectKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight,_ = genSql._getWhenSelectKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(', aTable_1234.field1 as when_0, aTable_1234.field4 as when_1', actualLeft)
        self.assertEquals(', raw_table.field2 as when_0, raw_table.field3 as when_1', actualRight)


    def test_getWhenClause_empty_1(self):
        rule = 'in.field1 <=> out.field2'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenClause_empty_2(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field2)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)


    def test_getWhenClause_empty_3(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field2, out.field3 = in.field4)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)


    def test_getWhenClause_1(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5', actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenClause_2(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field2 = 10)'

        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5', actualLeft)
        self.assertEquals(' raw_table.field2 = 10', actualRight)

    def test_getWhenClause_3(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, in.field4 = "Active", out.field2 = 10)'

        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5 and aTable_1234.field4 = \'Active\'', actualLeft)
        self.assertEquals(' raw_table.field2 = 10', actualRight)

    def test_getWhenClause_4(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = null)'

        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 is null', actualLeft)
        self.assertFalse(actualRight)

    def test_getWhenClause_5(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 != null)'

        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 is not null', actualLeft)
        self.assertFalse(actualRight)


    def test_getWhenClause_6(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, in.field4 = "Active", in.field5 = null, in.field6 != null, out.field1 = null, out.field2 != null)'

        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getWhenClause(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRight = genSql._getWhenClause(GenerateSQL.OUT_PREFIX, genSql.whenClauses)
        self.assertEquals(' aTable_1234.field1 = 5 and aTable_1234.field4 = \'Active\' and aTable_1234.field5 is null and aTable_1234.field6 is not null', actualLeft)
        self.assertEquals(' raw_table.field1 is null and raw_table.field2 is not null', actualRight)


    def test_getRowCount_1(self):
        rule = 'in.field1 <=> out.field2 '

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then count(*) end)', actualLeft)
        self.assertEquals('(case when transform is null then count(*) end)', actualRight)


    def test_getRowCount_2(self):
        rule = 'in.field1 <=> out.field2 '

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then count(*) end)', actualLeft)
        self.assertEquals('(case when transform is not null then count(*) end)', actualRight)

    def test_getRowCount_3(self):
        rule = 'in.field1 <=> count(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_4(self):
        rule = 'in.field1 <=> count(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)

    def test_getRowCount_5(self):
        rule = 'min(out.field1) <=> in.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_6(self):
        rule = 'min(out.field1) <=> in.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)


    def test_getRowCount_7(self):
        rule = 'sum(in.field1) <=> avg(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_8(self):
        rule = 'sum(in.field1) <=> avg(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)

    def test_getRowCount_9(self):
        rule = 'min(in.field1) <=> max(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_10(self):
        rule = 'min(in.field1) <=> max(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)

    def test_getRowCount_11(self):
        rule = 'default(min(in.field1) > 1, 5) <=> max(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_12(self):
        rule = 'default(min(in.field1) > 1, 5) <=> max(out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)

    def test_getRowCount_13(self):
        rule = 'default(min(in.field1) > 1, 5) <=> out.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = True
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is null then 1 end)', actualRight)

    def test_getRowCount_14(self):
        rule = 'default(min(in.field1) > 1, 5) <=> out.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)

        isNullCheck = False
        actualLeft = genSql._getRowCount(leftTransform, isNullCheck)
        actualRight = genSql._getRowCount(rightTransform, isNullCheck)
        self.assertEquals('(case when transform is not null then 1 end)', actualLeft)
        self.assertEquals('(case when transform is not null then 1 end)', actualRight)

    def test_getGroupBy_empty_1(self):
        rule = 'count(in.field1) <=> out.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertFalse(actualLeft)
        self.assertEquals(' group by transform', actualRight)

    def test_getGroupBy_empty_2(self):
        rule = 'out.field1 <=> min(in.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertFalse(actualRight)

    def test_getGroupBy_1(self):
        rule = 'in.field1 <=> out.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertEquals(' group by transform', actualRight)

    def test_getGroupBy_2(self):
        rule = 'out.field1 <=> in.field2'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertEquals(' group by transform', actualRight)


    def test_getGroupBy_3(self):
        rule = 'out.field1 <=> in.field2 when(in.field1 = 5)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertEquals(' group by transform', actualRight)

    def test_getGroupBy_4(self):
        rule = 'out.field1 <=> in.field2 when(out.field1 = 10)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertEquals(' group by transform', actualRight)

    def test_getGroupBy_5(self):
        rule = 'out.field1 <=> in.field2 when(in.field1 = out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform, when_0', actualLeft)
        self.assertEquals(' group by transform, when_0', actualRight)

    def test_getGroupBy_6(self):
        rule = 'count(out.field1) <=> in.field2 when(in.field1 = out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by  when_0', actualLeft)
        self.assertEquals(' group by transform, when_0', actualRight)

    def test_getGroupBy_7(self):
        rule = 'out.field1 <=> count(in.field2) when(in.field1 = out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform, when_0', actualLeft)
        self.assertEquals(' group by  when_0', actualRight)

    def test_getGroupBy_8(self):
        rule = 'count(out.field1) <=> count(in.field2) when(in.field1 = out.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by  when_0', actualLeft)
        self.assertEquals(' group by  when_0', actualRight)

    def test_getGroupBy_9(self):
        rule = 'out.field1 <=> in.field2 when(in.field1 = in.field2)'

        grammar =  self._getVariables(rule)
        genSql = self._getGenSQLObject2(grammar)
        leftTransform = self._replaceCharacters(grammar.ltransform, genSql)
        rightTransform = self._replaceCharacters(grammar.rtransform, genSql)
        leftWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        rightWhenKeys = genSql._getWhenGroupingKeys(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        actualLeft = genSql._getGroupBy(leftTransform, leftWhenKeys)
        actualRight = genSql._getGroupBy(rightTransform, rightWhenKeys)
        self.assertEquals(' group by transform', actualLeft)
        self.assertEquals(' group by transform', actualRight)

    def test_getComparisonKeys_empty_1(self):
        rule = 'out.field1 <=> in.field2'
        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getComparisonKeys(GenerateSQL.LEFT)
        actualRight = genSql._getComparisonKeys(GenerateSQL.RIGHT)

        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

        actualLeft = genSql._getTransformationSql(GenerateSQL.LEFT, GenerateSQL.IN_PREFIX)
        actualRight = genSql._getTransformationSql(GenerateSQL.RIGHT, GenerateSQL.OUT_PREFIX)



    def test_getComparisonKeys_empty_2(self):
        rule = 'out.field1 <=> in.field2 when(in.field1 = 5)'
        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getComparisonKeys(GenerateSQL.LEFT)
        actualRight = genSql._getComparisonKeys(GenerateSQL.RIGHT)

        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

        actualLeft = genSql._getTransformationSql(GenerateSQL.LEFT, GenerateSQL.IN_PREFIX)
        actualRight = genSql._getTransformationSql(GenerateSQL.RIGHT, GenerateSQL.OUT_PREFIX)


    def test_getComparisonKeys_empty_3(self):
        rule = 'out.field1 <=> in.field2 when(out.field1 = 5)'
        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getComparisonKeys(GenerateSQL.LEFT)
        actualRight = genSql._getComparisonKeys(GenerateSQL.RIGHT)

        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getComparisonKeys_1(self):
        rule = 'out.field1 <=> in.field2 when(out.field1 = in.field2)'
        genSql = self._getGenSQLObject(rule)
        actualLeft = genSql._getComparisonKeys(GenerateSQL.LEFT)
        actualRight = genSql._getComparisonKeys(GenerateSQL.RIGHT)

        self.assertEquals(', when_0', actualLeft)
        self.assertEquals(', when_0', actualRight)

        actualLeft = genSql._getTransformationSql(GenerateSQL.LEFT, GenerateSQL.IN_PREFIX)
        actualRight = genSql._getTransformationSql(GenerateSQL.RIGHT, GenerateSQL.OUT_PREFIX)


    def test_getComparisonKeys_2(self):
        rule = 'out.field1 <=> in.field2 when(out.field1 = in.field1, in.field2 = out.field2)'
        genSql = self._getGenSQLObject(rule)

        actualLeft = genSql._getComparisonKeys(GenerateSQL.LEFT)
        actualRight = genSql._getComparisonKeys(GenerateSQL.RIGHT)
        self.assertEquals(', when_0, when_1', actualLeft)
        self.assertEquals(', when_0, when_1', actualRight)
        tt = genSql._getTransformationSql(GenerateSQL.LEFT, GenerateSQL.IN_PREFIX)
        self.assertTrue('cast(HASH (convert(varchar, transform||aTable_1234.field1||aTable_1234.field2)' in tt, 'Incorrect Transform!')
        tt = genSql._getTransformationSql(GenerateSQL.RIGHT, GenerateSQL.OUT_PREFIX)


        self.assertTrue('cast(HASH (convert(varchar, transform||raw_table.field1||raw_table.field1||raw_table.field2)' in tt, tt)
        #self.assertEquals("drop table if exists lts__nl17357; select * into lts__nl17357 from (select (case when transform is null then count(*) end) as rowCount, raw_table.field1 as transform, (case when transform is null then cast(-1 as char(32)) end ) as hashid, aTable_1234.field1 as when_0, aTable_1234.field2 as when_1 from raw_table group by transform, when_0, when_1) as temp;drop table if exists ltsnonl17357; select * into ltsnonl17357 from (select (case when transform is not null then count(*) end) as rowCount, raw_table.field1 as transform, (case when transform is not null then cast(HASH (convert(varchar, transform||aTable_1234.field1||aTable_1234.field2), 'md5') as char(32)) end ) as hashid, aTable_1234.field1 as when_0, aTable_1234.field2 as when_1 from raw_table group by transform, when_0, when_1) as temp;" , tt)
    def test_whereClause_1(self):
        rule = 'out.field1 <=> in.field2'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where out.hour_id = 1'
        expectedRight = ' where in.hour_id = 1'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_whereClause_2(self):
        rule = 'in.field1 <=> out.field2'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where in.hour_id = 1'
        expectedRight = ' where out.hour_id = 1'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_whereClause_3(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where in.hour_id = 1 and ' + self.inTable + '.field1 = 5'
        expectedRight = ' where out.hour_id = 1'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_whereClause_4(self):
        rule = 'in.field1 <=> out.field2 when(out.field1 = 5)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where in.hour_id = 1'
        expectedRight = ' where out.hour_id = 1 and ' + self.outTable + '.field1 = 5'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)


    def test_whereClause_5(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field1 = 6)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where in.hour_id = 1 and ' + self.inTable + '.field1 = 5'
        expectedRight = ' where out.hour_id = 1 and ' + self.outTable + '.field1 = 6'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_whereClause_6(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field1 = 6, in.field1 = out.field1)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        expectedLeft = ' where in.hour_id = 1 and ' + self.inTable + '.field1 = 5'
        expectedRight = ' where out.hour_id = 1 and ' + self.outTable + '.field1 = 6'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)


    def test_whereClause_7(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field1 = 6, in.field1 = out.field1)'
        genSql = self._getGenSQLObject(rule)

        expectedLeft = ' where  ' + self.inTable + '.field1 = 5'
        expectedRight = ' where  ' + self.outTable + '.field1 = 6'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_whereClause_8(self):
        rule = 'in.field1 <=> out.field2 when(substring(in.field1, 5, 6) = 5, out.field1 = 6, in.field1 = out.field1)'
        genSql = self._getGenSQLObject(rule)

        expectedLeft = ' where  substring(' + self.inTable + '.field1,5,6) = 5'
        expectedRight = ' where  ' + self.outTable + '.field1 = 6'
        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)

    def test_getWhenLookups_1(self):
        rule = 'in.field1 <=> out.field2 when(lookup(dim_e_test, rnc_name, in.field1) = 5, out.field1 = 6, in.field1 = out.field1)'
        self.base(rule)
        genSql = self._getGenSQLObject(rule)
        expectedLeft = ' where  lookup_0.rnc_name = 5'
        expectedRight = ' where  ' + self.outTable + '.field1 = 6'
        expectedLeftLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.field1 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.field1 ) as lookup_0 on cast(aTable_1234.field1 as varchar) = cast(lookup_0.field1 as varchar) '
        expectedRightLookup = ''

        actualLeft = genSql._getWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.whenClauses)
        actualRight = genSql._getWhereClause(GenerateSQL.RIGHT, genSql.rightPrefix, genSql.whenClauses)
        actualLeftLookup = genSql._getWhenLookups(GenerateSQL.IN_PREFIX, genSql.whenClauses)
        actualRightLookup = genSql._getWhenLookups(GenerateSQL.OUT_PREFIX, genSql.whenClauses)

        self.assertEquals(expectedLeft, actualLeft)
        self.assertEquals(expectedRight, actualRight)
        self.assertEquals(expectedLeftLookup, actualLeftLookup)
        self.assertEquals(expectedRightLookup, actualRightLookup)

    def test_getComparisonWhereClause_1(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = 5, out.field1 = 6)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        actualLeft = genSql._getComparisonWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.rightPrefix, genSql.whenClauses, GenerateSQL.LEFT_NULL_TRANSFORMATION_TABLE, GenerateSQL.RIGHT_NULL_TRANSFORMATION_TABLE)
        actualRight = genSql._getComparisonWhereClause(GenerateSQL.RIGHT, genSql.leftPrefix, genSql.rightPrefix, genSql.whenClauses, GenerateSQL.LEFT_NULL_TRANSFORMATION_TABLE, GenerateSQL.RIGHT_NULL_TRANSFORMATION_TABLE)

        self.assertFalse(actualLeft)
        self.assertFalse(actualRight)

    def test_getComparisonWhereClause_2(self):
        rule = 'in.field1 <=> out.field2 when(in.field1 = out.field1)'
        whereIn = 'in.hour_id = 1'
        whereOut = 'out.hour_id = 1'
        genSql = self._getGenSQLObject(rule, whereIn, whereOut)

        actualLeft = genSql._getComparisonWhereClause(GenerateSQL.LEFT, genSql.leftPrefix, genSql.rightPrefix, genSql.whenClauses, GenerateSQL.LEFT_NULL_TRANSFORMATION_TABLE, GenerateSQL.RIGHT_NULL_TRANSFORMATION_TABLE)
        expectedLeft = ''
        self.assertEquals(expectedLeft, actualLeft)

        actualRight = genSql._getComparisonWhereClause(GenerateSQL.RIGHT, genSql.leftPrefix, genSql.rightPrefix, genSql.whenClauses, GenerateSQL.LEFT_NULL_TRANSFORMATION_TABLE, GenerateSQL.RIGHT_NULL_TRANSFORMATION_TABLE)
        expectedRight = ''

        self.assertEquals(expectedRight, actualRight)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    Test.verbose = False
    unittest.main()