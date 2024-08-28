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

import parser as Parser
import dbUtility as DbUtility

'''
Handle the detailed parsing and processing for keywords.
'''

# list of possible keywords.
#
# To add to this list, write a method return True or False and the text to add to a transform and add it to the 'keyMethods' dictionary below
# A keyword is a word from the reserved list,  followed by one or more comma separated arguments
# an argument can be:
#   another keyword
#   a comparitor
#   a field
#   a literal
#
# A comparitor is :
#   an argument followed by a comparison operator followed by a literal,
# supported comparison operators are:
#   =, !=, >=, <=, >, <
#
# The possible combinations depend on the keyword
#
# To add to this list, write a method return True or False and the text to add to a transform and add it to the 'keyMethods' dictionary below
#_keywords=['default', 'lookup', 'substr', 'sum', 'count', 'max', 'min', 'avg']
mykeywordsList = [
    'default',
    'lookup',
    'substr',
    'substring',
    'sum',
    'summation',
    'count',
    'max',
    'maximum',
    'min',
    'minimum',
    'unique',
    'distinct',
    'avg',
    'average',
    'cast',
    'pad',
    'padright',
    'round'
    ]
dbUtility = DbUtility.DbUtility()
class keywords:
    _aggList = ['sum','summation','count','max','maximum','min','minimum', 'avg','average', 'unique', 'distinct']

    def __init__(self):
        self.grammar = None
        self.lookupCounter = 0
        self._isAgg = False
        self.keyMethods = {
            'default':      self._keyDefault,
            'lookup':       self._keyLookup,
            'substr':       self._keySubstring,
            'substring':    self._keySubstring,
            'sum':          self._keySum,
            'summation':    self._keySum,
            'count':        self._keyCount,
            'max':          self._keyMax,
            'maximum':      self._keyMax,
            'min':          self._keyMin,
            'minimum':      self._keyMin,
            'unique':       self._keyUnique,
            'distinct':     self._keyDistinct,
            'avg':          self._keyAvg,
            'average':      self._keyAvg,
            'cast':         self._keyCast,
            'pad':          self._keyPad,
            'padright':     self._keyPadRight,
            'round':        self._keyRound
            }
        self.parser = Parser.Parser()

    def getIsAgg(self):
        return self._isAgg

    def setIsAgg(self, isAgg):
        self._isAgg = isAgg

    def isAggKeyword(self, keyword):
        if keyword in self._aggList:
            return True
        return False

    def setGrammar(self, grammar):
        self.grammar = grammar
        self.lookupCounter *= 10

    def getKeywords(self):
        keywords = self.keyMethods.keys()
        return keywords

    def _keySubstring(self, token1, token2):
        isValid = False # not a valid keyword

        keyWordStart = 'substring('
        keyWordEnd = ')'

        transformation = ''

        tokenList = self.parser.getTokens(token2.name)

        curPos = 0
        if tokenList[curPos].code not in Parser.starterCodes:
            return isValid, 'Error, not a valid starter, expected Literal, prefix or keyword.', ''

        usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects

        if usedTokens < 1:
            return isValid, 'Error detected.', ''
        curPos += usedTokens

        if curPos >= len(tokenList) or tokenList[curPos].code != Parser.COMMA:
            return False, 'Missing comma before substring offset.', ''

        transformation += keyWordStart
        lookup = ''
        currentPosition = 0

        stopCode = [Parser.COMMA]

        # add everything so far to the transformation
        while tokenList[currentPosition].code not in stopCode:
            tmpIsValid, tmpTransformation, tmpLookup, tmpCurrentPosition = self.getValue(tokenList, currentPosition, stopCode)
            if tmpIsValid:
                transformation += tmpTransformation
                lookup += tmpLookup
                currentPosition = tmpCurrentPosition
            else:
                return tmpIsValid, tmpTransformation, lookup

        transformation += tokenList[currentPosition].name # the comma
        currentPosition += 1

        # the string offset
        #  check if it is a negative number
        if tokenList[currentPosition].code == Parser.OP and tokenList[currentPosition].name == '-':
            transformation += tokenList[currentPosition].name
            currentPosition += 1

        if tokenList[currentPosition].code == Parser.NUMLIT:
            transformation += tokenList[currentPosition].name
            currentPosition += 1
        else:
            return isValid, 'Position must be an integer value.', ''

        # the next comma!
        if currentPosition >= len(tokenList) or tokenList[currentPosition].code != Parser.COMMA:
            return False, 'Missing comma before substring length.', ''


        transformation += tokenList[currentPosition].name
        currentPosition += 1

        if tokenList[currentPosition].code == Parser.NUMLIT:
            transformation += tokenList[currentPosition].name
            currentPosition += 1
        else:
            return isValid, 'Length must be an integer value.', ''

        transformation += keyWordEnd

        isValid = True
        return isValid, transformation, lookup

    def _keyDefault(self, token1, token2):
        isValid = False # not a valid keyword
        # syntax = 'default(starter comparitor literal , literal)'
        keyWordStart = '(case when '
        keyWordEnd = ' end)'
        #
        # default( starter compare literal | null , literal )
        #
        tokenList = self.parser.getTokens(token2.name)
        curPos = 0
        if tokenList[curPos].code not in Parser.starterCodes:
            return isValid, 'Error, not a valid starter, expected Literal, prefix or keyword.', ''
        usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects

        if usedTokens < 1:
            return isValid, 'Error detected.', ''
        curPos += usedTokens

        maxLength = len(tokenList)

        commaPosition = 0
        comparitorPosition = 0
        tmpIsValid, commaPosition = self.getCommaPosition(tokenList, commaPosition)
        if not tmpIsValid:
            return tmpIsValid, commaPosition, ''

        tmpIsValid, comparitorPosition = self.getComparitorPosition(tokenList, comparitorPosition, commaPosition)
        if not tmpIsValid:
            return tmpIsValid, comparitorPosition, ''


        transformation = keyWordStart
        lookup = ''
        currentPosition = 0
        base = ''
        tmpIsValid, tmpCurrentPosition, txt, tmpLookup = self._getLeftOfComapritor(tokenList, currentPosition, comparitorPosition)
        if tmpIsValid:
            base = txt
            transformation += txt
            lookup += tmpLookup
            currentPosition = tmpCurrentPosition
        else:
            return tmpIsValid, txt, ''

        tmpIsValid, currentPosition, txt = self._getComparitor(tokenList, currentPosition)
        if tmpIsValid:
            transformation += txt
        else:
            return tmpIsValid, txt, ''

        # if the next value is null, it will have already been taken care of in the getComparitor method.
        if tokenList[currentPosition].code != Parser.NULL:
            tmpIsValid, currentPosition, txt = self._getRightOfComparitor(tokenList, commaPosition, currentPosition)
            if tmpIsValid:
                transformation += txt
            else:
                return tmpIsValid, txt, ''
        else:
            currentPosition += 2

        transformation += ' then '
        #usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects
        #print 'here default()', currentPosition
        #for t in tokenList[currentPosition:]:
        #    print Parser.tokenText(t.code), t.name
        retVal = False
        if tokenList[currentPosition].code == Parser.ALIAS:
            retVal, tokenList = self.grammar._expandAlias(tokenList, currentPosition)
            if not retVal:
                return isValid, 'Error, expanding alias in default(). %s'%tokenList, ''
            maxLength = len(tokenList)
        stopCodes = [Parser.EMPTY, Parser.COMMA]
        tmpIsValid, txt, tmpLookup, currentPosition = self._getAnyValue(tokenList, currentPosition, maxLength, stopCodes)
        #tmpIsValid, txt, tmpLookup, currentPosition = self.getValue(tokenList, currentPosition, stopCodes)
        if tmpIsValid:
            transformation += txt
            lookup += tmpLookup
        else:
            return tmpIsValid, txt, ''

        if currentPosition == len(tokenList) or tokenList[currentPosition].code != Parser.COMMA:
            # if there is no else clause
            transformation += ' else ' + base + keyWordEnd
            isValid = True
        else: # handle else clause
            currentPosition += 1
            #print 'here default() else clause', currentPosition
            #for t in tokenList[currentPosition:]:
            #    print Parser.tokenText(t.code), t.name
            retVal = False
            if tokenList[currentPosition].code == Parser.ALIAS:
                retVal, tokenList = self.grammar._expandAlias(tokenList, currentPosition)
                if not retVal:
                    return isValid, 'Error, expanding alias in default(). %s'%tokenList, ''

            tmpIsValid, txt = self._getLiteral(tokenList, currentPosition)
            if tmpIsValid:
                transformation += ' else ' + txt + keyWordEnd
                isValid = True
            else:
                return tmpIsValid, txt, ''


        return isValid, transformation, lookup



    def _keyLookup(self, token1, token2):

        ''' handle a dim table lookup with or without aggregation
        lookup( lookupTable, return_fld, in.fld1 [= lookup.key1[, in.fld2=lookup.key2[...]] ] )
        lookup( lookupTable, aggregation, return_fld, in.fld1 [= lookup.key1[, in.fld2=lookup.key2[...]] ] )
        '''
        isValid = False
        self._isAgg= False
        lkFldLst = []
        tokenList = self.parser.getTokens(token2.name)
        if len(tokenList) < 6:
            txt = 'Invalid format for lookup. Insufficient arguments'
            return isValid, txt, ''


        lookupTable = tokenList[0].name
        curPos = 2
        if (tokenList[curPos].name=="sum" or tokenList[curPos].name=="count"):
            self._isAgg=True
            if tokenList[1].code != Parser.COMMA or tokenList[3].code != Parser.COMMA or tokenList[5].code != Parser.COMMA:
                txt = 'Invalid format for lookup. Expected lookup( lookupTable,aggregation, return_fld, in.fld1 = lookup.key1)\n                                                       ^           ^                         '
                return isValid, txt, ''

            if tokenList[0].code != Parser.FLDNM:
                txt = 'Invalid format for lookup. Expected lookup( DIM_TABLE,aggregation, return_fld, in.fld1 [= lookup.key1[ , in.fld2=lookup.key2[...]] ] )'
                return isValid, txt, ''


            if tokenList[4].code != Parser.FLDNM:
                txt = 'Invalid format for lookup. Expected lookup( lookupTable,aggregation, RETURN_FLD, in.fld1 [= lookup.key1[ , in.fld2=lookup.key2[...]] ] )'
                return isValid, txt, ''

            aggName=tokenList[curPos].name
            curPos=curPos+2
            returnFld = tokenList[curPos].name
            curPos=curPos+2

        else:
            self._isAgg= False
            if tokenList[1].code != Parser.COMMA or tokenList[3].code != Parser.COMMA:
                txt = 'Invalid format for lookup. Expected lookup( lookupTable, return_fld, in.fld1 = lookup.key1)\n                                                       ^           ^                         '
                return isValid, txt, ''

            if tokenList[0].code != Parser.FLDNM:
                txt = 'Invalid format for lookup. Expected lookup( DIM_TABLE, return_fld, in.fld1 [= lookup.key1[ , in.fld2=lookup.key2[...]] ] )'
                return isValid, txt, ''

            if tokenList[2].code != Parser.FLDNM:
                txt = 'Invalid format for lookup. Expected lookup( lookupTable, RETURN_FLD, in.fld1 [= lookup.key1[ , in.fld2=lookup.key2[...]] ] )'
                return isValid, txt, ''
            returnFld = tokenList[curPos].name
            lkFldLst.append(returnFld)
            curPos=curPos+2


        txt = ''
        rawTable = ''
        while curPos <= len(tokenList) and tokenList[curPos].code != Parser.EMPTY:
            # handle left. This also expands aliases.
            usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects
            if usedTokens < 1:
                return False, 'Error detected. %s'%tokenList, ''

            if tokenList[curPos].code == Parser.PREFIX and rawTable == '':
                rawTable = tokenList[curPos].name

            pos = curPos
            curPos += usedTokens
            tmpTxt = ''
            while pos < curPos:
                if tokenList[pos].code == Parser.KEYWRD:
                    if tokenList[pos].name.startswith('substr'):
                        tmpTxt += 'substring(' + tokenList[pos+1].name + ')' # TODO this will allow any old crap!
                        pos += 1
                    else:
                        return False, 'Error detected. Only the "substring" keyword is supported in a lookup', ''
                else:
                    tmpTxt += tokenList[pos].name
                pos += 1

            while tokenList[curPos].code == Parser.OP and curPos +2 < len(tokenList):
                tmpTxt += tokenList[curPos].name
                curPos += 1
                usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects
                if usedTokens < 1:
                    return False, 'Error detected. %s'%tokenList, ''

                pos = curPos
                curPos += usedTokens
                while pos < curPos:
                    if tokenList[pos].code == Parser.KEYWRD:
                        if tokenList[pos].name.startswith('substr'):
                            tmpTxt += 'substring(' + tokenList[pos+1].name + ')'
                            pos += 1
                        else:
                            return False, 'Error detected. Only the "substring" keyword is supported in a lookup', ''
                    else:
                        tmpTxt += tokenList[pos].name
                    pos += 1
            txt += 'cast('+tmpTxt+' as varchar)'

            if tokenList[curPos].code != Parser.COMPARE:
                # This only works if the left side is a field name!
                txt += ' = cast(lookup.'+ tokenList[curPos-1].name+' as varchar)'
                if tokenList[curPos-1].name not in lkFldLst:
                    lkFldLst.append(tokenList[curPos-1].name)
            else:
                if tokenList[curPos].name == '=' :#or tokenList[curPos].name == '!=':
                    txt += tokenList[curPos].name
                    curPos += 1
                else:
                    txt = 'Invalid format for lookup. Only join operator supported is "=", got "%s" instead.'%tokenList[curPos].name
                    return isValid, txt, ''

                # Only thing allowed after the '=' is fld or lookup.fld
                if tokenList[curPos].code == Parser.LOOKUP:
                    curPos += 1
                if tokenList[curPos].code == Parser.FLDNM:
                    tmpTxt = 'cast(lookup.'+tokenList[curPos].name+' as varchar)'
                    fld = tokenList[curPos].name
                elif tokenList[curPos].code == Parser.KEYWRD:
                    if tokenList[curPos].name == 'pad' :
                        valid, tmpTxt, fld = self._keyPad(tokenList[curPos], tokenList[curPos+1], False, True)
                    elif tokenList[curPos].name == 'padright' :
                        valid, tmpTxt, fld = self._keyPadRight(tokenList[curPos], tokenList[curPos+1], False, True)
                    else:
                        txt = 'Invalid format for lookup. Only thing allowed after the "=" is fldName or lookup.fldName. Got "%s" instead'%(tokenList[curPos].name)
                        return isValid, txt, ''
                    curPos += 1
                    if not valid:
                        txt = 'Problem with use of pad() in lookup(). %s'%(tmpTxt)
                        return isValid, txt, ''
                else:
                    txt = 'Invalid format for lookup. Only thing allowed after the "=" is fldName or lookup.fldName. Got "%s" instead'%(tokenList[curPos].name)
                    return isValid, txt, ''

                txt += tmpTxt
                if tokenList[curPos].name not in lkFldLst:
                    lkFldLst.append(fld)
                curPos += 1

            if tokenList[curPos].code == Parser.COMMA:
                txt += ' and ' # needs the spaces!
                curPos += 1

        lookupLabel = 'lookup_%d'%self.lookupCounter

        wheretxt = txt.replace('lookup.', lookupTable + '.')
        ontxt = txt.replace('lookup.', lookupLabel + '.')
        transform = lookupLabel + '.' + returnFld

        if self._isAgg:

            fldLst1=aggName+"("+lookupTable+'.'+returnFld+") as "+returnFld+","
            fldLstSumlk = lookupTable+'.'+(','+lookupTable+'.').join(lkFldLst)
            if rawTable == '':
                rawTable = 'in.' # consequence of not handling substr properly is that we don't always know the data table!
            newLookupText = ' left join (select %s %s from %s group by %s ) as lookup_%d on %s ' %( fldLst1,fldLstSumlk, lookupTable, fldLstSumlk, self.lookupCounter, ontxt )
        else:

            fldLst = lookupTable+'.'+(','+lookupTable+'.').join(lkFldLst)
            if rawTable == '':
                rawTable = 'in.' # consequence of not handling substr properly is that we don't always know the data table!
            newLookupText = ' left join (select %s from %s group by %s ) as lookup_%d on %s ' %( fldLst, lookupTable, fldLst, self.lookupCounter, ontxt )


        lookup = newLookupText
        self.lookupCounter += 1

        isValid = True
        return isValid, transform, lookup

    def _keyCast(self, token1, token2):
        isValid = False
        tokenList = self.parser.getTokens(token2.name)
        if len(tokenList) != 3:
            txt = 'Invalid format for cast. Expected a field name'
            return isValid, txt, ''

        if tokenList[0].code != Parser.PREFIX or tokenList[1].code != Parser.FLDNM:
            txt = 'Invalid format for cast. Expected cast( in.fld1)'
            return isValid, txt, ''

        self.grammar._handleField(tokenList, 0, False)

        transform = 'cast(%s%s as varchar)' % (tokenList[0].name, tokenList[1].name)
        return True, transform, ''

    def _keyPad(self, token1, token2, updateFields = True, isLookup = False):
        isValid = False
        tokenList = self.parser.getTokens(token2.name)
        if len(tokenList) < 6:
            txt = 'Invalid format for Pad. Expected pad( padChar, strLen, object)'
            return isValid, txt, ''

        if (tokenList[0].code != Parser.STRLIT or
            tokenList[1].code != Parser.COMMA or
            tokenList[2].code != Parser.NUMLIT or
            tokenList[3].code != Parser.COMMA ):
            txt = 'Invalid format for Pad. Expected pad(padChar, strLen, object)'
#             print 'pad got ',
#             for t in tokenList:
#                 print Parser.tokenText(t.code)+':', t.name
            return isValid, txt, ''

        if updateFields:
            self.grammar._handleField(tokenList, 4, False)
                    
        transform=dbUtility.getPadSyntax(tokenList[0].name,tokenList[2].name,tokenList[4].name,tokenList[5].name)

      
        myLookup = ''
        if isLookup:
            myLookup =  tokenList[5].name
        return True, transform, myLookup

    def _keyPadRight(self, token1, token2, updateFields = True, isLookup = False):
        isValid = False
        tokenList = self.parser.getTokens(token2.name)
        if len(tokenList) < 6:
            txt = 'Invalid format for Padright. Expected padright( padChar, strLen, object)'
            return isValid, txt, ''

        if (tokenList[0].code != Parser.STRLIT or
            tokenList[1].code != Parser.COMMA or
            tokenList[2].code != Parser.NUMLIT or
            tokenList[3].code != Parser.COMMA ):
            txt = 'Invalid format for PadRight. Expected padright(padChar, strLen, object)'
#             print 'pad got ',
#             for t in tokenList:
#                 print Parser.tokenText(t.code)+':', t.name
            return isValid, txt, ''

        if updateFields:
            self.grammar._handleField(tokenList, 4, False)
            
            
                 
        transform=dbUtility.getPadRightSyntax(tokenList[0].name,tokenList[2].name,tokenList[4].name,tokenList[5].name)

    
        myLookup = ''
        if isLookup:
            myLookup =  tokenList[5].name
        return True, transform, myLookup

    def _keyCount(self, token1, token2):
        isAgg, txt = self._keyAgg('count', token2)
        return isAgg, txt, ''

    def _keyMax(self, token1, token2):
        isAgg, txt = self._keyAgg('max', token2)
        return isAgg, txt, ''

    def _keyMin(self, token1, token2):
        isAgg, txt = self._keyAgg('min', token2)
        return isAgg, txt, ''

    def _keySum(self, token1, token2):
        isAgg, txt, lookup = self._keyAgg('sum', token2)
        return isAgg, txt, lookup

    def _keyAvg(self, token1, token2):
        isAgg, txt = self._keyAgg('avg', token2)
        return isAgg, txt, ''

    def _keyDistinct(self, token1, token2):
        isAgg, txt = self._keyAgg('distinct', token2)
        return isAgg, txt, ''

    def _keyUnique(self, token1, token2):
        isAgg, txt = self._keyAgg('unique', token2, True)
        return isAgg, txt, ''

    def _keyRound(self, token1, token2):
        
        roundKeywordList = dbUtility.getRoundSyntax()
        keyWordStart=roundKeywordList[0] 
        keyWordEnd = ')'
        transformation = ''
        isValid=False
        curPos=0
        tokenList = self.parser.getTokens(token2.name)
        usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects
        if usedTokens < 1:
            return isValid, 'Error detected.', ''
            curPos += usedTokens
        transformation += keyWordStart
        lookup = ''
        currentPosition = 0
        if tokenList[len(tokenList)-2].code != Parser.NUMLIT:
            return False, 'Length must be an integer value.', ''

        if tokenList[len(tokenList)-3].code != Parser.COMMA:
            return False, 'Missing comma in rule', ''
        stopCode = [Parser.COMMA]

        # add everything so far to the transformation
        while tokenList[currentPosition].code not in stopCode:
            tmpIsValid, tmpTransformation, tmpLookup, tmpCurrentPosition = self.getRoundedValue(tokenList, currentPosition, stopCode)
            if tmpIsValid:
                transformation += tmpTransformation
                lookup += tmpLookup
                currentPosition = tmpCurrentPosition
            else:
                return tmpIsValid, tmpTransformation, lookup
        transformation += roundKeywordList[1]
        transformation += tokenList[currentPosition].name # the comma
        currentPosition += 1

        if tokenList[currentPosition].code == Parser.NUMLIT:
            transformation += tokenList[currentPosition].name # the integer
            currentPosition += 1
        else:
            return isValid, 'Length must be an integer value.', ''

        transformation += keyWordEnd
        isValid = True
        return isValid, transformation, lookup


    def _keyAgg(self, agg, token, fakeKeyword = False):
        ''' in.fld
           aggKeyword(in.fld)
        but also
           count(distinct(in.imsi))
        '''
        tokenList = self.parser.getTokens(token.name)
  
        if(agg=='sum'):
            keyWordStart = 'sum('
            keyWordEnd = ')'
            transformation = ''
            isValid=False
            curPos=0
            usedTokens, tokenList = self.grammar.handleStarter(tokenList, curPos, False) # avoid unpleasant side effects
            if usedTokens < 1:
                return isValid, 'Error detected.', ''
                curPos += usedTokens
            transformation += keyWordStart
            lookup = ''
            currentPosition = 0
            stopCode = [Parser.EMPTY]
            # add everything so far to the transformation
            while tokenList[currentPosition].code not in stopCode:
                tmpIsValid, tmpTransformation, tmpLookup, tmpCurrentPosition = self.getRoundedValue(tokenList, currentPosition, stopCode)
                if tmpIsValid:
                    transformation += tmpTransformation
                    lookup += tmpLookup
                    currentPosition = tmpCurrentPosition
                else:
                    return tmpIsValid, tmpTransformation, lookup
            transformation += keyWordEnd
            isValid = True
            self._isAgg = True
            return isValid, transformation, lookup 


        if len(tokenList) > 3:
            txt = 'Invalid format for %s(). Expected %s(in.fld) but found extra token >%s<.'%(agg,agg, tokenList[2].name)
            return False, txt

        if agg == 'count' and tokenList[0].code == Parser.KEYWRD:

            isAgg, txt = self._keyAgg(tokenList[0].name, tokenList[1])
            if isAgg:
                txt = 'count('+txt+')'
                return True, txt
            else:
                return isAgg, txt


        curPos = 0
        usedTokens = self.grammar._handleField(tokenList, curPos, False)
        if usedTokens < 2:
            txt = 'Invalid format for %s(). Expected %s(in.fld)'%(agg,agg)
            return False, txt


        if not fakeKeyword:
            txt = agg+'(' + tokenList[0].name + tokenList[1].name + ')'


        else: # 'unique' is  a fake keyword that does not change the transform

            txt = tokenList[0].name + tokenList[1].name
        self._isAgg = True
        return True, txt

    def _handleComparitor(self, tokenList, txt, curPos):
        isValid = False
        if tokenList[curPos].code != Parser.COMPARE or tokenList[curPos].name not in ['=', '!=']:
            txt = 'Invalid format for lookup. Expected in.fld = lookup.key'
        else:
            isValid = True
            txt += tokenList[curPos].name
            curPos += 1

        return isValid, txt, curPos

    def _handleSide(self, tokenList, txt, curPos):
        isValid = False
        if tokenList[curPos].code == Parser.PREFIX:
            usedTokens = self.grammar._handleField(tokenList, curPos, False)
            if usedTokens < 2:
                txt = 'Invalid format for lookup. Expected lookup( lookupTable, return_fld, in.fld1 = lookup.key1, IN.fld2 = lookup.key2)'
                return isValid, txt, 0
            else:
                txt += tokenList[curPos].name + tokenList[curPos+1].name
                curPos += usedTokens

        elif tokenList[curPos].code == Parser.LOOKUP:
            txt += tokenList[curPos].name + tokenList[curPos+1].name
            curPos += 2
        elif tokenList[curPos].code in Parser.literalCodes:
            txt += tokenList[curPos].name
            curPos += 1
        else:
            txt = 'Invalid format for lookup. Expected lookup( lookupTable, return_fld, in.fld1 = lookup.key1, IN.fld2 = lookup.key2)'
            return isValid, txt, 0
        isValid = True

        return isValid, txt, curPos

    def _getLeftOfComapritor(self, tokenList, curPos, maxPos):
        lookup = ''

        tempTransformation = ''

        while curPos < maxPos:
            if tokenList[curPos].code == Parser.KEYWRD :
                tmpIsValid, txt, tmpLookup, tmpcurPos = self.processKeyWord(tokenList, curPos)
                if tmpIsValid:
                    tempTransformation += txt
                    lookup += tmpLookup
                    curPos = tmpcurPos
                else:
                    return tmpIsValid, txt
            else:
                tempTransformation += tokenList[curPos].name
                curPos += 1

        return True, curPos, tempTransformation, lookup

    # only called from getDefault
    def _getComparitor(self, tokenList, currentPosition):
        # handles = null and != null and converts them to is null and is not null
        isValid = True

        token1 = tokenList[currentPosition]
        token2 = tokenList[currentPosition + 1]

        txt = ''
        if token1.name == '=' and token2.code == Parser.NULL:
            txt = ' is null '
        elif token1.name == '!=' and token2.code == Parser.NULL:
            txt = ' is not null '
        elif token1.code == Parser.COMPARE:
            txt = ' ' + token1.name
        else:
            isValid = False
            return isValid, 0, 'Expected Comparator'

        return isValid, currentPosition+1, txt

    def _getLiteral(self, tokenList, curPos):
        if tokenList[curPos].code == Parser.NUMLIT or tokenList[curPos].code == Parser.STRLIT or tokenList[curPos].code == Parser.FLOAT:
            txt = tokenList[curPos].name
            return True, txt
        return False, 'Not a valid literal'

    def _getRightOfComparitor(self, tokenList, maxLength, curPos):
        # it can only be be [minus]num, [minus]float or str.

        if tokenList[curPos].name == '-' and curPos < maxLength and (tokenList[curPos+1].code == Parser.NUMLIT or tokenList[curPos+1].code == Parser.FLOAT):
            return True, curPos +3, ' -'+tokenList[curPos+1].name

        if tokenList[curPos].code == Parser.NUMLIT or tokenList[curPos].code == Parser.STRLIT or tokenList[curPos].code == Parser.FLOAT:
            return True, curPos +2, ' '+ tokenList[curPos].name

        return False, None, 'Default must contain a number or text after the test'

    def _getAnyValue(self, tokenList, currentPosition, maxLength, stopCodes):
        ''' only used by default() '''
        isValid = True
        transformation = ''
        lookup = ''

        while currentPosition < maxLength and tokenList[currentPosition].code not in stopCodes:
            if tokenList[currentPosition].code == Parser.KEYWRD and currentPosition < maxLength -1 :
                tmpIsValid, txt, tmpLookup, tmpCurrentPosition = self.processKeyWord(tokenList, currentPosition)
                if tmpIsValid:
                    transformation += txt
                    lookup += tmpLookup
                    currentPosition = tmpCurrentPosition
                else:
                    return tmpIsValid, txt, '', 0
            else:
                transformation += tokenList[currentPosition].name
                currentPosition += 1
        return isValid, transformation, lookup, currentPosition

    def getValue(self, tokenList, currentPosition, stopCodes):
        ''' only used by substring '''
        isValid = True

        transformation = ''
        lookup = ''

        if tokenList[currentPosition].code in stopCodes:
            transformation = tokenList[currentPosition].name
            currentPosition += 1
        else:
            if tokenList[currentPosition].code == Parser.KEYWRD:
                isValid, transformation, lookup, currentPosition = self.processKeyWord(tokenList, currentPosition)
            else:
                transformation += tokenList[currentPosition].name
                currentPosition += 1

        return isValid, transformation, lookup, currentPosition

    def getRoundedValue(self, tokenList, currentPosition, stopCodes):
        ''' only used by Round '''
        isValid = True
        transformation = ''
        lookup = ''

        if tokenList[currentPosition].code in stopCodes:
            transformation = tokenList[currentPosition].name
            currentPosition += 1
        else:
            if tokenList[currentPosition].code == Parser.KEYWRD:
                isValid, transformation, lookup, currentPosition = self.processKeyWord(tokenList, currentPosition)
            elif tokenList[currentPosition].code == Parser.BRKTS:
                isValid, transformation,lookup = self._handleBrackets(tokenList[currentPosition])
                currentPosition += 1
            else:
                transformation += tokenList[currentPosition].name
                currentPosition += 1

        return isValid, transformation, lookup, currentPosition

    def processKeyWord(self, tokenList, currentPosition):
        isValid = True

        token1 = tokenList[currentPosition]
        token2 = tokenList[currentPosition+1]

        tmpIsValid, transformation, lookup = self.keyMethods[token1.name](token1, token2)
        if  not tmpIsValid:
            transformation = 'recursive keyword failure'
            isValid = False

        currentPosition += 2

        return isValid, transformation, lookup, currentPosition

    def getCommaPosition(self, tokenList, curPos):
        while curPos < len(tokenList) - 1 and tokenList[curPos].code != Parser.COMMA :
            curPos += 1
        if curPos >= len(tokenList) -1: # there has to be something after the comma
            return False, ' Missing value argument'

        return True, curPos

    def getComparitorPosition(self, tokenList, curPos, maxPos):

        while curPos < maxPos - 1 and tokenList[curPos].name not in Parser.comparitor:
            curPos += 1
        if curPos >= maxPos -1: # there has to be something after the comparitor
            return False, ' Missing comparator'
        return True, curPos

    def _handleBrackets(self, token):
        bracketStart = '('
        bracketEnd = ')'
        transformation = ''
        lookup = ''

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

        transformation += bracketStart

        currentPos = 0
        stopCode = [Parser.EMPTY]

        # add everything so far to the transformation
        while tokenList[currentPos].code not in stopCode:
            tmpIsValid, tmpTransformation, tmpLookup, tmpCurrentPosition = self.getRoundedValue(tokenList, currentPos, stopCode)
            if tmpIsValid:
                transformation += tmpTransformation
                lookup += tmpLookup
                currentPos = tmpCurrentPosition

            else:
                return tmpIsValid, tmpTransformation, lookup

        if curToken < 0:
            return isValid
        transformation += bracketEnd

        isValid = True
        return isValid,transformation,lookup


def keyTest(keyTxt, argsTxt):
    token1 = Parser.TokenType()
    token1.code = Parser.KEYWRD
    token1.name = keyTxt

    token2 = Parser.TokenType()
    token2.code = Parser.BRKTS
    token2.name = argsTxt

    retVal, txt, lookup = keywords.keyMethods[token1.name](token1, token2)
    if retVal:
        print 'Pass: %s(%s) Transform: %s, Lookup: %s'%(token1.name, token2.name, txt, lookup)
    else:
        print 'Fail: %s(%s)\n Error: %s'%(token1.name, token2.name, txt)

if __name__ == '__main__':
    testText='''default(in.a == null, 0)
'''
    aliasDict = {}

    import grammar as Grammar
    grammar = Grammar.Grammar(testText, aliasDict)
    keywords = keywords()
    keywords.setGrammar(grammar)

    kyList = keywords.getKeywords()
    print kyList

    print keyTest('default','in.abc = null, 0')

    keyTest( 'default', 'in.a = (6 - 5) *6, 5')

    keyTest('substring','in.a, 3, 1')
    keyTest('substring', 'in.a, 3')

    keyTest('default', 'default(in.abc != null, 0) > 1, 1')

    keyTest('substring','substring(in.a,3,4),4')


    keyTest('lookup', 'DIM_RNC, nodename, in.nodeId') # test use of default field

    keyTest('lookup','DIM_RNC, nodename, in.nodeId = lookup.rncId')
    keyTest('lookup','DIM_RNC, nodename, in.nodeId = lookup.rncId, in.fld2=lookup.fld2')

    keyTest('lookup','dim_e_test, rnc_name, in.col2 = 1.333, lookup.rnc_id=1')
    keyTest('lookup','dim_e_test, rnc_name, 1.333 = col2, lookup.rnc_id=1')
    keyTest('lookup','dim_e_test, rnc_name, 1.333 = col2, in.rnc_id=1')
    keyTest('lookup','dim_e_test, rnc_name, 1.333 = lookup.col2, 1=lookup.rnc_id')
    keyTest('lookup','DIM_RNC, nodename, substring(in.a, 3, 4) = lookup.rncId')
    keyTest('lookup','DIM_RNC, nodename, substring(in.a, 3, 4) | substring(in.a, 1, 2)= lookup.rncId')
    keyTest('lookup','DIM_RNC, mcc, substring(in.gummei, 4, 1) | substring(in.gummei, 3, 1) | substring(in.gummei, 2, 1) = lookup.mcc')
    keyTest('lookup','DIM_RNC, nodename, in.a / 256 = lookup.NodeId')
    keyTest('default','lookup(dim_e_mccmnc_test, mnc, in.mnc2 = lookup.mnc, in.mcc=lookup.mcc) = null, lookup(dim_e_mccmnc_test, mnc, in.mnc3 = lookup.mnc, in.mcc=lookup.mcc)')
    keyTest('distinct','in.nodeId')
    keyTest('count','distinct(in.imsi)')
    keyTest('count','in.a')
    keyTest('lookup','DIM_RNC, nodename, in.nodeId')
    keyTest('cast','in.a')
    keyTest('pad','"0", 3, in.a')
    keyTest('lookup','DIM_RNC, nodename, in.nodeId = pad("0",3,lookup.rncId)')
    keyTest('padright','"0", 3, in.a')
    keyTest('lookup','DIM_RNC, nodename, in.nodeId = padright("0",3,lookup.rncId)')
