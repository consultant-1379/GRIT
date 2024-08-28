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

import os
import sys
import ConfigParser
import time
import dbAccess as DbAccess
#
def autoRuleGenerationMim(ruleDir,inFile):
        print 'Rule generation using mim'       
        
        tableList = []
        inList = set([])
        
            # List of unique counters created from schema
        with open(inFile, 'r') as fr:            
            inField=fr.read().splitlines()
            for i in inField:
                inList.add(i.strip())
        with open(inFile, 'w') as fw:
            for v in sorted(inList):
                fw.write('%s\n'%v)
                
            # obtain a DB connection to extract Raw table Counters
            
            dbPropertiesFile = 'etc/db.cfg'
            if not os.path.exists(dbPropertiesFile):
                dbPropertiesFile = '../etc/db.cfg'
            dbAccess = DbAccess.DbAccess(dbPropertiesFile)
            dbAccess.openConn()
            conn=dbAccess.conn
            print 'Connection Successfully Established.'
            with conn.cursor() as c:
                c.tables(None, None, '%', ('VIEW',))
                for s in c.fetchall():
                    if s[2].startswith('DC_E_') and s[2].endswith('RAW') and s[1] == 'dc':
                        tableList.append( s[2] )
                with open('views.txt', 'w') as f:
                    for keytable in tableList:
                        f.write('%s\n'%keytable)
                        columnList= set([])
                        colSet = set([])
                            # columns can be reported more then once so use a set to keep only unique values
                        c.columns(None, None, keytable, '%')
        
                        for col in c.fetchall():
                            colSet.add( col[3] )
                            columnList = list(colSet)
                            #Rule generation implementation
                        matchDict = {}
                        for col in columnList:
                            if col in inList:
                                matchDict[col] = col
                        if not os.path.exists(ruleDir):
                            os.makedirs(ruleDir)
                        if len(matchDict)> 0:
                            with open(ruleDir+'/'+keytable+'.rules', 'w') as g:
                                for k,v in matchDict.items():
                                    if '_V_RAW' in keytable:
                                        g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null,in.DC_VECTOR_index=out.DCVECTOR_INDEX)\n'%(k, v, k, v))
                                    elif 'FLEX_RAW' in keytable:
                                        g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null,in.FLEX_FILTERNAME=out.FLEX_FILTERNAME)\n'%(k, v, k, v))
                                    else:
                                        g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null)\n'%(k, v, k, v))
                    
                                  
def autoRuleGeneration(ruleDir):
        print "Current time " + time.strftime("%X")
        print "Rule generation using repdb"
        CounterDict ={}
            # obtain a DB connection to extract Raw table Counters
        dbPropertiesFile = 'etc/db.cfg'
        if not os.path.exists(dbPropertiesFile):
            dbPropertiesFile = '../etc/db.cfg'
        dbAccess = DbAccess.DbAccess(dbPropertiesFile)
        dbAccess.openConn()
        conn=dbAccess.conn
        print 'Connection Successfully Established.'
        with conn.cursor() as c:
            c.execute("SELECT dataformatid, dataname,process_instruction from dataitem where (dataformatid like  'DC_E%' ) and process_instruction in('flexcounter','vector','gauge','peg','cmvector','compressedvector')")
            data =c.fetchall()
            for rows in data:
                key=rows[0].split(':')
                Table=str(key[2])+'_RAW'
                value=rows[1]
                CounterDict.setdefault(Table, []).append(value)
            if not os.path.exists(ruleDir):
                os.makedirs(ruleDir)
            for k,v in CounterDict.items():
                with open(ruleDir+'/'+k+'.rules','w') as g:
                    for i in v :
                        if '_V_RAW' in k:
                            g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null,in.DC_VECTOR_index=out.DCVECTOR_INDEX)\n'%(i, i, i, i))
                        elif 'FLEX_RAW' in k:
                            g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null,in.FLEX_FILTERNAME=out.FLEX_FILTERNAME)\n'%(i, i, i, i))
                        else:
                            g.write('round(in.%s,2) <=> round(out.%s,2) when(in.moid=out.moid,in.FDN=out.SN,in.%s!=null,out.%s!=null)\n'%(i, i, i, i))
            if len(CounterDict)> 0:
                print 'Rules Generated.'
            print "Current time " + time.strftime("%X")
def main(argv = None):

    ruleDir =''
    inFile = ''
    outColDir = ''
    isMim=''
    verbose = False
    
    if argv == None:
        argv = sys.argv
    
    for arg in argv:
        if arg.startswith("ruleDir="):
            ruleDir = arg.split('=')[1]
        if arg.startswith("inFile="):
            inFile = arg.split('=')[1]
        if arg.startswith("outColDir="):
            outColDir = arg.split('=')[1]
        if arg.startswith("verbose="):
            verbose = (True if "True" == arg.split('=')[1] else False)
    
            # -- or --
    numArgs = len(argv)
    i = 0
    while i < numArgs:
        arg = argv[i]
        if arg == '-r' and (i+1) < numArgs :
            i += 1
            ruleDir=argv[i]
        if arg == '-v' or arg == '-?':
            verbose=True
        if arg == '-i' and (i+1) < numArgs :
            i += 1
            inFile=argv[i]
        if arg == '-o' and (i+1) < numArgs :
            i += 1
            outColDir=argv[i]
        if arg == '-m' and (i+1) < numArgs :
            i += 1
            isMim=argv[i]
        
        i+=1   
    if inFile == '':
        autoRuleGeneration(ruleDir)
    else:
        autoRuleGenerationMim(ruleDir,inFile)
                            
if __name__ == '__main__':
    print 'Run grit_db instead.'
