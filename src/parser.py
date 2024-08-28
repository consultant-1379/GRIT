#!/usr/bin/python
#------------------------------------------------------------------------------
# *******************************************************************************
# * COPYRIGHT Ericsson 2018
# *
# * The copyright to the computer program(s) herein is the property of
# * Ericsson Inc. The programs may be used and/or copied only with written
# * permission from Ericsson Inc. or in accordance with the terms and
# * conditions stipulated in the agreement/contract under which the
# * program(s) have been supplied.
# *******************************************************************************

import sys
import keywords as Keywords
'''
Functions and classes required to parse rules
'''

#literal = [\"].*[\"]|[0-9]+' # quoted string or sequence of digits
#fieldName = {[A-Za-z]+[A-Za-z_0-9]*}' # an alpha followed by zero or more alpha's, underscores or digits - follows a prefix
#prefix = {in.|out.|alias.}
#operator = {+|-|/|*||} - includes the pipe | to join text e.g. substring(*) | "hello"
#comparator = {=|!=|>|<|>=|<=}
#keyword = '{default|lookup|substring|min|max|avg|count|sum}'
#method = '{keyword(*)}'
#starter = '{[literal|{prefix}{fieldName}|method|alias]}
#middle = '[<=>|<-]'
#when = {prefix}{fieldName} {operator} { {prefix}{fieldName} | literal } [, {prefix}{fieldName} {operator} { {prefix}{fieldName} | literal }]*
#sentence='{starter}[{operator}{starter}]*{middle}{starter}[{operator}{starter}]* [when]

INVALID= 0#    invalid
NUMLIT = 1#    sequence of digits
STRLIT = 2#    quoted string
FLOAT  = 3#    floating point number
ALIAS  = 4#    can be any token or sequence of tokens
PREFIX = 5#    prefix 
FLDNM  = 6#    field name - 
MDL    = 7#    middle (<=> or <-)
OP     = 8#    operator
KEYWRD = 9#    known keyword
BRKTS  = 10#    bits in brackets
EMPTY  = 11#    nothing to process
COMMA  = 12#   comma separator 
COMPARE= 13#   comparator 
NULL   = 14#
LOOKUP = 15# prefix for lookup keyword
WHEN   = 16# when clause

_tokenText = {
    # token constants type  val
    INVALID:'INVALID',#    invalid
    NUMLIT :'LITERAL',#    string literal
    STRLIT: 'STRLIT ',#    string literal
    FLOAT  :'FLOAT  ',#    when clause
    ALIAS  :'ALIAS  ',#    numeric literal
    PREFIX :'PREFIX ',#    prefix 
    FLDNM  :'FLDNM  ',#    field name
    MDL    :'MDL    ',#    middle (<=> or <-)
    OP     :'OP     ',#    operator
    KEYWRD :'KEYWRD ',#    known keyword
    BRKTS  :'BRKTS  ',#    bits in brackets
    EMPTY  :'EMPTY  ',#    nothing to process
    COMMA  :'COMMA  ',#    comma separator 
    COMPARE:'COMPARE',#    comparator 
    NULL   :'NULL   ',#    null value
    LOOKUP :'LOOKUP ',#    null value
    WHEN   :'WHEN   ',#    when clause        
    }

def tokenText(code):
    if code in _tokenText:
        return _tokenText[code]
    return 'Unknown code!'

class TokenType:
    code = 0
    name = ''
    transformation = ''
    extra = ''

assign=r'<-'
_equiv=r'<=>'
_alias='alias.'
_prefixs=[r'in.',r'out.']

middles=[_equiv, assign]
contains='contains'
comparitor = [r'=', r'!=', r'>=', r'<=', r'>', r'<', contains]

starterCodes = [PREFIX, STRLIT, NUMLIT, FLOAT, ALIAS, KEYWRD, BRKTS]
literalCodes = [STRLIT, NUMLIT, FLOAT]
whenStarterCodes = [PREFIX, STRLIT, NUMLIT, FLOAT, ALIAS, KEYWRD, NULL, BRKTS]
whenLiteralCodes = [STRLIT, NUMLIT, FLOAT, NULL]

def chkList(text, listToUse):
    for pref in listToUse:
        if text.startswith(pref):
            return True, pref
    return False, ''

class Parser:

    # some lists used to define options.
    
    _nulls = ['null', r"''", r'""']
    _lookups = 'lookup.'
    _verbose = True
    

    def __init__(self):
        self.keywordsList = Keywords.mykeywordsList


    def getTokens(self, rawText):
        self.rawText = rawText
        self.offset = 0 # increment if something valid is found
        tokenList = []
        tt =TokenType()
        tt.code, tt.name  = self._getNextToken()
        #print  tt.code, tt.name
        while True: 
            tokenList.append(tt)
            if tt.code != INVALID and tt.code != EMPTY:
                tt = TokenType()
                tt.code, tt.name  = self._getNextToken()  
                #print  tt.code, tt.name                                          
            else:
                break;
            
        return tokenList
    
    def checkRule(self, rawText):
        ''' checks rules is syntactically valid
        '''
        self.rawText = rawText
        self.offset = 0 # increment if something valid is found

        code, name  = self._getNextToken()
        while code != INVALID:
            if code != EMPTY:
                code, name  = self._getNextToken()
            else:
                return True, '', '';
        return False, self.offset, name
    
    def _getNextToken(self):
        ''' returns type and value of next token
        '''
        name = ''
        curPos = self.offset
        maxl = len(self.rawText)

        # skip leading white space
        #print 'curPos ', curPos, self.rawText[curPos:]
        while curPos < maxl and self.rawText[curPos].isspace():
            curPos += 1 
        
        if curPos >= maxl: # reached the end of the line
            return EMPTY, ''

        if self.rawText[curPos] == '#': # start of comment
            return EMPTY, ''

        if self.rawText[curPos] == ',': 
            self.offset += 1
            return COMMA, ','
                
        if self.rawText[curPos] == '"': # start of string literal
            name = self.rawText[curPos+1:].split('"')[0]  # todo consider embeded quotes - but not today
            curPos += len(name)+1
            if curPos >= maxl or self.rawText[curPos] != '"':
                return INVALID, 'missing "'
            self.offset = curPos + 1            
            return STRLIT, "'"+name+"'"
        
        
        if self.rawText[curPos] == '(': # start of bracketed text
            bc = 1 # bracket count
            np = curPos +1 # new position
            while bc > 0 and np < maxl:
                ch = self.rawText[np]
                name += ch
                if ch == ')':
                    bc -= 1
                elif ch == '(':
                    bc+=1
                np += 1 
            if bc != 0:                
                return INVALID, 'missing ")"'
            
            name = name[:-1] # strip the last character off (the closeing bracket) 
            curPos += len(name)+2            
            self.offset = curPos 
            return BRKTS, name
        
        if self.rawText[curPos] in r'+-/*|':
            self.offset = curPos + 1
            return OP, self.rawText[curPos]
         
        if self.rawText[curPos].isdigit() or self.rawText[curPos] == '.': # start of numeric literal            
            while curPos < maxl and (self.rawText[curPos].isdigit() or self.rawText[curPos] == '.'):
                name += self.rawText[curPos]
                curPos += 1
            self.offset = curPos 
            if '.' in name:
                try: 
                    float(name) # is it a valid number?
                    return FLOAT, name 
                except ValueError: 
                    return INVALID, 'Invalid number'
            return NUMLIT, name

        couldBe, name = chkList(self.rawText[curPos:], middles)
        if couldBe:
            self.offset = curPos+len(name)
            return MDL, name
        
        couldBe, name = chkList(self.rawText[curPos:], comparitor)
        if couldBe:
            self.offset = curPos + len(name)
            return COMPARE, name
        
        
        couldBe, name = chkList(self.rawText[curPos:], _prefixs)
        if couldBe:
            self.offset = curPos + len(name)
            return PREFIX, name

        if self.rawText[curPos:].startswith(_alias):
            self.offset = curPos + len(_alias)
            return ALIAS, _alias
            
        if self.rawText[curPos:].startswith(self._lookups):
            self.offset = curPos + len(self._lookups)
            return LOOKUP, self._lookups
            
        if '(' in self.rawText[curPos:]:
            ky = self.rawText[curPos:].split('(')[0] # keyword must be followed by brackets        
            couldBe, name = self._inList(ky, self.keywordsList)
            if couldBe:
                self.offset = curPos + len(ky)
                return KEYWRD, name
            if ky.lower() == 'when':
                self.offset = curPos + len(ky)
                return WHEN, ky
            
        # Field must start with an alpha         
        if not self.rawText[curPos].isalpha(): # not start of field means error!
            return INVALID, ' Unexpected character.'
        
        #while curPos < maxl and re.match(r'^[A-Za-z0-9_]+$', self.rawText[curPos]):
        while curPos < maxl and (self.rawText[curPos].isalnum() or self.rawText[curPos] == '_'):        
            name+=self.rawText[curPos]
            curPos += 1
        self.offset = curPos 
        
        couldBe, tmp = self._inList(name, Parser._nulls)
        if couldBe:
            return NULL, tmp 
         
        return FLDNM, name
    
    def _inList(self, text, listToUse):
        if text.lower() in listToUse:
            return True, text
        return False, ''
        

        
if __name__ == '__main__':        
    testText='''in.event_id <=> out.event_id
"text" + in.val <=> out.val
a((x))<=>b(()())
in.a1 + default(stuff(), null, "zero")  <=> out.b2 # simple rule with most features
# this is a comment 
   # so is this but it doesn't start at the begining
# this is a rule
in.a <=> out.b 
junk <=> out.b # should be accepted by parser but not by grammer
lookup(stuff) <=> out.txt
lookup(stuff with embedded brackets ()) <=> out.b   
lookup(stuff) <=> default(stuff)
lookup(stuff with missing bracket () <=> out.b   
lookup(stuff) <=> default(stuff())
lookup(stuff) <=> default(extra close bracket()))
lookup(stuff) <=> default(extra open bracket()
in.a < this is not valid
in.a <=> out.b # this is rule with a comment 
in.a + 5 <=> out.b # this is rule with a literal and a comment
in.a+5<=>out.b# no spaces
in.a+in.b-in.c/in.d*in.e <=>out.b# all the operators
in.a    +    5    <=>    out.b    # tabs (check editor hasn't changed them to spaces!)
in.abc + lookup(stuff + more stuff) <=> out.b123 
# next line is blank

5 + in.a <=> out.b # this is a literal with a rule and a comment


in.abc + look(stuff) <=> out.b123 # not a keyword
default(in.a1 = null, 0) <=> default(out.b != '')   
 
in.a = (6 - 5) *6
in.event_id <=> out.event_id
in.abc <=> out._id
in.12abc <=> out.id
5+in.b<=>lookup(some stuff) - "text"
alias.a <=> in.b
alias.mcc <- substringS3 + substrisanamewithextratext(in.plmnid,1,1) | substring(in.plmnid,0,1) | substr(in.plmnid,2,1)
sumstr(in.plmnid,2,1) <=> substr(in.plmnid,2,1)
alias.mcc <- substring(in.plmnid,1,1) | substring(in.plmnid,0,1) | substring(in.plmnid,2,1) # an alias not a rule
in.a + alias.mss <=> out.b
in.a + alias.mss <=> lookup.b
in.a <=>out.b when(in.a = 1)
in.a <=>out.b when(in.a >= 1)
in.a + 0.0<=>out.b when(in.a >= 1)
in.a + .0<=>out.b when(in.a >= 1)
in.a + -.0<=>out.b when(in.a >= 1)
in.a + 1..2 <=>out.b when(in.a >= 1) # should fail invalid number 
in.a + -.0<=>out.b WHEN(in.a >= 1) # should pass
in.a + -.0<=>out.b w(in.a >= 1)
in.a contains(1,2,3)  
in.a <=> default(out.b, 0, 1)
'''

    # do something with testText
    inFile = '' 
    for arg in sys.argv:
        if arg.startswith("inFile="):
            inFile=arg.split('=')[1]
 
    if inFile == '':
        rawText = testText
    else:
        rawText = [line.strip() for line in open(inFile)] # read what ever is in specified file
     
    lineNum = 0
    parser = Parser()
        
    for text in rawText.splitlines():
        lineNum +=1
        print lineNum,':',text

        tokenList = parser.getTokens(text)
        
        for tt in tokenList:
            if tt.code != EMPTY:
                print tokenText(tt.code).strip(), tt.name,
        print
        
        ok, code, name  = parser.checkRule(text)
        if not ok:
            #print ' Error encountered:',name
            print '  '+text
            print '  '+' '*parser.offset+'^'+' Error encountered:',name
        
    
    
    