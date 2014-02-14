import saliweb.backend
import os
import sys

class MissingOutputError(Exception): pass


class Job(saliweb.backend.Job):

    runnercls = saliweb.backend.LocalRunner

    def run(self):
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
                   if not value:
                       value = 30
                   try: 
                       seq_ident=float(value)
                   except ValueError:
                       raise TypeError("Sequence Identity %s contains disallowed characters"
                                       % (seq_ident))
                   if seq_ident < 1.1:
                       seq_ident *= 100.

           fh.close()

        directory=os.getcwd()
        evaluation_script = self.config.evaluation_script \
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
        print >>fh, self.config.modeller_setup
        print >>fh, "python " + self.config.modeller_script \
                    + " --model input.pdb " + seq_ident + ">&modeller.log"
        print >>fh, "echo \"<evaluation>\" >evaluation.txt\n"
        print >>fh, "cat *.xml >>evaluation.txt\n"
        print >>fh, "echo \"</evaluation>\" >>evaluation.txt\n"
        print >>fh, "mv evaluation.txt evaluation.xml\n"
        print >>fh,"sleep 10s"
        print >>fh,"echo DONE >job-state"
        fh.close()
        r = self.runnercls("cd "+directory+"; chmod +x "+script+";./"+script)
        return r 

    def postprocess(self):
        for f in ('modeller.results', 'input.tsvmod.results'):
            if not os.path.exists(f):
                raise MissingOutputError("File %s was not generated" % f)


class Config(saliweb.backend.Config):
    def populate(self, config):
        saliweb.backend.Config.populate(self, config)
        # Read our service-specific configuration
        self.evaluation_script = config.get('scoring', 'evaluation_script')
        self.modeller_setup = config.get('scoring', 'modeller_setup')
        self.modeller_script = config.get('scoring', 'modeller_script')


def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = Config(config_file)
    return saliweb.backend.WebService(config, db)

