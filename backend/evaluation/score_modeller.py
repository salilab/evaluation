from argparse import ArgumentParser
import sys
import itertools
from modeller import log, Environ, Selection
from modeller.scripts import complete_pdb

import matplotlib
# Force matplotlib (and pylab) to not use any X backend
# (we don't have a display).
matplotlib.use('Agg')
import pylab   # noqa: E402


def get_profile(profile_file):
    """Read `profile_file` into a Python array."""

    vals = []
    with open(profile_file) as f:
        for line in f:
            if not line.startswith('#') and len(line) > 10:
                spl = line.split()
                vals.append(float(spl[-1]))
    return vals


"""Runs all ModPipe Model Evaluation routines (dope,zdope,ga341)
"""


def get_options():
    """Parse command-line options"""
    p = ArgumentParser(description="""
 This script runs Modeller to retrieve z-dope, and ga341.
 Run `%(prog)s -h` for help information
""")

    p.add_argument("--model", type=str, metavar="FILE", required=True,
                   help="""Path and Filename of models file (PDB format)""")
    p.add_argument("--seq_ident", type=float, default=None, metavar='PCT',
                   help="""Sequence Identity to Template PDB File.
If no sequence identity is given, either here or in the model file,
only the z-dope score will be computed.""")

    return p.parse_args()


def main():
    opts = get_options()
    fh = open("modeller.results", "w")
    fhxml = open("modeller.results.xml", "w")
    print("modelfile "+str(opts))
    log.minimal()
    env = Environ()
    env.libs.topology.read(file='$(LIB)/top_heav.lib')
    env.libs.parameters.read(file='$(LIB)/par.lib')

    try:
        mdl = complete_pdb(env, opts.model, transfer_res_num=True)
    except Exception:
        print("Error in Modelfile: Not a valid PDB file\n", file=fh)
        print("    <modeller_results>\n"
              "        <type>Error in Modelfile: Not a valid PDB file</type>\n"
              "    </modeller_results>", file=fhxml)
        sys.exit("Error in Modelfile: Not a valid PDB file")

    colors = ["green", "red", "blue", "purple"]

    for c, color in zip(mdl.chains, itertools.cycle(colors)):
        (c.name, len(c.residues))
        selected_chain = complete_pdb(
            env, opts.model, model_segment=('FIRST:'+c.name, 'LAST:'+c.name))
        if not c.name:
            c.name = "A"
        z_dope_score = selected_chain.assess_normalized_dope()
        s = Selection(selected_chain)
        s.assess_dope(output='ENERGY_PROFILE NO_REPORT',
                      file='input.profile_'+c.name,
                      normalize_profile=True, smoothing_window=15)
        profile = get_profile('input.profile_'+c.name)
        try:
            pylab.figure(1, figsize=(10, 6))
            pylab.xlabel('Alignment position')
            pylab.ylabel('DOPE per-residue score')
            pylab.plot(profile, color=color, linewidth=2,
                       label='Chain '+c.name)
            pylab.legend()
            pylab.savefig('dope_profile.png', dpi=65)
            pylab.savefig('dope_profile.svg')
        except Exception:
            pass

        try:
            (ga341, compactness, e_native_pair, e_native_surf, e_native_comb,
             z_pair, z_surf, z_comb) = selected_chain.assess_ga341()
        except ValueError:
            # Provide sequence identity if GA341 needs it
            if opts.seq_ident is None:
                continue
            selected_chain.seq_id = opts.seq_ident
            (ga341, compactness, e_native_pair, e_native_surf, e_native_comb,
             z_pair, z_surf, z_comb) = selected_chain.assess_ga341()
        print("%s SeqIdent %f\n\n%s ZDOPE %f\n\n%s GA341 %f\n%s Z-PAIR %f\n"
              "%s Z-SURF %f\n%s Z-COMBI %f\n%s Compactness %f\n"
              % (c.name, selected_chain.seq_id, c.name, z_dope_score, c.name,
                 ga341, c.name, z_pair, c.name, z_surf, c.name, z_comb, c.name,
                 compactness), file=fh)
        print("    <modeller_results>\n"
              "        <model>%s</model>\n"
              "        <chain>%s</chain>\n"
              "        <sequence_identity>%f</sequence_identity>\n"
              "        <zdope>%f</zdope>\n"
              "        <ga341>%f</ga341>\n"
              "        <z_pair>%f</z_pair>\n"
              "        <z_surf>%f</z_surf>\n"
              "        <z_comb>%f</z_comb>\n"
              "        <compactness>%f</compactness>\n"
              "    </modeller_results>\n"
              % (opts.model, c.name, selected_chain.seq_id, z_dope_score,
                 ga341, z_pair, z_surf, z_comb, compactness), file=fhxml)
    fh.close()
    fhxml.close()


if __name__ == '__main__':
    main()
