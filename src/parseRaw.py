''' Read and parse raw data to produce SQL insert statements
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

import sys
import schema
import datetime

#TODO sort this!
# bitstring is python 2.7+ but we are stuck using jython 2.5.3!
from bitstring import BitArray

def convInt(bitArray):
    if (bitArray):
        return '%d' % bitArray.uint
    else:
        return '0'


def convBin(bitArray):
    # return byteArray.decode(encoding='UTF-8')
    if (bitArray):
        try:
            return "'" + bitArray.hex+"'"
        except : # the above fails if not a multiple of 4 bits
            lb = len(bitArray)
            value = ''
            for index in range(4, lb, 4):
                nibble = bitArray[index-4:index].uint
                value += '%X'%(nibble)
            nibble = 0
            for index in range(index, lb, 1):
                nibble *=2
                nibble += bitArray[index]
            value += '%X'%nibble

            return "'"+value+"'"

#             ll = len(bitArray)
#             if ll % 4 != 0:
#                 ll = ll - (ll %4) # reduce to nearest multiple of 4 bits
#                 ba = bitArray[:ll]
#                 return "'" + ba.hex+"'"
#             raise
    else:
        return 'null'

# check if this is correct
# I think it should be "'"+bitArray.bytes+"'" but need data to test it
def convStr(bitArray):
    if (bitArray):
        return "'" + str(bitArray.bytes) + "'"
    else:
        return 'null'

def convByteA(bitArray):
    if (bitArray):
        return "'" + str(bitArray.bytes)[:100] + "'"
    else:
        return 'null'

def convDNS(bitArray):
    if (not bitArray):
        return 'null'
    name = str(bitArray.bytes)

    parts = []
    i = 0
    while i < len(name):
        length = ord(name[i])
        parts.append(name[i+1:i+1+length])
        i += 1 + length
    return "'" + ".".join(parts) + "'"

# check if this is correct
def convIBCD(bitArray):
    if (bitArray):
        bcd = bitArray.hex
        return "'"+bcd[::-1]+"'"
    else:
        return 'null'


# check if this is correct
def convTBCD(bitArray):
    # * IMSI type=TBCD, 64 bits
    #
    # 5-15 digits, TBCD (Telephony Binary Coded Decimal), each digit represented by 4 bits.
    # Padded with '1111' for each unused digit upto a total length of 8 octets/16 digits.
    # For more information see:3GPP TS 23.003 (ch 2.2) for the composition and TS 29.060 (ch 7.7.2) for the coding.
    # Some fuckwit decided to reverse the order of the nibbles so 12345 would be 21 43 f5.
    if bitArray:
        if len(bitArray) %4 != 0:
            padd = 4 - len(bitArray) %4
            print 'How did we end up here?', len(bitArray)
            bitArray = bitArray[:len(bitArray) - padd]
        imsiH = bitArray.hex

        i = 0 # skip the leading 0x
        imsi = '' # some fuckwit thought it would be fun to reverse the nibbles
        while i < len(imsiH) : # and the traling L
            try:
                imsi += imsiH[ i + 1 if (i % 2 == 0) else i - 1]
            except IndexError:
                imsi += imsiH[i]
            i+=1
        # now remove any padding
        padding_start_pos = imsi.find('f')
        if padding_start_pos > 0:
            imsi = imsi[:padding_start_pos]
        return "'"+imsi+"'"
    else:
        return 'null'

def convIPv4(bitArray):
    if (bitArray):
        ip = bitArray.uint
        return "0x%02x%02x%02x%02x"% ( (ip >> 24) &0xff, (ip >> 16) &0xff, (ip >> 8) &0xff, (ip &0xff) )
        # return "'%d.%d.%d.%d'"% ( (ip >> 24) &0xff, (ip >> 16) &0xff, (ip >> 8) &0xff, (ip &0xff) )
    else:
        return 'null'

def convIPv6(bitArray):
    if (bitArray):
        ip = bitArray.uint # pretty sure I am going to need two uints :)
        #return "'%x:%x:%x:%x:%x:%x:%x:%x'"% (
        return "0x%04x%04x%04x%04x%04x%04x%04x%04x"% (
            (ip >> 112) &0xffff,
            (ip >> 96) &0xffff,
            (ip >> 80) &0xffff,
            (ip >> 64) &0xffff,
            (ip >> 48) &0xffff,
            (ip >> 32) &0xffff,
            (ip >> 16) &0xffff,
            ip&0xffff)
    else:
        return 'null'


# methods for case statement
rawConv = {'UINT':convInt,
            'ENUM':convInt,
            'LONG':convInt,
            'FROREF':convBin,
            'BINARY':convBin,
            'STRING':convStr,
            'IPADDRESS':convIPv4,
            'IPADDRESSV6':convIPv6,
            'TBCD':convTBCD,
            'IBCD':convIBCD,
            'BCD':convBin,
            'DNSNAME':convDNS,
            'BYTEARRAY':convByteA,}


class parser(object):
    '''

    '''
    # schema = schema.Schema()

    def __init__(self, schema):
        self.schema = schema
        self.oldEvtId = ''
        self.oldLenBody = 0
        self.insertSize = 0
        self.isCTRS = False
        if self.schema.header.feature == 'CTRS':
            self.isCTRS = True

    def decodeField(self, bitArray, offset, field, nvl, evtId):
        # bitArray - the data source
        # offset - the current offset into the data
        # field - the schema entry for this field
        # nvl - length of this varlen field
        # returns value to be used in SQL insert statement and offset to start of next field
        # isOpt bit is in addition to the field length
        # isValid bit is included in the length for CTRS only
        #
        value = -1
        if field.isOptional or field.isValidBit:
            if offset > len(bitArray):
                print 'oops!'
            inValidBit = bitArray[offset] # set if value is one
            offset += 1
            fldLen = field.fieldLen
            if self.isCTRS:
                offset -= 1
                if inValidBit == 1: # invalid bit is set
                    offset += fldLen
                    value = 'null'
                else:
                    value, offset = self._getVal(field, bitArray, offset, fldLen)

            if not self.isCTRS:
                if inValidBit == 0:
                    if field.fieldType == 'DNSNAME' or field.fieldType == 'BYTEARRAY':
                        lenArray = bitArray[offset :offset + field.lengthbits].uint
                        offset = offset + field.lengthbits
                        # byte align
                        padd = 0
                        if ((offset % 8)) > 0 :
                            padd = 8 - (offset % 8)
                        offset += padd
                        ff = bitArray[offset :offset + (lenArray * 8) ] # lenArray in bytes not bits!
                        value = rawConv[field.fieldType](ff)
                        offset += (lenArray * 8)
                    else:
                        ff = bitArray[offset :offset + fldLen ]
                        value = rawConv[field.fieldType](ff)
                        offset += fldLen
                else:
                    value = 'null'
                    if not field.isOptional:
                        offset += fldLen

        else:
            # deal with possibilty of crap data from EDE etc.
            endPoint = offset + field.fieldLen + nvl
            if endPoint > len(bitArray):
                print 'Out of buffer! Current offset is',offset, 'Requested len is', endPoint-offset, 'buffer len is ', len(bitArray),
                print 'EvtId is ',evtId, ', Field is ',field.dbName, 'Field offset is ', field.offset
                #raise Exception("Ran out of buffer!")
                # or
                endPoint = len(bitArray) -1

            if field.fieldType == 'DNSNAME' or field.fieldType == 'BYTEARRAY':
                lenArray = bitArray[offset :offset + field.lengthbits].uint
                offset = offset + field.lengthbits
                # byte align
                padd = 8 - (offset % 8)
                if padd < 8:
                    offset += padd
                ff = bitArray[offset :offset + (lenArray * 8) ]
                value = rawConv[field.fieldType](ff)
                offset += (lenArray * 8)
            else:
                ff = bitArray[offset : endPoint]
                value = rawConv[field.fieldType](ff)
                offset = endPoint
        return value, offset

    def _getVal(self, field, bitArray, offset, fldLen):
        if field.fieldType == 'DNSNAME' or field.fieldType == 'BYTEARRAY':
            lenArray = bitArray[offset :offset + field.lengthbits].uint
            offset = offset + field.lengthbits
            # byte align
            padd = 8 - (offset % 8)
            offset += padd
            ff = bitArray[offset :offset + (lenArray * 8) ] # lenArray in bytes not bits!
            value = rawConv[field.fieldType](ff)
            offset += (lenArray * 8)
        else:
            ff = bitArray[offset :offset + fldLen ]
            value = rawConv[field.fieldType](ff)
            offset += fldLen
        return value, offset

    def parseEvent(self, eventId, bitArray, offset):
        ''' Given an event id and a byte array, produce a SQL insert statement
        '''
        # When sequence blocks are used, there may be different fields
        # so we can not concat values in that case.
        repeatsInUse = False

        sqlStmt = ''
        lastField = ''
        curSequence = -1
        txt = ''
        try:
            head = []
            body = []

            event = self.schema.getEvent(eventId)
            if event == None:
                return ''
            nvl = 0 # length of next field if it is varlen

            repeatedFields = []
            repeatCount = 0
            for field in event.fields:
                lastField = field
                if curSequence > 0 and field.seqNum != curSequence: # reached the end of a sequence
                    inst = 0
                    nxtFld = 0
                    repeatedField = repeatedFields[nxtFld]
                    for _ in range(repeatCount):
                        while repeatedField.instNum == inst:
                            head.append(repeatedField.dbName)
                            value, offset = self.decodeField(bitArray, offset, repeatedField, nvl, eventId)
                            body.append(value)
                            nxtFld += 1
                            if nxtFld >= len(repeatedFields): # deal with fucked up repeat counts
                                break
                            repeatedField = repeatedFields[nxtFld]
                        inst += 1
                    curSequence = -1
                if field.seqNum != 0: # start a new sequence
                    if field.seqNum != curSequence:  # Start a new sequence
                        curSequence = field.seqNum
                        repeatCount = bitArray[offset:offset + 8].uint
                        offset = offset + 8
                        if repeatCount  >127:
                            repeatCount = 0
                        repeatedFields = [] # there can be more then one sequence
                    repeatedFields.append(field)
                    continue # nothing else to do until end of sequence
                # not in a sequence
                head.append(field.dbName)
                value, offset = self.decodeField(bitArray, offset, field, nvl, eventId)
                body.append(value)
                #if field.dbName == 'EVENTID' and value != eventId:
                #    bits = bitArray[0:96].bytes
                #    print 'reported EventId is', eventId,' calculated enevt Id is', value, bits
                if field.fieldName == 'L3MESSAGE_LENGTH' or field.fieldName == 'MESSAGE_LENGTH':
                    try:
                        nvl = int(value)
                    except:
                        nvl = 0
                    nvl *= 8 # is always in bytes
                    # From p88 GPEH_RNC
                    # "The parameter EVENT_PARAM_MESSAGE_LENGTH gives the length in bytes of the ASN.1
                    #  coded message given in EVENT_PARAM_MESSAGE_CONTENTS."
                txt += "'"+field.dbName+"': " + value+',\n'

            if eventId != self.oldEvtId or repeatsInUse or len(body) != self.oldLenBody: # merge insert statements if possible
                sqlStmt = ';\ninsert into %s_%d' % (self.schema.header.tablePrefix, eventId)
                sqlStmt += ' (gritEVENTID,'+','.join(head) + ') Values '
                sqlStmt += '\n (%d,'%eventId
                sqlStmt += ','.join(body) + ')'
                self.oldEvtId = eventId
                self.oldLenBody = len(body) # handle optional fields
                self.insertSize = 0
                repeatsInUse = 0
            else:
                sqlStmt += ',\n (%d,'%eventId
                sqlStmt += ','.join(body) + ')'
            # prevent insert statements from becoming excessivily large
            self.insertSize += len(sqlStmt)
            if self.insertSize > 8000:
                self.oldEvtId = ''


        except:
            print 'failed to parse event with Id: %d' % eventId
            if lastField:
                print 'last field was %s'%lastField.dbName
            # We should abort at this point
            raise
        return sqlStmt

    def newparseEvent(self, eventId, bitArray, offset):
        ''' Given an event id and a byte array, produce the key and value for a SQL insert statement
        '''
        # When sequence blocks are used, there may be different fields
        # so we can not concat values in that case.
        lastField = ''
        curSequence = -1
        txt = ''
        try:
            head = []
            body = []
            body.append('%d'%eventId)

            event = self.schema.getEvent(eventId)
            if event == None:
                return ''
            nvl = 0 # length of next field if it is varlen

            repeatedFields = []
            repeatCount = 0
            for field in event.fields:
                lastField = field
                #Warning : The same block of code is repeated below
                # to handle the cases where Sequence parameters are
                # the last one in the 10 dash document
                if curSequence > 0 and field.seqNum != curSequence: # reached the end of a sequence
                    inst = 0
                    nxtFld = 0
                    repeatedField = repeatedFields[nxtFld]
                    for _ in range(repeatCount):
                        while repeatedField.instNum == inst:
                            head.append(repeatedField.dbName)
                            value, offset = self.decodeField(bitArray, offset, repeatedField, nvl, eventId)
                            body.append(value)
                            nxtFld += 1
                            if nxtFld >= len(repeatedFields): # deal with fucked up repeat counts
                                break
                            repeatedField = repeatedFields[nxtFld]
                        inst += 1
                    curSequence = -1
                if field.seqNum != 0: # in a new sequence
                    if field.seqNum != curSequence:  # Start a new sequence
                        curSequence = field.seqNum
                        repeatCount = bitArray[offset:offset + 8].uint
                        offset = offset + 8
                        if repeatCount  >127:
                            repeatCount = 0
                        repeatedFields = [] # there can be more then one sequence
                    repeatedFields.append(field)
                    continue # nothing else to do until end of sequence
                # not in a sequence
                head.append(field.dbName)
                value, offset = self.decodeField(bitArray, offset, field, nvl, eventId)
                body.append(value)
                #if field.dbName == 'EVENTID' and value != eventId:
                #    bits = bitArray[0:96].bytes
                #    print 'reported EventId is', eventId,' calculated enevt Id is', value, bits
                if field.fieldName == 'L3MESSAGE_LENGTH' or field.fieldName == 'MESSAGE_LENGTH':
                    try:
                        nvl = int(value)
                    except:
                        nvl = 0
                    nvl *= 8 # is always in bytes
                    # From p88 GPEH_RNC
                    # "The parameter EVENT_PARAM_MESSAGE_LENGTH gives the length in bytes of the ASN.1
                    #  coded message given in EVENT_PARAM_MESSAGE_CONTENTS."
                txt += "'"+field.dbName+"': " + value+',\n'

            #Warning above
            if curSequence > 0: # reached the end of a sequence
                inst = 0
                nxtFld = 0
                repeatedField = repeatedFields[nxtFld]
                for _ in range(repeatCount):
                    while repeatedField.instNum == inst:
                        head.append(repeatedField.dbName)
                        value, offset = self.decodeField(bitArray, offset, repeatedField, nvl, eventId)
                        body.append(value)
                        nxtFld += 1
                        if nxtFld >= len(repeatedFields): # deal with fucked up repeat counts
                            break
                        repeatedField = repeatedFields[nxtFld]
                    inst += 1
                curSequence = -1

            key = '%s_%d  (gritEVENTID,' % (self.schema.header.tablePrefix, eventId) + ','.join(head) + ')'
            data = '(' + ','.join(body) + ')'

        except:
            print 'failed to parse event with Id: %d' % eventId
            if lastField:
                print 'last field was %s'%lastField.dbName
            # We should abort at this point
            raise
        return key, data

    def parseFile(self, inFile, outFile, verbose, maxRec = -1):

        recCnt = 0 # reco0rds in raw table
        insrtCnt = 0 #
        sqlFile = open(outFile, 'w')
        sqlFile.write('-- created by Grit parseRaw from %s on %s\n'%(inFile, datetime.datetime.now()))
        sqlFile.write('-- using %s schema ffv %s, fiv %s, %s, %s\n'%(self.schema.header.feature, self.schema.header.ffv, self.schema.header.fiv, self.schema.header.fiv1, self.schema.header.fiv2))
        sqlFile.write('select 1; -- syntactic glue required to ensure correct behaviour\n')
        inValidCnt = 0 # number of invalid GPEH events
        insertDict = {}

        # Handle compressed files
        if inFile.endswith('.gz') :
            import gzip
            byteList = gzip.open(inFile, 'rb').read()
        else:
            byteList = open(inFile, 'rb').read()
        raw = BitArray(bytes=byteList)

        size = len(raw)
        offset = 0;
        feature = self.schema.header.feature
        typeValueForEventRecord = self.schema.header.typeValueForEventRecord
        recordLengthBits = self.schema.header.recordLengthBits
        recordTypeBits = self.schema.header.recordTypeBits
        eventIdBits = self.schema.header.eventIdBits
        evtIdOffset = self.schema.header.evtIdOffset

        while offset + recordLengthBits + recordTypeBits < size:
            recCnt += 1
            if maxRec > 0 and recCnt > maxRec:
                break;

            recordSizeBits = raw[offset:offset + recordLengthBits].uint * 8
            evtType = raw[offset + recordLengthBits:offset + recordLengthBits + recordTypeBits].uint
            if evtType == 3 and feature == 'CTUM': # footer
                break

            if feature == 'GPEH':
                inValidBit = raw[offset + evtIdOffset]
                if inValidBit:
                    inValidCnt += 1
                    offset += recordSizeBits
                    continue
                else:
                    evtId = raw[offset + 77:offset + 87].uint
            else:
                evtId = raw[offset + evtIdOffset:offset + evtIdOffset+eventIdBits].uint
            if feature == 'CTUM':
                evtId = 0 # hack!

            if recordSizeBits < 32 or recordSizeBits > 99999: # length is fucked!
                print 'Bad length of %d found at offset %d. Aborting. %d %d '%(recordSizeBits, offset, evtType, evtId)
                break
            if evtType == typeValueForEventRecord :  # this is an event
                if feature == 'CTRS':
                    key, data = self.newparseEvent(evtId, raw[offset:offset+ recordSizeBits+ eventIdBits], (recordLengthBits + recordTypeBits+ eventIdBits))
                else:
                    key, data = self.newparseEvent(evtId, raw[offset:offset + recordSizeBits ], (recordLengthBits + recordTypeBits))
                if key not in insertDict:
                    insertDict[key] = []
                factor = 32768 / len(data) # assume an 32k maximum for a single insert statement
                if len(insertDict[key]) >= factor:
                    self.writeRec(key, insertDict[key], sqlFile)
                    insertDict[key] = []
                insertDict[key].append(data)
                insrtCnt += 1
            # FFV checks
            elif evtType == 0: # this is a header
                off = recordLengthBits + recordTypeBits
                if not self.ffvCheck(raw[offset +off: offset + recordSizeBits - off], feature, verbose):
                    return

            else:
                if verbose:
                    print 'Record type', evtType, 'is not an Event record.'

            offset += recordSizeBits

        for key in insertDict:
            self.writeRec(key, insertDict[key], sqlFile)

        sqlFile.write('commit;\n')
        sqlFile.close()
        print 'record count in raw data: %d (incl headers, footers etc.). Records added to DB: %d ' % (recCnt, insrtCnt)
        if inValidCnt > 0:
            print "%d records with invalid event IDs detected!"%inValidCnt

    def writeRec(self, key, data, sqlFile):
        sqlFile.write('insert into ')
        sqlFile.write(key)
        sqlFile.write(' values\n ')
        sqlFile.write(',\n '.join(data))
        sqlFile.write(';\n')


    def ffvCheck(self, raw, feature, verbose):
        ''' return false if ffv or fiv test fails
        '''
        if feature=='CTRS': # CTRS FILE and TCP headers
            ffv = raw[0: 40].bytes
            tmp = str(ffv.strip())
            ffv = ''
            for t in tmp: # strip() wont remove 0x0 bytes.
                if t.isalpha():
                    ffv += t
            if ffv == 'T':
                fiv = raw[144:168].bytes # fiv2
            else:
                fiv = str(raw[40:80].bytes).strip()
        elif feature=='GPEH':
            ffv = raw[0: 40].bytes
            f2 = raw[3296:3336].bytes
            #print 'len',len(raw),'f2',f2
            fiv = ''
            for i in range(len(f2)):
                if f2[i].isalnum():
                    fiv += f2[i]
            self.printGPEHheader(raw, 0)
        elif feature=='SGEH' or feature=='CTUM':
            ffv = str(raw[0:8].uint)
            fiv = str(raw[8:16].uint)
        else:
            print 'Unknown feature "%s". Unable to check FFV/FIV. Aborting!'%feature
            return False

        if ffv != self.schema.header.ffv:
            print 'Warning! FFV does not match. Expected "%s" but got "%s". Aborting!'%(self.schema.header.ffv, ffv)
            return False
        else :
            if feature=='CTRS':
                expectedfiv = self.schema.header.fiv2
            else:
                expectedfiv = self.schema.header.fiv
            if fiv != expectedfiv:
                print 'Warning! FIV does not match. Expected "%s" but got "%s".'%(expectedfiv, fiv),
                if expectedfiv < fiv:
                    print 'Will attempt to "Treat As"'
                else:
                    print 'Results unpredictable!'
            if verbose:
                print 'FFV:',ffv,', FIV:',fiv


        return True

    def printSGEHheader(self, raw, off):
        print 'GPEH Header',
        ll = raw[0:16].uint
        print 'll',ll,
        rt = raw[16:24].uint
        print 'rt',rt,
        ffv = raw[24:32].uint
        print 'ffv',ffv,
        fiv = raw[32:40].uint
        print 'fiv',fiv


    def printGPEHheader(self, raw, off):
        #off = 0
        print 'GPEH Header',
        ffv = raw[off : off + 40].bytes
        off += 40
        print ' ffv:', ffv,
        print 'year ', raw[off : off + 16].uint,
        off += 16
        print 'mon ', raw[off : off + 8].uint,
        off += 8
        print 'day ', raw[off : off + 8].uint,
        off += 8
        print 'hour ', raw[off : off + 5].uint,
        off += 8
        print 'min ', raw[off : off + 6].uint,
        off += 8
        print 'sec ', raw[off : off + 6].uint,
        off += 8
        # ne_usr label 1600 bits
        off += 1600
        # ne_logical_label 1600 bits
        off += 1600
        print 'off ',off,'fiv ', 'len =',len(raw), raw[off : off +40].bytes
        print 'fiv +8 ', raw[off +8: off +48].bytes
        print 'fiv -8 ', raw[off -8: off +32].bytes
        print 'fiv -16 ', raw[off -16: off +64]


        ll = raw[0:16].uint
        print 'll',ll,
        rt = raw[16:24].uint
        print 'rt',rt,
        ffv = raw[24:64]
        print 'ffv',ffv,
        yr = raw[64:80].uint
        print 'yr',yr,
        mn = raw[80:88].uint
        print 'mn',mn,
        mn = raw[88:96].uint
        print 'dy',mn,
        mn = raw[96:104].uint
        print 'hr',mn,
        mn = raw[104:112].uint
        print 'mm',mn,
        mn = raw[112:120].uint
        print 'ss',mn
        fiv = raw[120+3200:120+3200+40].bytes

        print 'fiv',fiv
        print 'fiv',str(fiv)
        print 'fiv',str(fiv).strip()
        f2 = ''
        for i in range(len(fiv)):
            if fiv[i].isalnum():
                f2 += fiv[i]
        print 'fiv',f2
        # fiv 40

def main(argv = None):
    #outFile = 'raw.sql'
    outFile = ''
    verbose = False
    inFile = ''
    schemaFile = ''
    maxRec = -1

    if argv == None:
        argv = sys.argv

    for arg in argv:
        if arg.startswith("inFile="):
            inFile = arg.split('=')[1]
        if arg.startswith("schema="):
            schemaFile = arg.split('=')[1]
        if arg.startswith("outFile="):
            outFile = arg.split('=')[1]
        if arg.startswith("verbose="):
            verbose = (True if "True" == arg.split('=')[1] else False)

        # -- or --
    numArgs = len(argv)
    i = 0
    while i < numArgs:
        arg = argv[i]
        if arg == '-i' and (i+1) < numArgs :
            i += 1
            inFile=argv[i]
        if arg == '-s' and (i+1) < numArgs :
            i += 1
            schemaFile=argv[i]
        if arg == '-o' and (i+1) < numArgs :
            i += 1
            outFile=argv[i]
        if arg == '-m' and (i+1) < numArgs :
            i += 1
            maxRec=int(argv[i])
        if arg == '-v' or arg == '-?':
            verbose=True
        i+=1

    if not outFile:
        outFile = inFile + '.sql'

    print 'Starting parseRaw with schemaFile=%s, inFile=%s, outFile=%s, verbose=%s'%(schemaFile, inFile,outFile, verbose)

    mySchema = schema.loadSchema(schemaFile)

    p = parser(mySchema)


    p.parseFile(inFile, outFile, verbose, maxRec)

if __name__ == '__main__':
    print 'Run grit_db instead.'
    #main()
