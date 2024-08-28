# Unit Tests for the grammer module
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
from grammar import Grammar
from parser import TokenType

class RulesGrammarTest(unittest.TestCase):
    def _getToken(self, code, name):
        token = TokenType()

        token.code = code
        token.name = name

        return token

    def test_isValid_True(self):

        '''
        Tests to add for the lookup improvements

        lookup(dim_e_test, rnc_name, in.field1, in.field2, in.field3) <=> out.nodeName
        lookup(dim_e_test, rnc_name, substring(in.field1, 1, 4) = lookup.mcc, in.field2, in.field3) <=> out.nodeName
        lookup(dim_e_test, rnc_name, substring(in.field1, 1, 4) = mcc, in.field2, in.field3) <=> out.nodeName
        lookup(dim_e_test, rnc_name, (substring(in.field1, 1, 4) | "test") = mcc, in.field2, in.field3) <=> out.nodeName
        lookup(dim_e_test, rnc_name, in.field1 - (in.field1 / 256)* 256 = mcc, in.field2, in.field3) <=> out.nodeName
        '''


        validRules = '''in.a <=>out.b
in.a+5<=>out.b
in.a+5<=>count(out.b)
count(in.field1) <=> out.aggTotal
in.a <=> out.a
in.a+5<=>out.b
in.a_2 <=> out.b
alias.mcc <- in.a
in.a + alias.mcc <=> out.b
default(in.a = null, 0) <=> out.b
default(in.a = null, 0, 1) <=> out.b
default(count(in.a) = null, 0) <=> out.total # comment
default(default(in.a8 > 1, 1) < 1, 0) <=> out.b
default(in.a1 = null, 0) <=> out.b
default(default(in.a8 > 1, 1) < 1, 0) <=> out.b
default(in.a = null, 0)<=>out.b # no. 22 here
default(default(in.a < 1, null) = null, 0)<=>out.b
default(lookup(DIM_RNC, nodeName, in.nodeId=lookup.nodeId) = null, "Unknown") <=> out.nodeName
default(in.a > 1, 1) <=> out.b
default(in.a = 0, "ACTIVE") <=> out.b
default(in.a > 1.0, 1.0) <=> out.b
default(in.a = null, 1) <=> out.b
default(in.a != null, 1) <=> out.b
default(default(in.a = null, 0) > 1, 1) <=> out.b
default(in.a != 5, substring(in.a, 1, 5)) <=> out.b
default((in.a + 7) = null, 0) <=> out.b
default(in.a != 5, lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id)) <=> out.b
default(in.a != 5, default(in.a = 5, in.b)) <=> out.b
in.a<=>default(out.b = null, 0)
in.a <=> default(out.b > 2, 2)
in.a+5<=>count(out.b)
unique(in.a) <=> out.b
sum(in.a) <=> out.b
summation(in.a) <=> out.b
min(in.a) <=> out.b
minimum(in.a) <=> out.b
max(in.a) <=> out.b
maximum(in.a) <=> out.b
avg(in.a) <=> out.b
average(in.a) <=> out.b
count(in.a) <=> out.b
count(in.a) <=> out.total
count(in.a) <=> out.total when(in.a = 1)
alias.w1 <- out.total
count(in.a) <=> alias.w1
substring(in.a, 2, 4) <=> out.a
substring(substring(in.d, 3, 4), 4, 5) <=> out.b
substring(substring(in.d, 3, 4), 4, 5) <=> out.b
alias.mcc <- substr(in.plmnid,1,1) | substr(in.plmnid,0,1) | substring(in.plmnid,2,1) # an assignment not a rule
in.x + alias.mcc <=> out.y
substring(in.a, 2, 4) <=> out.b
alias.mcc <- substring(in.plmnid,1,1) | substring(in.plmnid,0,1) | substring(in.plmnid,2,1) # an assignment not a rule
in.x + alias.mcc <=> out.y
substring(substring(in.a,3,4),4,5) <=> out.b
substring(in.a, 3, 4) <=> out.b
substring(in.a, 30000, 40000) <=> out.b
substring(in.a, -3, 4) <=> out.b
substring(lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id), 3, 4) <=> out.b
lookup(DIM_RNC, nodeName, in.nodeId) <=> out.nodeName
lookup(DIM_RNC, nodeName, in.nodeId = lookup.nodeId) <=> out.nodeName
lookup(DIM_RNC, nodeName, in.nodeId = lookup.nodeId, in.a = lookup.b) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id) <=> out.nodeName
lookup(dim_e_test, rnc_name, out.rnc_id = lookup.rnc_id) <=> in.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, in.col2 = lookup.col2) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, in.col2 = lookup.col2) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, "test" = lookup.col2) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, "test" = col2) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, 1 = col2) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id, 1.333 = col2) <=> out.nodeName
in.a <=> out.b when(lookup(dim_e_test1, rnc_name, in.a1 = lookup.a1) = out.b1, in.a2 = 3)
in.a <=> out.b when(in.a = null, null = out.b)
(in.a +5) * 6 <=> out.b + ((8*7)/9)/10
((in.a + in.b) + (5-8)) + 10 <=> out.b
alias.id<-in.rcn_id
lookup(dim_e_test, rnc_name, alias.id=lookup.id) <=> out.nodeName
lookup(dim_e_test, rnc_name, substring(in.a, 3, 4)=lookup.id) <=> out.nodeName
in.a <=> out.b when(in.a = out.b)
in.a <=> out.b when(in.a = out.b, in.a1=out.b1)
in.a <=> out.b when(in.a = out.b, alias.id=out.b1)
in.a <=> out.b when(in.a = out.b, alias.id=alias.mcc)
alias.num <-"abc"
default(in.a > 0, alias.num) <=> out.b
default(in.a > 0, 1, alias.num) <=> out.b
in.a <=> cast(out.b)
substr(cast(in.a),1,1) <=> out.b
pad("0", 5, in.a)  <=> out.b
lookup(dim_e_test, rnc_name, in.rnc_id = lookup.rnc_id) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = rnc_id) <=> out.nodeName
lookup(dim_e_test, rnc_name, in.rnc_id = pad("0",5,lookup.rnc_id)) <=> out.nodeName
padright("0", 5, in.a)  <=> out.b
lookup(dim_e_test, rnc_name, in.rnc_id = padright("0",5,lookup.rnc_id)) <=> out.nodeName
'''
        aliasDict = {}
        i = 1
        print 'Passing Rules:'
        for rule in validRules.splitlines():
            print '%3d: %s'%(i, rule)
            i += 1
            grammar = Grammar(rule, aliasDict)
            actual = grammar.isValid()

            self.assertTrue(actual, rule + ' is invalid')
            if grammar.isAlias():
                aliasDict = grammar.aliasDict


    def atest_isValid_false(self):
        validRules = ''' " kujwdhq
junk + in.a3 <+> out.b
#in.a <=> out.a
    #tab
in.abc + lookup(stuff) <=> out.b123 # not a keyword
in.a | substr("abc",1) <=> out.b # missing argument
substring(substring(in.a,3,4),4) <=> out.b
substring(substring(in.a,3,4),4) <=> null
(in.a % 5) *6 <=> out.a
(in.a -- 6) <=> out.b
(in.a + out.b) <=> out.b
(in.a + out.b +) <=> out.b
in.a + out.b <=> out.b
lookup(dim_e_test, rnc_name, in.field1 - (in.field1 / 256)* 256 - = mcc, in.field2, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, mcc, in.field2, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, default(in.field2 = null, 0)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, sum(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, min(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, max(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, mvg(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, count(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, unique(in.field2)= lookup.field1, in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, lookup.field1 = unique(in.field2), in.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, lookup.field1 = in.field2, out.field3 = lookup.field3) <=> out.nodeName
lookup(dim_e_test, rnc_name, 1.333 = lookup.rnc_id ) <=> out.nodeName
count(in.a,) <=> out.b
count(*) <=> out.b
sum(*) <=> out.b
sum(in.*) <=> out.b
substring(substring(in.a,3,4),default(in.abc = null, 0),5) <=> out.b
substring(substring(in.a,3,4),substring(in.b, 7, 8),5) <=> out.b
substring(in.a) <=> out.b
substring(in.a, 1) <=> out.b
substring(substring(in.a,3,4),5,substring(in.b, 7, 8)) <=> out.b
substring(in.a + in.a + in.a + in.a,) <=> out.b
substring(in.a, 3 5 7,) <=> out.b
substring(in.a, 3.9, 5) <=> out.b
default(in.a != in.b, 1) <=> out.b
default(in.a != substring(in.a, 4, 5), 1) <=> out.b
lookup(dim_e_test, rnc_name, outfield1) <=> in.nodeName

'''
        aliasDict = {}
        print 'Failing Rules:'
        for rule in validRules.splitlines():
            grammar = Grammar(rule, aliasDict)
            actual = grammar.isValid()
            self.assertFalse(actual, rule + ' should not be valid')
            if grammar.isAlias():
                aliasDict = grammar.aliasDict

    def test_isAgg1(self):
        rule = 'count(in.*) <=> out.total'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertFalse(isValid, "count.* should not be supported!")
        self.assertFalse(grammar._isAgg)

    def test_isAgg2(self):
        rule = 'count(in.a) <=> out.total'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")
        self.assertTrue(grammar._isAgg)

    def test_isAgg3(self):
        rule = 'in.a <=> count(out.b)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")
        self.assertTrue(grammar._isAgg)

    def test_isAgg4(self):
        rule = 'default(count(in.a) > 1, 1) <=> out.total'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")
        self.assertTrue(grammar._isAgg)

    def test_When1(self):
        rule = 'in.a <=> out.b when(in.a = 1)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")

    def test_When2(self):
        ''' check fields in when clause are valid
        '''
        rule = 'in.a <=> out.b when(in.a1 = out.b1)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")

        InFlds = ['a', 'a1'] # list of available fields in the input table - Must be all lower case!
        OutFlds = ['b',] # list of available fields in the input table

        isValid = grammar.testInFields(InFlds)
        self.assertTrue(isValid, rule+" should be valid!")
        isValid = grammar.testOutFields(OutFlds)
        self.assertFalse(isValid, rule+" should be invalid because b1 is not in outFlds!")

    def test_When3(self):
        ''' check fields in when clause are valid
        '''
        rule = 'in.a <=> out.b when(in.a1 = out.b1, in.a2 = 3)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid, rule+" should be valid!")

        InFlds = ['a', 'a1', 'a2'] # list of available fields in the input table - Must be all lower case!
        OutFlds = ['b',] # list of available fields in the input table

        isValid = grammar.testInFields(InFlds)
        self.assertTrue(isValid, rule+" should be valid!")
        isValid = grammar.testOutFields(OutFlds)
        self.assertFalse(isValid, rule+" should be invalid because b1 is not in outFlds!")


    def test_When_fail_1(self):
        rule = 'count(in.a) <=> out.total when(count(in.a) = 1, in.b = 5)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertFalse(isValid)

    def test_When_fail_2(self):
        rule = 'count(in.a) <=> out.total when(unique(in.a) = 1, in.b = 5)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertFalse(isValid)

    def test_When_fail_3(self):
        rule = 'count(in.a) <=> out.total when(substring(in.a) = 1, in.b = 5)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertFalse(isValid)

    def test_When_1(self):
        rule = 'in.a <=> out.b when(lookup(dim_e_test1, rnc_name, in.a1 = lookup.a1) = out.b1, in.a2 = 3)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expected = [
[['lookup_0.rnc_name'], '=', ['out.b1'], ' left join (select dim_e_test1.rnc_name,dim_e_test1.a1 from dim_e_test1 group by dim_e_test1.rnc_name,dim_e_test1.a1 ) as lookup_0 on cast(in.a1 as varchar)=cast(lookup_0.a1 as varchar) ', ''],
[['in.a2'], '=', ['3'], '', '']]

        actual = grammar.whenClause

        self.assertEquals(expected, actual)

    def test_When_2(self):
        rule = 'count(in.a) <=> out.total when(in.a = 1, in.b = 5)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expected = [[['in.a'], '=', ['1'], '', ''], [['in.b'], '=', ['5'], '', '']]

        actual = grammar.whenClause

        self.assertEquals(expected, actual)

    def test_When_3(self):
        rule = 'in.a <=> out.total when(in.a + 5 = 1, in.b = 5)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expected = [[['in.a', '+', '5'], '=', ['1'], '', ''], [['in.b'], '=', ['5'], '', '']]

        actual = grammar.whenClause

        self.assertEquals(expected, actual)

    def test_When_4(self):
        rule = 'in.a <=> out.total when(in.a + 5 = null, null = in.b)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expected = [[['in.a', '+', '5'], '=', ['null'], '', ''], [['null'], '=', ['in.b'], '', '']]

        actual = grammar.whenClause

        self.assertEquals(expected, actual)

    def test_When_5(self):
        rule = 'in.a <=> out.total when((substring(in.a,5,6) + 5) * 6  = null, null = in.b)'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expected = [[['(', 'substring(in.a,5,6)', '+', '5', ')', '*', '6'], '=', ['null'], '', ''], [['null'], '=', ['in.b'], '', '']]

        actual = grammar.whenClause

        self.assertEquals(expected, actual)

    def test_brackets_1(self):
        rule = '(in.a +5) * 6 <=> out.b + ((8*7)/9)/10'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expectedLeftTransform = ['(', 'in.a', '+', '5', ')', '*', '6']
        expectedRightTransform = ['out.b', '+', '(', '(', '8', '*', '7', ')', '/', '9', ')', '/', '10']

        actualLeftTransform = grammar.ltransform
        actualRightTransform = grammar.rtransform

        self.assertEquals(expectedLeftTransform, actualLeftTransform)
        self.assertEquals(expectedRightTransform, actualRightTransform)


    def test_brackets_2(self):
        rule = '(substring(in.a, 5, 6) +5) * 6 <=> out.b + ((8*7)/9)/10'
        aliasDict = {}
        grammar = Grammar(rule, aliasDict)
        isValid = grammar.isValid()

        self.assertTrue(isValid)
        expectedLeftTransform = ['(', 'substring(in.a,5,6)', '+', '5', ')', '*', '6']
        expectedRightTransform = ['out.b', '+', '(', '(', '8', '*', '7', ')', '/', '9', ')', '/', '10']

        actualLeftTransform = grammar.ltransform
        actualRightTransform = grammar.rtransform

        self.assertEquals(expectedLeftTransform, actualLeftTransform)
        self.assertEquals(expectedRightTransform, actualRightTransform)



if __name__ == "__main__":
    unittest.main()