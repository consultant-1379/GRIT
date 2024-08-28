#
#Created on Jun 22, 2015
#
#@author: esmipau
#
# For running Grit in debug mode
import grit
if __name__ == '__main__':
    # you are running from the src directory, compensate accordingly
    dbPropertiesFile = "../etc/db.cfg" 

    # full functional run through
    #argv = ['-a', '10dash', '-t','../etc/ctrs_T_R8A.xml', '-f','CTRS', '-p','Paulct', '-s', 'CTRS_R8A']
    #grit.main(argv)
    
    #argv = ['-a', 'sql', '-d', dbPropertiesFile, '-f', 'makeCTRSTable.sql','-v'] 
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS_R8A', '-i', 'CTRS.bin','-v'] 
    #grit.main(argv)

    #argv = ['-a', 'sql', '-d', dbPropertiesFile, '-f', '../testresources/ctrs_out.bin.sql','-v'] 
    #grit.main(argv)

    #argv = ['-a', 'cleanup', '-f', '../makeCTRSTable.sql','-v'] 
    #grit.main(argv)
 
    # Rules 
    #argv = ['-a', 'sql', '-d', dbPropertiesFile, '-f', '../testresources/basic_test.sql','-v'] 
    #grit.main(argv)

    #argv = ['-a', 'analyse', '-d', dbPropertiesFile, '-t',  '../CFA/Rules_CFA_ERR_RAW/CFA_ERR_RAW.cfg', '-r', '../CFA/Rules_CFA_ERR_RAW/CFA_ERR.rules' ]
    #grit.main(argv)
    
    argv = ['-a', '10dash', '-outsql','K:\\xdeesaw\\Data_for_VTOC_GRit_Code_Change\\Arun_WCDMA_INPUT_OUTPUT\\GRITOUTPUT', '-eparse','../etc/']
    grit.main(argv)

    # clean up
    #argv = ['-a', 'cleanup', '-d', dbPropertiesFile, '-f', 'makeCTRSTable.sql','-v'] 
    #grit.main(argv)
 

    #argv = ['-a', '10dash', '-t','../etc/ctrs_R10A.xml', '-f','CTRS', '-p','Paulct', '-s', 'CTRS_R10A']
    #grit.main(argv)

    #argv = ['-a', '10dash', '-t','ebm_4_18.xml', '-f','SGEH', '-p','Shweta', '-s', 'SGEHShweta']
    #grit.main(argv)

    #argv = ['-a', '10dash', '-t','ctrs_definition.xml', '-f','CTRS', '-p','Paulct', '-s', 'CTRS_15']
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS_13B', '-i', 'CTRS1.bin','-v'] # fails FFV 'S' instead of 'T'
    #grit.main(argv)
    
    #argv = ['-a', 'raw', '-s', 'CTRS_13B', '-i', 'CTRS1.bin','-v'] # fails FFV 'S' instead of 'T'
    #grit.main(argv)

    #argv = ['-a', '10dash', '-t','../etc/ctum_2_2.xml', '-f','CTUM', '-p','Paulct', '-s', 'CTUM']
    #grit.main(argv)
    #argv = ['-a', '10dash', '-t','../etc/ctrs_T_R5A.xml', '-f','CTRS', '-p','Paulct', '-s', 'CTRS']
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTUM', '-i', 'CTUM.bin' ,'-v'] # passes 239 records
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS', '-i', 'CTRS.bin','-v'] # fails FFV 'S' instead of 'T'
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS', '-i', 'CTRS2.bin','-v'] # passes, 4168 records
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS', '-i', 'CTRS3.bin','-v'] # passes 4130 records
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'CTRS', '-i', 'LTEtest2.bin','-v'] # passes 8 records, FIV warning
    #grit.main(argv)

    #argv = ['-a', '10dash', '-t','../etc/ebm_4_15.xml', '-f','SGEH', '-p','Paulct', '-s', 'SGEH_15']
    #grit.main(argv)

    #argv = ['-a', 'raw', '-s', 'SGEH_15', '-i', '../ebm/SGSN56S_A20150602.1415+0800-20150602.1430+0800_14_ebs.253', '-o', 'SGSN56.bin.sql'] # passes 89020 records
    #grit.main(argv)
    #argv = ['-a', '10dash', '-t','../etc/ebm_4_21.xml', '-f','SGEH', '-p','Paulct', '-s', 'SGEH_21']
    #grit.main(argv)
    #argv = ['-a', 'raw', '-s', 'SGEH_21', '-i', '../ebm/TCGLMME05_A20140313.1015+0900-20140313.1016+0900_1_ebs.103', '-o', 'SGSN_TCG.bin.sql' ] # passes 78297
    #grit.main(argv)
    #argv = ['-a', '10dash', '-t','../etc/ebm_4_18.xml', '-f','SGEH', '-p','Paulct', '-s', 'SGEH_18']
    #grit.main(argv)
    #argv = ['-a', 'raw', '-s', 'SGEH_18', '-i', 'SGSN.bin', '-o', 'SGSN_MME.bin.sql', '-v'] # Parsed 226 records -  
    #grit.main(argv)

    #argv = ['-a', '10dash', '-t','../etc/gpeh_15A.xml', '-f','GPEH', '-p','Paulgp', '-s', 'GPEH', '-v']
    #grit.main(argv)
    #argv = ['-a', 'raw', '-s', 'GPEH', '-i', 'AgpehMp0.bin.gz']
    #grit.main(argv)
    #argv = ['-a', 'raw', '-s', 'GPEH', '-i', '../GPEH/AgpehMp10.bin.gz'] # processed 180494 out of 529665
    #grit.main(argv)


    