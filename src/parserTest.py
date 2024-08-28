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
#from parser import TokenType

import parser as Parser

class ParserTest(unittest.TestCase):

    def _getToken(self, code, name):
        token = Parser.TokenType()
        
        token.code = code
        token.name = name
        
        return token

    def compareLists(self, rule, expectedTokenList):
        parser = Parser.Parser()
        
        actualTokenList = parser.getTokens(rule)
        
        self.assertEqual(len(expectedTokenList), len(actualTokenList))
        
        for i in range(len(expectedTokenList)):
                self.assertEqual(expectedTokenList[i].code, actualTokenList[i].code)
                self.assertEqual(expectedTokenList[i].name, actualTokenList[i].name)
                               
    def test_getTokens_basicRule(self):
        rule = 'in.a <=> out.b'
        
        token1 = self._getToken(Parser.PREFIX, 'in.')
        token2 = self._getToken(Parser.FLDNM, 'a')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_underscoresInField(self):
        rule = 'in.event_id <=> out.event_id'
    
        token1 = self._getToken(Parser.PREFIX, 'in.')
        token2 = self._getToken(Parser.FLDNM, 'event_id')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'event_id')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_underscoresAndNumbersInField(self):
        rule = 'in.event_id_1 <=> out.event_id_1'
    
        token1 = self._getToken(Parser.PREFIX, 'in.')
        token2 = self._getToken(Parser.FLDNM, 'event_id_1')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'event_id_1')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
            
            
    def test_getTokens_substring(self):
        rule = 'substring(in.a, 5, 6) <=> out.b'
        
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 5, 6')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_pad(self):
        rule = 'pad("0", 5, in.a) <=> out.b'
        
        token1 = self._getToken(Parser.KEYWRD, 'pad')
        token2 = self._getToken(Parser.BRKTS, '"0", 5, in.a')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_padR(self):
        rule = 'padright("0", 5, in.a) <=> out.b'
        
        token1 = self._getToken(Parser.KEYWRD, 'padright')
        token2 = self._getToken(Parser.BRKTS, '"0", 5, in.a')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_default(self):
        rule = 'default(in.a = null, 0) <=> out.b'
        
        token1 = self._getToken(Parser.KEYWRD, 'default')
        token2 = self._getToken(Parser.BRKTS, 'in.a = null, 0')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_commentAfterRule(self):
        rule = 'in.a <=> out.b # this is rule with a comment '
        
        token1 = self._getToken(Parser.PREFIX, 'in.')
        token2 = self._getToken(Parser.FLDNM, 'a')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
        
    def test_getTokens_fail_MissingClosingBracket(self):
        rule = 'lookup(stuff) <=> default(extra open bracket()'
        
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'stuff')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.KEYWRD, 'default')
        token5 = self._getToken(Parser.INVALID, 'missing ")"')
        
        expectedTokenList = [token1, token2, token3, token4, token5]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_fail_UnexpectedCharacter(self):
        rule = 'lookup(stuff) <=> default(extra open bracket()))'
        
        token1 = self._getToken(Parser.KEYWRD, 'lookup')
        token2 = self._getToken(Parser.BRKTS, 'stuff')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.KEYWRD, 'default')
        token5 = self._getToken(Parser.BRKTS, 'extra open bracket()')
        token6 = self._getToken(Parser.INVALID, ' Unexpected character.')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
        
    def test_getTokens_fail_UnexpectedCharacter2(self):
        rule = 'substring(in.a, 5, 6) <=> out.b)'
        
        token1 = self._getToken(Parser.KEYWRD, 'substring')
        token2 = self._getToken(Parser.BRKTS, 'in.a, 5, 6')
        token3 = self._getToken(Parser.MDL, '<=>')
        token4 = self._getToken(Parser.PREFIX, 'out.')
        token5 = self._getToken(Parser.FLDNM, 'b')
        token6 = self._getToken(Parser.INVALID, ' Unexpected character.')
        
        expectedTokenList = [token1, token2, token3, token4, token5, token6]
        
        self.compareLists(rule, expectedTokenList)
    
    def test_getTokens_comment(self):
        rule = '# this is a comment'
        
        token1 = self._getToken(Parser.EMPTY, '')
        
        expectedTokenList = [token1]
        
        self.compareLists(rule, expectedTokenList)
        
    def test_getTokens_getOffset(self):
        # the offset is used to point out where the error is in the string
        rule = 'substring(in.a, 5, 6) <=> out.b)'
        expectd = len(rule)-1 # the offset should end at the last valid token which is the out.
        parser = Parser.Parser()
        
        parser.getTokens(rule)
        
        actual = parser.offset
        
        self.assertEquals(expectd, actual)
        
    def test_getTokens_getOffset_fail(self):
        # the offset is used to point out where the error is in the string
        rule = 'substring(in.a, 5, 6.0) <=> out.b)'
        expectd = len(rule)-1 # the offset should end at the last valid token which is the out.
        parser = Parser.Parser()
        
        parser.getTokens(rule)
        
        actual = parser.offset
        
        self.assertEquals(expectd, actual)
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()