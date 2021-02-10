import saliweb.backend
import os


class MissingOutputError(Exception):
    pass


def _read_parameters_file():
    """Read sequence identity from parameters file and return it"""
    seq_ident = 0
    if not os.path.exists("parameters.txt"):
        return seq_ident

    with open("parameters.txt") as fh:
        for line in fh:
            key, value = line.split(":")
            if key == "SequenceIdentity":
                if not value.rstrip(' \r\n'):
                    value = 30
                try:
                    seq_ident = float(value)
                except ValueError:
                    raise TypeError("Sequence Identity %s contains disallowed "
                                    "characters" % value)
                if seq_ident < 1.1:
                    seq_ident *= 100.
    return seq_ident


class Job(saliweb.backend.Job):

    runnercls = saliweb.backend.LocalRunner

    def run(self):
        if os.path.exists("alignment.pir"):
            alignment = " -alignment alignment.pir"
        else:
            alignment = ""

        if os.path.exists("input.pdb"):
            model = " -model input.pdb"
        else:
            model = ""
        seq_ident = _read_parameters_file()

        directory = os.getcwd()
        evaluation_script = self.config.evaluation_script \
            + model+alignment
        script = "score_all.sh"
        fh = open(directory+"/"+script, "w")
        if seq_ident > 0:
            seq_ident = " --seq_ident "+str(seq_ident)
        else:
            seq_ident = ""
        print("#!/bin/csh", file=fh)
        print("cd "+directory, file=fh)
        print("echo STARTED >job-state", file=fh)
        print(evaluation_script+">&evaluation.log", file=fh)
        print(self.config.modeller_setup, file=fh)
        print("python3 " + self.config.modeller_script
              + " --model input.pdb " + seq_ident + ">&modeller.log", file=fh)
        print("echo \"<evaluation>\" >evaluation.txt\n", file=fh)
        print("rm -f evaluation.xml\n", file=fh)
        print("cat *.xml >>evaluation.txt\n", file=fh)
        print("echo \"</evaluation>\" >>evaluation.txt\n", file=fh)
        print("mv evaluation.txt evaluation.xml\n", file=fh)
        print("sleep 2s", file=fh)
        print("echo DONE >job-state", file=fh)
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
