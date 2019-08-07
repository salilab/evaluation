import saliweb.frontend
import collections
import re


TSVModResult = collections.namedtuple('TSVModResult',
    ('modelfile', 'chain', 'matchtype', 'featurecount', 'relaxcount', 'size',
     'rmsd', 'no35', 'ga341', 'ga341_pair', 'ga341_surf', 'ga341_comb',
     'zdope'))


class ResultError(object):
    def __init__(self, error):
        self.error = error


def show_results_page(job):
    errors = []
    tsvmod_results = parse_tsvmod(job, errors)
    modeller_results = parse_modeller(job, errors)

    return saliweb.frontend.render_results_template("results_ok.html",
        extra_xml_outputs=['evaluation.xml'],
        tsvmod_results=list(tsvmod_results),
        modeller_results=modeller_results, job=job, errors=errors)


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
    results = []
    chains = {}

    blank_line = re.compile('\s*$')
    with open(job.get_path('modeller.results')) as fh:
        for line in fh:
            if blank_line.match(line):  # skip blank lines
                continue
            elif line.startswith('Error'):
                e = ResultError(line.rstrip('\r\n'))
                errors.append(e)
                results.append(e)
            else:
                chain, key, value = line.rstrip('\r\n').split()
                key = key.replace('-', '').lower()
                if chain in chains:
                    chains[chain][key] = float(value)
                else:
                    r = {key: float(value), 'chain': chain}
                    chains[chain] = r
                    results.append(r)
    return results
