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
import keywords as Keywords
from parser import TokenType
import parser as Parser

class KeywordTests(unittest.TestCase):
    import grammar as Grammar
    aliasDict = {}
    grammar = Grammar.Grammar('', aliasDict)
    keywords = Keywords.keywords()
    keywords.setGrammar(grammar)

    def _getToken(self, code, name):
        token = TokenType()

        token.code = code
        token.name = name

        return token

    def test_keyLookup_1(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText, actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_1a(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.cellid/256 = lookup.mnc_id')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.mnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.mnc_id ) as lookup_0 on cast(in.cellid/256 as varchar)=cast(lookup_0.mnc_id as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText, actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)


    def test_keyLookup_2(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = rnc_id')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText, actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_3(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, in.col2 = lookup.col2')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) and cast(in.col2 as varchar)=cast(lookup_0.col2 as varchar) '
        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText, actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_4(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, in.col2 = lookup.col2')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) and cast(in.col2 as varchar)=cast(lookup_0.col2 as varchar) '
        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_5(self):
        # tests if the lookup can take a string literal as a part of the condition
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, "test" = lookup.rnc_name')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = " left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) and cast('test' as varchar)=cast(lookup_0.rnc_name as varchar) "

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_6(self):
        # testing an integer literal
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, 1 = lookup.col2')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) and cast(1 as varchar)=cast(lookup_0.col2 as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyLookup_7(self):
        # testing an float literal
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, 1.333 = lookup.col2')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id,dim_e_test.col2 ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) and cast(1.333 as varchar)=cast(lookup_0.col2 as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)


    def test_keyLookup_9(self):
        # testing defaulting the name of the lookup field names with the in.fieldname
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.field1')

        expectedText = 'lookup_0.rnc_name'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.field1 from dim_e_test group by dim_e_test.rnc_name,dim_e_test.field1 ) as lookup_0 on cast(in.field1 as varchar) = cast(lookup_0.field1 as varchar) '
        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)


    def test_keyLookup_fail_1(self):
        # invalid operator
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.field1 - = mcc')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    # should this fail???
    # should we allow a field name and append "lookup." and "in."?
    # any possibility that "out" could be used for a lookup?
    def test_keyLookup_fail_2(self):
        # extra minus on the calculation
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, mcc, in.field2, in.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_ = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    # is there a reason we might need a default value when comparing to a lookup???
    def test_keyLookup_fail_3(self):
        # cannot use default in a lookup
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, default(in.field2 = null, 0)= lookup.field1, in.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    def test_keyLookup_fail_4(self):
        # aggregations are not allowed in a lookup
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, sum(in.field2)= lookup.field1, in.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    def test_keyLookup_fail_5(self):
        # aggregations are not allowed in a lookup
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, min(in.field2)= lookup.field1, in.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)


    def test_keyLookup_fail_6(self):
        # aggregations are not allowed in a lookup
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, lookup.field1 = unique(in.field2), in.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    def test_keyLookup_fail_7(self):
        # aggregations are not allowed in a lookup
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, lookup.field1 = in.field2, out.field3 = lookup.field3')

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        isValid, _,_  = keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(isValid)

    def test_keyUnique(self):
        ##rulePart = count(in.a)

        token1 = self._getToken(Parser.KEYWRD, 'unique')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'in.a'

        isValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keyCount(self):
        ##rulePart = count(in.a)

        token1 = self._getToken(Parser.KEYWRD, 'count')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'count(in.a)'

        isValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(isValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keyCount_invalid_comma(self):
        ##rulePart = count(in.a,)

        token1 = self._getToken(Parser.KEYWRD, 'count')
        token2 = self._getToken(Parser.BRKTS, 'in.a,')

        expectedText = 'Invalid format for count(). Expected count(in.fld) but found extra token >,<.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keySum(self):
        ##rulePart = sum(in.a)

        token1 = self._getToken(Parser.KEYWRD, 'sum')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'sum(in.a)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keySum_invalid_comma(self):
        ##rulePart = sum(in.a,)

        token1 = self._getToken(Parser.KEYWRD, 'sum')
        token2 = self._getToken(Parser.BRKTS, 'in.a,')

        expectedText = 'Invalid format for sum(). Expected sum(in.fld) but found extra token >,<.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keySum_invalid_star(self):
        ##rulePart = sum(in.*)

        token1 = self._getToken(Parser.KEYWRD, 'sum')
        token2 = self._getToken(Parser.BRKTS, 'in.*')

        expectedText = 'Invalid format for sum(). Expected sum(in.fld)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keyMax(self):
        ##rulePart = max(in.a)

        token1 = self._getToken(Parser.KEYWRD, 'max')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'max(in.a)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keyMax_invalid_comma(self):
        ##rulePart = max(in.a,)

        token1 = self._getToken(Parser.KEYWRD, 'max')
        token2 = self._getToken(Parser.BRKTS, 'in.a,')

        expectedText = 'Invalid format for max(). Expected max(in.fld) but found extra token >,<.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keyMin(self):
        ##rulePart = min(in.a)
        token1 = self._getToken(Parser.KEYWRD, 'min')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'min(in.a)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertTrue(self.keywords.getIsAgg())

    def test_keySubstring_fail_1(self):
        #rulePart = 'substring(substring(in.a, 3, 4), default(in.abc = null, 0), 5)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'substring(in.a,3,4),default(in.abc = null, 0),5')

        actualValid, _,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keySubstring_fail_2(self):
        #rulePart = 'substring(substring(in.a, 3, 4), substring(in.b, 7, 8), 5)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'substring(in.a,3,4),substring(in.b, 7, 8),5')


        actualValid, _,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keySubstring_fail_3(self):
        #rulePart = 'substring(in.a)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = 'Missing comma before substring offset.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keySubstring_fail_4(self):
        #rulePart = 'substring(in.a)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 1')

        expectedText = 'Missing comma before substring length.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keySubstring_fail_5(self):
        #rulePart = 'substring(in.a)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'substring(in.a,3,4),5,substring(in.b, 7, 8)')

        actualValid, _,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keySubstring_fail_6(self):
        #rulePart = 'substring(in.a + in.a + in.a + in.a,)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a + in.a + in.a + in.a,')

        expectedText = 'Missing comma before substring offset.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keySubstring_fail_7(self):
        #rulePart = 'substring(in.a, 3 5 7,)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 3 5  8 7')

        expectedText = 'Missing comma before substring length.'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keySubstring_fail_8(self):
        #rulePart = 'substring(in.a, 3 5 7,)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 3.9, 5')

        actualValid, _,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keySubstring_nestedSubstring(self):
        #rulePart = 'substring(substring(in.a, 3, 4), 4, 5)'

        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'substring(in.a,3,4),4,5')

        expectedText = 'substring(substring(in.a,3,4),4,5)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keySubstringCast_1(self):
        #rulePart = 'substring(in.a, 3, 4)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'cast(in.a), 3, 4')

        expectedText = 'substring(cast(in.a as varchar),3,4)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)


    def test_keySubstring_1(self):
        #rulePart = 'substring(in.a, 3, 4)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 3, 4')

        expectedText = 'substring(in.a,3,4)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)


    def test_keySubstring_2(self):
        #rulePart = 'substring(in.a, 30000, 40000)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 30000, 40000')

        expectedText = 'substring(in.a,30000,40000)'

        actualValid, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    # use a minus number to start from the end and work back
    def test_keySubstring_3(self):
        #rulePart = 'substring(in.a, -3, 4)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, -3, 4')

        expectedText = 'substring(in.a,-3,4)'

        _, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)

        #self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    # round
    def test_keyRound_1(self):
        #rulePart = 'round(in.a,2)'
        token1 = self._getToken(Parser.KEYWRD, 'round')
        token2 = self._getToken(Parser.BRKTS, 'in.a,2')
        expectedText = 'round(convert(double,(in.a)),2)'
        _, actualText,_ = self.keywords.keyMethods[token1.name](token1, token2)
        self.assertEqual(expectedText, actualText)

    # round with lookup
    def test_keyRound_withlookup(self):
        token1 = self._getToken(Parser.KEYWRD, 'round')
        token2 = self._getToken(Parser.BRKTS, 'lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id), 3, 4')

        expectedText = 'round(convert(double,(lookup_0.rnc_name)),3)'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        actualValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)


    def test_keySubstring_withLookup_1(self):
        #rulePart = 'substring(lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id), 3, 4)'
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id), 3, 4')

        expectedText = 'substring(lookup_0.rnc_name,3,4)'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_0 on cast(in.rnc_id as varchar)=cast(lookup_0.rnc_id as varchar) '

        keywords = Keywords.keywords()
        keywords.setGrammar(self.grammar)
        actualValid, actualText,actualLookup = keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyDefault(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > 1, 1')

        expectedText = '(case when in.a > 1 then 1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_minus_1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > -1, 1')

        expectedText = '(case when in.a > -1 then 1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_minus_2(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > 1, -1')

        expectedText = '(case when in.a > 1 then -1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_minus_3(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > -1, -1')

        expectedText = '(case when in.a > -1 then -1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_StringLiteral(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a = 0, "ACTIVE"')

        expectedText = '(case when in.a = 0 then \'ACTIVE\' else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_float(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > 1.0, 1.0')

        expectedText = '(case when in.a > 1.0 then 1.0 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_nullValue(self):
        #rulePart = 'default(in.a = null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a = null, 1')

        expectedText = '(case when in.a is null  then 1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_NotNullValue(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != null, 1')

        expectedText = '(case when in.a is not null  then 1 else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_withAnotherdefault(self):
        #rulePart = 'default(default(in.a = null, 0) > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'default(in.a = null, 0) > 1, 1')

        expectedText = '(case when (case when in.a is null  then 0 else in.a end) > 1 then 1 else (case when in.a is null  then 0 else in.a end) end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_fail_1(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != in.b, 1')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)


    def test_keyDefault_fail_2(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != substring(in.a, 4, 5), 1')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keyDefault_fail_3(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != in.b, ')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)


    def test_keyDefault_keywordAsResult_1(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != 5, substring(in.a, 1, 5)')

        expectedText = '(case when in.a != 5 then substring(in.a,1,5) else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_keywordAsResult_2(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != 5, lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id)')

        expectedText = '(case when in.a != 5 then lookup_1.rnc_name else in.a end)'
        expectedLookup = ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_1 on cast(in.rnc_id as varchar)=cast(lookup_1.rnc_id as varchar) '
                        #' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test, .in. where in.rnc_id                 =cast(dim_e_test.rnc_id as varchar) group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_1 on in.rnc_id                 =cast(lookup_1.rnc_id as varchar) '

        actualValid, actualText, actualLookup = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)
        self.assertEqual(expectedLookup, actualLookup)

    def test_keyDefault_keywordAsResult_3(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a != 5, default(in.a = 5, in.b)')

        expectedText = '(case when in.a != 5 then (case when in.a = 5 then in.b else in.a end) else in.a end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_Lookup_1(self):
        #rulePart = 'default(in.a != null, 1)'

        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id) = null, 1')

        expectedText = '(case when lookup_0.rnc_name is null  then 1 else lookup_0.rnc_name end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_else1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > 1, 1, 0')

        expectedText = '(case when in.a > 1 then 1 else 0 end)'

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyDefault_else2(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a > 1, "a", "b"')

        expectedText = "(case when in.a > 1 then 'a' else 'b' end)"

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyCast_1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'cast')
        token2 = self._getToken(Parser.BRKTS, 'in.a')

        expectedText = "cast(in.a as varchar)"

        actualValid, actualText, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedText, actualText)

    def test_keyCast_2(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'cast')
        token2 = self._getToken(Parser.BRKTS, '')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keyCast_3(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'cast')
        token2 = self._getToken(Parser.BRKTS, 'in.a, in.b')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertFalse(actualValid)

    def test_keyPad_1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'pad')
        token2 = self._getToken(Parser.BRKTS, '"0",5, in.b')

        actualValid, actualText, actualLookup = self.keywords.keyMethods[token1.name](token1, token2)
        self.assertTrue(actualValid)
        expectedLookup = '' # check lookup is not affected
        self.assertEqual(expectedLookup, actualLookup)
        expectedText = "right(replicate('0', 5) | in.b, 5)"

        self.assertEqual(expectedText, actualText)

    def test_keyPad_fail1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'pad')
        token2 = self._getToken(Parser.BRKTS, '0,5, in.b')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)
        self.assertFalse(actualValid)

    def test_keyPadInLookup_1(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        #token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id')
        # expectedLookup =  ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test, .in. where cast(in.rnc_id as varchar)=cast(dim_e_test.rnc_id as varchar) group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_2 on cast(in.rnc_id as varchar)=cast(lookup_2.rnc_id as varchar) '
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = pad("0", 4, lookup.rnc_id)')

        expectedLookup = " left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_2 on cast(in.rnc_id as varchar)=right(replicate('0', 4) | lookup_2.rnc_id, 4) "
        expectedText = 'lookup_2.rnc_name'

        actualValid, actualText, actualLookup = self.keywords.keyMethods[token1.name](token1, token2)

        self.assertTrue(actualValid)
        self.assertEqual(expectedLookup, actualLookup)
        self.assertEqual(expectedText, actualText)

    def test_keyPadR_1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'padright')
        token2 = self._getToken(Parser.BRKTS, '"0",5, in.b')

        actualValid, actualText, actualLookup = self.keywords.keyMethods[token1.name](token1, token2)
        self.assertTrue(actualValid)
        expectedLookup = ''
        self.assertEqual(expectedLookup, actualLookup)
        expectedText = "left(in.b | replicate('0', 5), 5)"

        self.assertEqual(expectedText, actualText)

    def test_keyPadR_fail1(self):
        #rulePart = 'default(in.a > 1, 1)'
        token1 = self._getToken(Parser.KEYWRD, 'padright')
        token2 = self._getToken(Parser.BRKTS, '0,5, in.b')

        actualValid, _, _ = self.keywords.keyMethods[token1.name](token1, token2)
        self.assertFalse(actualValid)

    def test_keyPadRInLookup_1(self):
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        #token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id')
        # expectedLookup =  ' left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test, .in. where cast(in.rnc_id as varchar)=cast(dim_e_test.rnc_id as varchar) group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_2 on cast(in.rnc_id as varchar)=cast(lookup_2.rnc_id as varchar) '
        token2 = self._getToken(Parser.BRKTS, 'dim_e_test, rnc_name, in.rnc_id = padright("0", 4, lookup.rnc_id)')

        expectedLookup = " left join (select dim_e_test.rnc_name,dim_e_test.rnc_id from dim_e_test group by dim_e_test.rnc_name,dim_e_test.rnc_id ) as lookup_3 on cast(in.rnc_id as varchar)=left(lookup_3.rnc_id | replicate('0', 4), 4) "

        actualValid, _, actualLookup = self.keywords.keyMethods[token1.name](token1, token2)
        #print actualValid, actualText, actualLookup

        self.assertTrue(actualValid)
        self.assertEqual(expectedLookup, actualLookup)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()