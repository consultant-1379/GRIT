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

import ConfigParser
import os

class DbUtility:

    def __init__(self): 
        
        self.dbPropertiesFile = 'etc/db.cfg'
        if not os.path.exists(self.dbPropertiesFile):
            self.dbPropertiesFile = '../etc/db.cfg'
        self.driver=self.getDriverDetails(self.dbPropertiesFile)
        
    def getDataTypeInCharConversion(self,isNullCheck,transform,var):  
        if 'postgres' in self.driver:
            if isNullCheck:                
                castStr="\'-1\'::char"
            else:
                castStr="(%s%s)::varchar"%(transform,var)
                
        else:
            if isNullCheck: 
                castStr="cast(-1 as char(32))"
            else:
                castStr="convert(varchar,%s%s)"%(transform,var)
        return castStr
    
    def getMD5Conversion(self,castStr):
        valMD5='cast(HASH (%s, \'md5\')as char(32))'%castStr
        if 'postgres' in self.driver:
            valMD5='md5(%s)'%castStr
           
        return valMD5
    
    def getAlias(self,transform): 
        if 'postgres' in self.driver:
            return '('+transform+')'
        else:
            return 'transform'  
    
    
    def getDateFormatConversion(self):
        dateStr = 'DATEFORMAT'
        
        if 'postgres' in self.driver:
            dateStr = 'to_char'
        
        return dateStr
    
    def getRoundSyntax(self):
        roundKeywordList = ['round(convert(double,(','))']  
        if 'postgres' in self.driver:
            roundKeywordList = ['round(cast(',' as numeric)']
        
        return roundKeywordList

    
    def getPadSyntax(self,tokenList0,tokenList2,tokenList4,tokenList5): 
        transform = 'right(replicate(%s, %s) | %s%s, %s)' % (tokenList0, tokenList2, tokenList4, tokenList5,tokenList2)         
        if 'postgres' in self.driver:
            transform = 'lpad(%s%s :: text,%s,%s)' %(tokenList4,tokenList5,tokenList2, tokenList0)
        
        return transform 
    

    def getPadRightSyntax(self,tokenList0,tokenList2,tokenList4,tokenList5):
        transform = 'left(%s%s | replicate(%s, %s), %s)' % (tokenList4, tokenList5, tokenList0, tokenList2, tokenList2) 
        if 'postgres' in self.driver:
            transform = 'rpad(%s%s :: text,%s,%s)' %(tokenList4,tokenList5,tokenList2, tokenList0)
        
        return transform
                                     
    def getDriverDetails(self,dbPropertiesFile):
        section = 'DATABASE_INFO'
        config = ConfigParser.RawConfigParser()
        config.read(dbPropertiesFile)
        try:
            self.driver = config.get(section, 'driver') 
        except Exception:
            print 'Invalid database configuration'
            
        return self.driver


        
  
        
        