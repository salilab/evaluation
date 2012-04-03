import saliweb.backend
import os
import ConfigParser
import sys


class Job(saliweb.backend.Job):

    runnercls = saliweb.backend.LocalRunner

    def run(self):
        config = self.configlocal("/modbase5/home/evaluation/service/conf/backend.conf")

        if os.path.exists("alignment.pir"):
            alignment=" -alignment alignment.pir"
        else:
            alignment=""

        if os.path.exists("input.pdb"):
            model=" -model input.pdb"
        else:
            model=""
        seq_ident=0
        if os.path.exists("parameters.txt"):
           fh=open("parameters.txt")
           while 1:
               line = fh.readline()
               if not line:
                   break
               (key,value)=line.split(":")
               if key == "SequenceIdentity":
                   if float(value) < 1.1:
                       value=float(value)*100
                   try: 
                       seq_ident=float(value)
                   except:
                       raise TypeError("Sequence Identity %s contains disallowed characters"
                                       % (seq_ident))
                       
             
           fh.close

        directory=os.getcwd()
        evaluation_script=config['evaluation_script'] \
               + model+alignment
        script="score_all.sh"
        fh=open(directory+"/"+script,"w")
        if (seq_ident>0):
            seq_ident=" --seq_ident "+str(seq_ident)
        else:
            seq_ident=""
        print >>fh,"#!/bin/csh"
        print >>fh,"cd "+directory
        print >>fh,"echo STARTED >job-state"
        print >>fh,evaluation_script+">&evaluation.log"
        print >>fh,config['modeller']+" python "+config['modeller_script']+" --model input.pdb "+seq_ident+ ">&modeller.log"
        print >>fh, "echo \"<evaluation>\" >evaluation.txt\n"
        print >>fh, "cat *.xml >>evaluation.txt\n"
        print >>fh, "echo \"</evaluation>\" >>evaluation.txt\n"
        print >>fh, "mv evaluation.txt evaluation.xml\n"
        print >>fh,"sleep 10s"
        print >>fh,"echo DONE >job-state"
        fh.close
        r = self.runnercls("cd "+directory+"; chmod +x "+script+";./"+script)
        return r 
        
    def configlocal(self,fh):
        configl=ConfigParser.SafeConfigParser()
        fh = open(fh)
        configl.readfp(fh)
        self.configl = {}
        self.configl['database'] = configl.get('scoring','database')
        self.configl['evaluation_script'] = configl.get('scoring','evaluation_script')
        self.configl['modeller'] = configl.get('scoring','modeller')
        self.configl['modeller_script'] = configl.get('scoring','modeller_script')
        self.configl['username'] = configl.get('backend_db','user')
        self.configl['password'] = configl.get('backend_db','passwd')
        return (self.configl)


def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)

