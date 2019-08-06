import saliweb.frontend
import collections
import re


TSVModResult = collections.namedtuple('TSVModResult',
    ('modelfile', 'chain', 'matchtype', 'featurecount', 'relaxcount', 'size',
     'rmsd', 'no35', 'ga341', 'ga341_pair', 'ga341_surf', 'ga341_comb',
     'zdope'))

ModellerResult = collections.namedtuple('ModellerResult',
    ('chain', 'zdope', 'ga341', 'zpair', 'zsurf', 'zcombi', 'seqid',
     'compactness'))


class ResultError(object):
    def __init__(self, error):
        self.error = error


def show_results_page(job):
    errors = []
    tsvmod_results = parse_tsvmod(job, errors)
    modeller_results = parse_modeller(job, errors)
    return saliweb.frontend.render_results_template("results_ok.html",
        tsvmod_results=list(tsvmod_results),
        modeller_results=list(modeller_results), job=job, errors=errors)


def parse_tsvmod(job, errors):
    with open(job.get_path('input.tsvmod.pred')) as fh:
        fh.readline()   # ignore header line
        for line in fh:
            spl = line.rstrip('\r\n').split('|')
            if len(spl) > 9:
                yield TSVModResult._make(spl)
            else:
                e = ResultError(line.rstrip('\r\n'))
                errors.append(e)
                yield e


def parse_modeller(job, errors):
    current_chain = None
    current_fields = dict.fromkeys(ModellerResult._fields)
    field_map = {'ZDOPE': 'zdope', 'GA341': 'ga341', 'Z-PAIR': 'zpair',
                 'Z-SURF': 'zsurf', 'Z-COMBI': 'zcombi', 'SeqIdent': 'seqid',
                 'Compactness': 'compactness'}
    blank_line = re.compile('\s*$')
    def update_chain(chain):
        if chain != current_chain and current_chain is not None:
            r = ModellerResult._make(
                current_fields[f] for f in ModellerResult._fields)
            for key in current_fields.keys():
                current_fields[key] = None
            return r
  
    with open(job.get_path('modeller.results')) as fh:
        for line in fh:
            if re.match(blank_line, line):  # skip blank lines
                continue
            if line.startswith('Error'):
                e = ResultError(line.rstrip('\r\n'))
                errors.append(e)
                yield e
            else:
                chain, key, value = line.rstrip('\r\n').split()
                c = update_chain(chain)
                if c: yield c
                current_chain = chain
                current_fields[field_map[key]] = float(value)
                current_fields['chain'] = chain
    c = update_chain(None)
    if c: yield c
