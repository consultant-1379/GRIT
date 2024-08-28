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

'''
apply the grammar to a rule to produce a tokenlist
'''


'''
#literal = [\"].*[\"]|[0-9]+' # quoted string or sequence of digits
#fieldName = {[A-Za-z]+[A-Za-z_0-9]*}' # an alpha followed by zero or more alpha's, underscores or digits - follows a prefix
#prefix = {in.|out.|alias.}
#operator = {+|-|/|*||} - includes the pipe | to join text e.g. substring(*) | "hello"
#comparator = {=|!=|>|<|>=|<=}
#keyword = '{default|lookup|substring|min|max|avg|count|sum|round}'
#method = '{keyword(*)}'
#starter = '{[literal|{prefix}{fieldName}|method|alias]}
#middle = '[<=>|<-]'
#when = {prefix}{fieldName} {operator} { {prefix}{fieldName} | literal } [, {prefix}{fieldName} {operator} { {prefix}{fieldName} | literal }]*
#sentence='{starter} [{operator}{starter}]* {middle} {starter} [{operator}{starter}]* [when]
'''
import parser as Parser
import keywords as Keywords

class Grammar:
    '''
    # token constants type
    See parser for the different tokens available

    '''

    def __init__(self, rawText, aliasDict, verbose = False):
        self.verbose = verbose
        self.inFld = []  # input fields mentioned in rule
        self.outFld = []
        self.inChkFld = []  # input fields tested in rule (excludes fields only mentioned in when clauses)
        self.outChkFld = []
        self.ltransform=[]
        self.rtransform=[]
        self.leftLookup=''
        self.rightLookup=''
        self._whenLeftTransform = []
        self._whenRightTransform = []
        self._whenLeftLookup = ''
        self._whenRightLookup = ''
        self.whenClause = []
        self.keywords = Keywords.keywords()
        self.keywords.setGrammar(self)
        self._isRule = False
        self._isAlias = False
        self._validPrefix = ''
        self._isLeft = True # changed to false after 'middle' is processed
        self._isAgg = False
        self._isWhenAgg = False
        self._isWhenClause = False
        self.aliasDict = aliasDict

        self.parser = Parser.Parser()
        self.tokenList = self.parser.getTokens(rawText)
        self._doStuff(self.tokenList)


    def _getVariables(self):
        return self.variables

    def isValid(self):
        ''' Is this a valid rule '''
        return self._isRule or self._isAlias

    def isRule(self):
        ''' Is this a valid rule '''
        return self._isRule

    def isAlias(self):
        ''' Is this a valid rule '''
        return self._isAlias

    def getResults(self):
        return (self.ltransform, self.rtransform, self.leftLookup, self.rightLookup, self.whenClause, self._isAgg)

    def getTokenList(self):
        return self.tokenList

    def testInFields(self, fieldsList):
        ''' fieldsList must be a list of lowercase fields names from the input table
        return False if an input field does not exist in fieldList
        '''
        for fld in self.inFld:
            if fld.lower() not in fieldsList:
                if self.verbose:
                    print ' Field %s is not in input field list'%fld
                return False
        return True

    def testOutFields(self, fieldsList):
        ''' fieldsList must be a list of lowercase field names  from the output table
        return False if an output field does not exist in fieldList
        '''
        for fld in self.outFld:
            if fld.lower() not in fieldsList:
                if self.verbose:
                    print ' Field %s is not in output field list'%fld
                return False
        return True

    #
    # End of public methods
    #
    def _doStuff(self, tokenList):
        self._isRule = False

        if len(tokenList) < 4: # no rule has less then four tokens
            return

        curToken = 0
        token = tokenList[curToken]
        if token.code == Parser.EMPTY : # nothing to do
            print ' this is empty'
            return

        # assigning an alias always looks like
        # alias.fldname <- definition
        if tokenList[2].code == Parser.MDL and tokenList[2].name == Parser.assign:
            self._handleAliasAssign(tokenList)
            return

        #expand aliases and brackets now. Then we wont have to worry about them again
        # This doesn't work becuase we can't expand brackets properly!
        curToken = 0
        for token in tokenList:
            if token.code == Parser.ALIAS: # must be followed by a field name
                retVal, tokenList  = self._expandAlias(tokenList, curToken)
                if not retVal:
                    print tokenList
                    return
            #if token.code == Parser.BRKTS: # must be followed by a field name
            #    if curToken > 1 and tokenList[curToken-1].code != Parser.KEYWRD:
            #        retVal, tokenList = self._expandBrackets(tokenList, curToken)
            curToken += 1

        curToken = 0

        curToken, tokenList = self._handleSide(tokenList, curToken) # handle one side of sentence
        if curToken < 0:
            return
        #
        # If we are here, it must be a middle
        token = tokenList[curToken]
        if self._validPrefix == '':
            print 'no fields specified in expression'
            return
        elif self._validPrefix == 'in.':
            self._validPrefix = 'out.'
        else:
            self._validPrefix = 'in.'

        if token.code != Parser.MDL:
            print 'Invalid token, %s, expected one of %s'%(token.name, Parser.middles)
            return

        curToken += 1
        self._isLeft = False # ToDo do this properly

        curToken, tokenList = self._handleSide(tokenList, curToken)
        if curToken < 0:
            return

        self._isAgg = self.keywords.getIsAgg()
        self.keywords.setIsAgg(False)

        # optional When clause
        token = tokenList[curToken]
        if token.code == Parser.WHEN and curToken +1 < len(tokenList):
            if not self._handleWhen(tokenList[curToken+1]):
                print 'Invalid When clause'
                return
        elif token.code != Parser.EMPTY:
            print 'Unexpected token in sentence'
            return

        self._isRule = True


    def _handleWhen(self, token):

        isValid = False
        '''
        rule when(prefix field OP {literal | prefix field} [comma prefix field OP {literal | prefix field}[...]])
        '''
        self._isWhenClause = True

        if token.code != Parser.BRKTS:
            print 'Not a valid "when" clause!'
            return isValid

        parser = Parser.Parser()
        tokenList = parser.getTokens(token.name)
        curPos = 0

        #retVal = False
        while curPos < len(tokenList) -1:
            if tokenList[curPos].code == Parser.ALIAS:
                retVal, tokenList  = self._expandAlias(tokenList, curPos)
                if not retVal:
                    print tokenList
                    return isValid # alias expansion failed
            curPos += 1
        else:
            curPos = 0

        whenTokenList = []

        curPos = 0
        tmpTokenList = []
        while curPos < len(tokenList):
            token = tokenList[curPos]
            tmpTokenList.append(token)

            if token.code == Parser.COMMA or curPos + 1 == len(tokenList):
                whenTokenList.append(tmpTokenList)
                tmpTokenList = []

            curPos += 1

        for whenList in whenTokenList:
            isValid, whenClausePart = self._processWhenCondition(whenList)
            if not isValid:
                break
            else:
                self.whenClause.append(whenClausePart)

        return isValid

    def _handleSide(self, tokenList, curToken, updateTransform = True):
        ''' Handle one side of a sentence
        '''
        # A side consists of a starter,
        # it can be followed by zero or more OP and starters
        retVal = -1

        token = tokenList[curToken]
        if self._isWhenClause:
            if token.code not in Parser.whenStarterCodes:
                print ' Invalid token. Expected a literal, keyword or prefix, got a %s'%Parser.tokenText(token.code)
                return retVal, tokenList
        else:
            if token.code not in Parser.starterCodes:
                print ' Invalid token. Expected a literal, keyword or prefix, got a %s'%Parser.tokenText(token.code)
                return retVal, tokenList

        usedToken, tokenList = self.handleStarter(tokenList, curToken, updateTransform)
        if usedToken < 0:
            print tokenList
            return retVal, tokenList

        curToken += usedToken

        # A sentence can be followed by operators and starters
        token = tokenList[curToken]

        while token.code == Parser.OP and curToken +2 < len(tokenList):
            if updateTransform:
                self._updateTransform(token.name)
            curToken += 1
            token = tokenList[curToken]
            if token.code not in Parser.starterCodes:
                return retVal, tokenList

            usedToken, tokenList = self.handleStarter(tokenList, curToken, updateTransform)
            if usedToken < 0:
                print 'Invalid token ', token.name
                return retVal, tokenList
            curToken += usedToken
            token = tokenList[curToken]

        return curToken, tokenList # if we are here, then we haven't found any problems

    def _processWhenCondition(self, tokenList):
        self._isWhenClause = True
        self._isLeft = True

        whenClausePart = []
        isValid = False
        comparator = ''

        if len(tokenList) < 4: # no when condition has less then four tokens
            return isValid, 'Missing tokens'

        curToken = 0
        token = tokenList[curToken]
        if token.code == Parser.EMPTY : # nothing to do
            print ' this is empty'
            return isValid, whenClausePart

        curToken, tokenList = self._handleSide(tokenList, curToken) # handle one side of sentence
        if curToken < 0:
            return isValid, whenClausePart

        # If we are here, it must be a comparator
        token = tokenList[curToken]
        if (token.name == 'is' or token.name == 'is not') and tokenList[curToken + 1].code == Parser.NULL:
            comparator = token.name
            self.rtransform = tokenList[curToken + 1].name
        #elif token.name == 'inList' and tokenList[curToken+1].code == Parser.BRKTS:
        #    comparator = ' IN '
        #    self.rtransform = tokenList[curToken + 1].name
        else:
            if token.code != Parser.COMPARE:
                print 'Invalid token, %s, expected one of %s'%(token.name, Parser.comparitor)
                return isValid, whenClausePart

            if token.name == Parser.contains:
                comparator = 'IN'
                curToken += 1
                self._whenRightTransform.append('('+tokenList[curToken].name+')')
            else:
                comparator = tokenList[curToken].name
                curToken += 1

                self._isLeft = False

                curToken, tokenList = self._handleSide(tokenList, curToken)
                if curToken < 0:
                    return isValid, whenClausePart

                self._isWhenAgg = self.keywords.getIsAgg()
                self.keywords.setIsAgg(False)

                if self._isWhenAgg:
                    print 'Aggregation keywords are illegal in a when clause'
                    return isValid, whenClausePart

        isValid = True

        whenClausePart.append(self._whenLeftTransform)
        whenClausePart.append(comparator)
        whenClausePart.append(self._whenRightTransform)
        # TODO
        # if join and not where, comparitor must be '='
        #
        whenClausePart.append(self._whenLeftLookup)
        whenClausePart.append(self._whenRightLookup)

        #reset the values
        self._whenLeftTransform = []
        self._whenRightTransform = []
        self._whenLeftLookup = ''
        self._whenRightLookup = ''

        return isValid, whenClausePart

    def _handleField(self, tokenList, curToken, updateTransform = True):
        ''' given token 1 - a prefix and token2 -expected to be a field name, do what needs doing
                Warning - tokenList will be updated if alias is processed
            return number of tokens consumed or -1 for error
            side effects - updates inFld, outFld and transform
        '''
        token1 = tokenList[curToken]
        token2 = tokenList[curToken+1]
        if token2.code != Parser.FLDNM:
            if self.verbose:
                print 'Error, expected field name, got', token2.name
            return -1

        if token1.name != self._validPrefix and not self._isWhenClause:
            if self._validPrefix == '':
                self._validPrefix = token1.name
            else:
                print 'Can not mix "in." and "out." in the same expression '
                return -1
        fldname = token2.name.lower()
        if token1.name == 'in.': # Yuck! Todo - find a better way!
            if not self._isWhenClause:
                self.inChkFld.append(fldname)
            self.inFld.append(fldname)
            if updateTransform:
                self._updateTransform(token1.name + fldname)
            return 2
        elif token1.name == 'out.':
            if not self._isWhenClause:
                self.outChkFld.append(fldname)
            self.outFld.append(fldname)
            if updateTransform:
                self._updateTransform(token1.name + fldname)
            return 2

        print 'Should not be here'
        return -1

    def _expandAlias(self, tokenList, curPos):
        '''
        return False if error
        '''
        retVal = True
        token2 = tokenList[curPos+1]
        numToken = len(tokenList)
        if token2.code != Parser.FLDNM:
            txt = 'Error, expected field name, got', token2.name
            if self.verbose:
                print txt
            return False, txt

        if token2.name not in self.aliasDict:
            txt = 'Attempt to use undefined alias %s'%token2.name
            print txt
            return False, txt

        # build a new tokenList by replacing the 'alias.' 'keyname' with the tokens from the definition

        tt = tokenList[0:curPos ] + self.aliasDict[token2.name][:-1] # ignore the EMPTY at the end of definition
        if curPos +2 < numToken:
            tt += tokenList[curPos +2:]
        tokenList = tt
        curPos += 1
        #if len(tokenList) != numToken:
        #    print 'here',numToken
        #    for t in tokenList:
        #        print Parser.tokenText(t.code), t.name
        while curPos < len(tokenList) and retVal == 0:
            if tokenList[curPos].code == Parser.ALIAS:
                retVal, tokenList = self._expandAlias(tokenList, curPos)
                numToken = len(tokenList)
            curPos += 1

        return retVal, tokenList

    def _handleKeyword(self, token1, token2, updateTransform = True):
        ''' given token 1 - a keyword and token2 -its arguments, do what needs doing
        '''
        retVal = False
        if token2.code != Parser.BRKTS:
            if self.verbose:
                print 'Error, expected arguments for keyword, got', token2.name
            return retVal

        retVal, transform, lookup = self.keywords.keyMethods[token1.name](token1, token2)

        if retVal and updateTransform:
            self._updateTransform(transform)
            self._updateLookup(lookup)
            if self.keywords.isAggKeyword(token1.name):
                if self._isLeft:
                    self._isLeftAgg = True
                else:
                    self._isRightAgg = True

        return retVal, transform

    def handleStarter(self, tokenList, curToken, updateTransform = True):
        ''' Handle a starter
         return the number of tokens consumed
        '''
        failure = -1 # number of tokens consumed
        token = tokenList[curToken]
        if token.code == Parser.ALIAS: # must be followed by a field name
            retVal, tokenList  = self._expandAlias(tokenList, curToken)
            if not retVal:
                return failure, tokenList # alias replacement failed.
            token = tokenList[curToken]

        if self._isWhenClause:
            if token.code in Parser.whenLiteralCodes:
                if updateTransform:
                    self._updateTransform(token.name)
                return 1, tokenList
        else:
            if token.code in Parser.literalCodes:
                if updateTransform:
                    self._updateTransform(token.name)
                return 1, tokenList

        if token.code == Parser.PREFIX: # must be followed by a field name
            retVal  = self._handleField(tokenList, curToken, updateTransform)
            return retVal, tokenList

        # has to be a keyword
        if token.code == Parser.KEYWRD:
            val, transform, = self._handleKeyword(token, tokenList[curToken+1], updateTransform)
            if val < 1:
                txt = 'Error, failed to parse keyword:'+ transform
                if self.verbose:
                    print txt
                return failure, txt
            return 2, tokenList

        if token.code == Parser.BRKTS:
            ok = self._handleBrackets(token,updateTransform)
            if not ok:
                txt = 'Error, failed to parse Brackets'+ token.name
                if self.verbose:
                    print txt
                return failure, txt
            return 1, tokenList

        return -1, 'Not a valid starter! Got "%s" instead'%(token.name)

    def _handleBrackets(self, token, updateTransform = True):
        bracketStart = '('
        bracketEnd = ')'

        isValid = False

        parser = Parser.Parser()
        tokenList = parser.getTokens(token.name)

        for token in tokenList:
            if token.code == Parser.INVALID:
                print ' Syntax error detected in bracket %s. Rule will be excluded:'%(token.name)
                return isValid

        curToken = 0
        if tokenList[curToken].code not in Parser.starterCodes:
            return isValid, 'Error, not a valid starter, expected Literal, prefix or keyword.', ''

        retVal = 0
        while curToken < len(tokenList) -1 and retVal == 0:
            if tokenList[curToken].code == Parser.ALIAS:
                retVal, tokenList  = self._expandAlias(tokenList, curToken)
            curToken += 1

        if retVal != 0:
            return isValid # alias expansion failed
        else:
            curToken = 0

        if updateTransform:
            self._updateTransform(bracketStart)

        curToken, tokenList = self._handleSide(tokenList, curToken,updateTransform) # handle everything in the brackets
        if curToken < 0:
            return isValid

        if updateTransform :
            self._updateTransform(bracketEnd)

        isValid = True
        return isValid

    def _handleAliasAssign(self, tokenList):
        ''' Handle the assignment of an alias
           alias.key <- stuff!
        '''
        numToken = len(tokenList)
        if numToken < 4:
            print 'Insufficient tokens to define an alias'
            return

        curToken = 0
        token = tokenList[curToken]
        token2 = tokenList[curToken+1]

        if token.code != Parser.ALIAS or token2.code != Parser.FLDNM:
            print 'Not a valid alias definition'
            return
        if self._handleSide(tokenList, 3): # just checks for errors
            self.aliasDict[token2.name] = tokenList[3 : ] # the list of tokens after the assignment
            self._isAlias = True

    def _updateTransform(self, val):
        if self._isLeft:
            if self._isWhenClause:
                self._whenLeftTransform.append(val)
            else:
                self.ltransform.append(val)
        else:
            if self._isWhenClause:
                self._whenRightTransform.append(val)
            else:
                self.rtransform.append(val)


    def _updateLookup(self, val):
        if self._isLeft:
            if self._isWhenClause:
                self._whenLeftLookup += val
            else:
                self.leftLookup += val
        else:
            if self._isWhenClause:
                self._whenRightLookup += val
            else:
                self.rightLookup += val


if __name__ == '__main__':
    rawText= '''in.a1<=>out.b
in.a + 5 <=> out.b
 " kujwdhq
junk + in.a3 <+> out.b
default(stuff = null, 0)<=>out.b # comment here
in.a<=>default(out.b = null, 0)
#lookup(stuff with embedded brackets ()) <=> out.b
#lookup(stuff) <=> default(extra close bracket()))
#5+in.b<=>lookup(some stuff) - "text" # doesn't work!
in.a+5<=>out.b
in.a+5<=>count(out.b)
in.abc + look(stuff) <=> out.b123 # not a keyword
default(in.a1 = null, 0) <=> out.b
in.a <=> default(out.b > 2, 2)
default(default(in.a8 > 1, 1) < 1, 0) <=> out.b
substring(substring(in.d, 3, 4), 4, 5) <=> out.b
in.a_2 <=> out.b
alias.mcc <- in.a
in.a + alias.mcc <=> out.b
alias.mcc <- substring(in.plmnid,1,1) | substring(in.plmnid,0,1) | substring(in.plmnid,2,1) # an assignment not a rule
in.x + alias.mcc <=> out.y
default(in.a = null, 0)<=>out.b # no. 22 here
default(default(in.a < 1, null) = null, 0)<=>out.b
#lookup(DIM_RNC, nodeName, in.nodeId=lookup.nodeId) <=> out.nodeName
#lookup(DIM_RNC, nodeName, in.nodeId=lookup.nodeId and in.a = lookup.b) <=> out.nodeName
default(lookup(DIM_RNC, nodeName, in.nodeId=lookup.nodeId) = null, "Unknown") <=> out.nodeName
substring(in.a, 2, 4) <=> out.b
count(in.a) <=> out.b
default(count(in.a) > 1, 1) <=> out.b
substring(substring(in.a,3,4),4,5) <=> out.b
in.a<=>out.b when(in.a1 = 1, in.a2 = 1)
in.a<=>out.b when (in.c = 1) # illegal space after 'when'
in.a<=>out.b when(out.b3 = 1) # b3 is unknown field
in.a<=>out.b when(in.a1 != null, in.a2 = null)
count(in.a) <=> out.b when(in.a = out.b)
alias.w1<- in.a = out.b
count(in.a) <=>  out.b when(alias.w1)
count(in.a) <=> out.b when(in.a = out.b, in.a1 = out.b1)
alias.w2<- in.a1 = out.b1
count(in.a) <=>  out.b when(alias.w1, alias.w2)
count(in.a) <=> out.b when(in.a >= out.b)
"active" <=> in.status
default(count(in.a) > 1, 1.0) <=> out.b
default(count(in.a) > 1.0, 1.0) <=> out.b
substring(in.a,4,5.0) <=> out.b
alias.nodeId <- in.gcellid - in.gcellid/256*256
alias.nodeId <=> out.nodeId
alias.nodeId2 <- (in.gcellid - in.gcellid/256*256)
alias.nodeId2 <=> out.nodeId
count(distinct(in.a)) <=> out.b
pad("0", 3, in.a) <=> out.b
'''

    InFlds = ['a','a1','a2', 'a_2', 'x', 'nodeid','gcellid'] # list of available fields in the input table - Must be all lower case!
    OutFlds = ['b','b1','b2', 'y', 'nodename','nodeid'] # list of available fields in the input table
    aliasDict = {}
    numValid = 0
    lineNum = 0
    for text in rawText.splitlines():
        lineNum +=1
        print lineNum,':',text

        grmr = Grammar(text, aliasDict)

        if not grmr.isValid():
            print 'Not valid grammer - output is ',grmr.getResults()
            continue
        numValid += 1
        if grmr.isAlias():
            aliasDict = grmr.aliasDict
            print 'Updating alias dictionary'
            continue
        if not grmr.testInFields(InFlds):
            print 'Ignoring rule as it contains unknown input field'
            continue
            # all input fields in input table
        if not grmr.testOutFields(OutFlds):
            print 'Ignoring rule as it contains unknown output field'
            continue

        #print ' -- Rule is valid - output is ',grmr.getResults()

    print 'Number of valid rules:',numValid

    '''
    aliasDict = {}
    lineNum = 0
    for text in rawText.splitlines():
        lineNum +=1
        print lineNum,':',text

        grmr = Grammar(text, aliasDict)

        code, name  = grmr.getNextToken()
        while code != parser.INVALID:
            if code != parser.EMPTY:
                print ' %d %8s %d'%(code, name, grmr.offset)
                code, name  = grmr.getNextToken()
            else:
                break;
        else:
            print ' Error encountered:',name
            print '  '+text
            print '  '+' '*grmr.offset+'^'
    '''