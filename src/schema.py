# classes involved in parsing/ processing a dash10
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
class Field:
    def __init__(self, fieldName, fieldType, fieldLen, offset, dbName, isVarLenParam,isValidBit,isOptional, seqNum, instNum, lenbits):
        self.fieldName = fieldName # name from 10dash 
        self.dbName = dbName       # shortend name in db  
        self.fieldType = fieldType # 
        self.fieldLen = fieldLen   # in bytes - 0 means variable len
        self.offset = offset       # offset from start of event
        self.isVarLenParam = isVarLenParam  # is the feild of variable length 
        self.isValidBit = isValidBit        # is the field (ie.uses valid bit)
        self.isOptional=isOptional
        self.seqNum = seqNum # number of the sequence struct this field belongs to or zero
        self.instNum = instNum # which instance in the sequence
        self.lengthbits = lenbits # the lenght of BYTEARRAY and DNSNAME fields

class Seq:
    def __init__(self, cnt):
        self.cnt = cnt
        self.fields = []
        
    def add(self, field):
        self.fields.append(field)
          
                
class Header:
    ffv = ''
    fiv = '' #  used by GPEH and older LTE nodes
    fiv1 = ''
    fiv2 = ''
    feature='Unset'
    lenInBytes = False
    lenInBits = False
    recordLengthBits = 0
    recordTypeBits = 0
    eventIdBits = 0
    evtIdOffset = 0
    typeValueForEventRecord = 1
    tablePrefix = 'aTable' 
         
    
class Event:  
    #eventName = ''
    #eventId = 0
    #msgLen = 0
    #varLen = False
    #self.fields = [] # will be Fields()
    def __init__(self, eventName, eventId):
        self.eventName = eventName
        self.eventId = eventId
        self.fields = []

    def set(self, msgLen, varLen):
        self.msgLen = msgLen
        self.varLen = varLen
    
    def addField(self, field):
        dbName = field.dbName
        if not dbName[0].isalpha():  # sql column names must start with an alpha            
            dbName = 'a'+dbName
        
        if not dbName.isalnum(): # and be made of alpha numerics
            raise Exception('Invalid field name detected: %s'%dbName) 
            
        #
        # the dbName could appear more then once when structures are used
        # if so, we need to dedup it.
        found = False
        for f in self.fields:
            if f.dbName == dbName: 
                found=True
                break
        if found:
            dbName = self._dedup(dbName)
        field.dbName = dbName
        self.fields.append(field)

    def _dedup(self, dbName):
        found = False
        i = 1
        name = '%s_%d'%(dbName, i)
        while True:
            for f in self.fields:
                if f.dbName == name:
                    found = True 
                    break
            if found:
                name = '%s_%d'%(dbName, i)
                i += 1
                found = False
            else :
                break
        return name
    

def typeUint(flen):
    return 'bigint NULL'
    
def typeEnum(flen):
    return 'bigint NULL'
    
def typeLong(flen):
    return 'bigint NULL'

def typeIPv4(flen):
    return 'binary(4) NULL'

def typeIPv6(flen):
    return 'binary(16) NULL'

def typeDNS(flen):
    return 'varchar(101) NULL'

def typeByteA(flen):
    return 'varchar(100) NULL'

def typeBin(flen):
    # flen is in bits. We need bytes
    ll = flen /8
    if flen %8 != 0:
        ll += 1
    
    if ll == 0 or ll > 256: # handle varlen and excessivly long fields
        ll = 256        
    return 'varchar(%d) NULL'%(ll*2) # data stored as hex so twice as long 
 
def typeStr(flen):
    # flen is in bits. We need bytes
    ll = flen /8
    if flen %8 != 0:
        ll += 1
    if ll == 0 or ll > 256: # handle varlen and excessivly long fields
        ll = 256
    return 'varchar(%d) NULL'%(ll*2) 

#methods for case statement
rawTypes = {'UINT':typeUint, 
            'ENUM':typeEnum, 
            'LONG':typeLong,
            'FROREF':typeBin,
            'BINARY':typeBin,
            'STRING':typeStr,
            'IPADDRESS':typeIPv4,
            'IPADDRESSV6':typeIPv6,
            'TBCD':typeBin,
            'IBCD':typeBin,
            'BCD':typeBin,
            'DNSNAME':typeDNS,
            'BYTEARRAY':typeByteA}

import sys
import gzip
import pickle     
class Schema:
    def __init__(self, header):
        self.source = header
        self.events = []
        
    def addEvent(self, event):
        self.events.append(event)
         
    def persistSchema(self, fileName):
        try:
            with gzip.open(fileName+'.gz', 'wb') as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        except:
            raise ("failed to write schema file: %s", fileName) 
            
    def writeSchemaAsText(self, fileName):
        ''' Pretty(ish) human readable format
        '''        
        with open(fileName, 'w') as f:
            f.write('source: %s, feature %s, table Prefix %s\n'%(self.source, self.header.feature, self.header.tablePrefix) )
            f.write(' ffv: %s\n fiv: %s, fiv1: %s, fiv2: %s\n'%(self.header.ffv, self.header.fiv, self.header.fiv1, self.header.fiv2))
            f.write(' numEvents %d\n'%len(self.events))
            for event in self.events:
                f.write('  id: %4s, numFields %3d, msgLen: %4d, varLen: %5s, name: %s\n'%(event.eventId, len(event.fields), event.msgLen, ' true' if event.varLen else 'false', event.eventName))
                for fe in event.fields:
                    txt = ('   off: %5d len: %4d, Var %5s, Val %5s, Opt %5s, Seq %2d-%02d, type %s, name %s, dbName %s \n'%
                           (fe.offset, fe.fieldLen, fe.isVarLenParam, fe.isValidBit, fe.isOptional, fe.seqNum, fe.instNum,
                            fe.fieldType, fe.fieldName, fe.dbName ))
                    
                    f.write(txt)  
   
        return

    def writeSchemaAsStruct(self, fileName):
        ''' To be read by Java class - schema.java        
        '''        
        with open(fileName, 'wb') as f:
            # write file identification record
            f.write('H,%d,%s,%d,%s,%s,%s, %s\n'%(1,self.source,len(self.events),self.header.ffv, self.header.fiv1, self.header.fiv2, self.header.tablePrefix) ) 
            for event in self.events:
                f.write('E,%s,%d,%d,%s,%s\n'%(event.eventId, len(event.fields), event.msgLen, 'T' if event.varLen else 'F', event.eventName))
                for fe in event.fields:
                    f.write('F,%d,%d,%s,%s,%s,%s,%s,%d,%d\n'%(fe.offset, fe.fieldLen, fe.fieldType, fe.fieldName, fe.dbName, fe.isVarLenParam, fe.isValidBit,fe.seqNum, fe.instNum ))     
        return
    
    def getEvent(self, eventId):        
        for event in self.events:
            if event.eventId == eventId:
                return event
                    
        print 'Event ID %d not found in schema!'%eventId
        return None
        
    
    def createDBtable(self, tableNamePrefix):
        ''' create a table in the db for each event type in the schema
        '''
        biggestEvt = ''
        longestEvent = ''
        numInBiggestEvt = 0
        lenOfLongestEvt = 0
        numEvts = 0
         
        sqlStmt = ''
        for event in self.events:
            sqlStmt += 'drop table if exists %s_%d;\n'%(tableNamePrefix, event.eventId)
            sqlStmt += 'create table %s_%d\n ( gritEVENTID INTEGER,\n '%(tableNamePrefix, event.eventId)
            fList = []
            numInCurrentEvt = 0
            numEvts += 1
            for field in event.fields:
                numInCurrentEvt +=1                 
                st = ' ' + field.dbName + ' '
                try :
                    st += rawTypes[field.fieldType](field.fieldLen)
                except:
                    e = sys.exc_info()[0]
                    print 'Exception : Unsupported field type >%s<\n'%(field.fieldType), e 
                    st += 'varchar(%d) -- Unsupported field type >%s<\n'%(field.fieldLen, field.fieldType)
                     
                fList.append(st)
            if numInCurrentEvt > numInBiggestEvt:
                numInBiggestEvt = numInCurrentEvt
                biggestEvt = event.eventId
            if event.msgLen > lenOfLongestEvt:
                lenOfLongestEvt = event.msgLen
                longestEvent = event.eventId
            sqlStmt += ',\n'.join(sorted(fList))        
            sqlStmt += ');\n'
     
        print 'Out of %d events, the biggest event is %s which has %d fields. The longest event is %s which is up to %d bits.'%(numEvts, biggestEvt, numInBiggestEvt, longestEvent, lenOfLongestEvt)
        return sqlStmt   

class ParameterType:
    def __init__(self):
        self.param = {}
        
    def addParam(self, name, pType, pLen , isVarLenParam, useValid, lenBits):
        self.param[name] = (pType, pLen, isVarLenParam, useValid, lenBits)
    
    def getParam(self, name):
        return self.param[name]


def loadSchema(fileName):
    inFile = None
    if not fileName.endswith('.gz'):
        fileName += '.gz'
        
    try: 
        inFile = gzip.open(fileName, 'rb')
        mySchema = pickle.load(inFile)
        inFile.close()
    except:
        print 'Unable to load specified Schema file >%s<. Please check it exists and you have permission to read it.' % fileName
        sys.exit(4)
    return mySchema

if __name__ == '__main__':        
    print 'This class is not directly runnable.'
    