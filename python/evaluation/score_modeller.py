from optparse import OptionParser
import sys
import os

import matplotlib
# Force matplotlib (and pylab) to not use any X backend
# (we don't have a display).
matplotlib.use('Agg')
import pylab

from modeller import *
from modeller.automodel import *
from modeller.scripts import complete_pdb

def get_profile(profile_file):
    """Read `profile_file` into a Python array."""

    f = file(profile_file)
    vals = []
    for line in f:
        if not line.startswith('#') and len(line) > 10:
            spl = line.split()
            vals.append(float(spl[-1]))
    return vals


"""Runs all ModPipe Model Evaluation routines (dope,zdope,ga341)
"""

def get_options():
    """Parse command-line options"""
    parser = OptionParser()
    parser.set_usage("""
 This script runs Modeller to retrieve z-dope, and ga341
 Run `%prog -h` for help information
""")

    parser.add_option("--model", type="string", metavar="FILE",
                      help="""Path and Filename of models file (PDB format)""")
    parser.add_option("--seq_ident", type="string",
                      help="""Sequence Identity to Template PDB File.
If no sequence identity is given, either here or in the model file,
only the z-dope score will be computed.""")

    opts, args = parser.parse_args()
    if (not opts.model):
        parser.error("Cannot proceed without --model (input pdb file)")
    return opts

def main():
    opts = get_options()
    fh=open("modeller.results","w")
    fhxml=open("modeller.results.xml","w")
    print "modelfile "+str(opts)
    log.minimal()
    env = environ()
    env.libs.topology.read(file='$(LIB)/top_heav.lib')
    env.libs.parameters.read(file='$(LIB)/par.lib')

    try:
        mdl=complete_pdb(env,opts.model, transfer_res_num=True)
    except:
        print >>fh, "Error in Modelfile: Not a valid PDB file\n"
        print >>fhxml, "    <modeller_results>\n        <type>Error in Modelfile: Not a valid PDB file<\type>\n    </modeller_results>\n"
        sys.exit("Error in Modelfile: Not a valid PDB file")
    i=0
    colors=["green","red","blue","purple","green","red","blue","purple"]
    color=colors[i]

    for c in mdl.chains:
        (c.name, len(c.residues))
        selected_chain=complete_pdb(env,opts.model,model_segment=('FIRST:'+c.name,'LAST:'+c.name))
        if not c.name:
            c.name="A"
        z_dope_score = selected_chain.assess_normalized_dope()
        s = selection(selected_chain)
        s.assess_dope(output='ENERGY_PROFILE NO_REPORT', file='input.profile_'+c.name,
                  normalize_profile=True, smoothing_window=15)
        profile = get_profile('input.profile_'+c.name)
        try:
            pylab.figure(1, figsize=(10,6))
            pylab.xlabel('Alignment position')
            pylab.ylabel('DOPE per-residue score')
            pylab.plot(profile, color=color, linewidth=2, label='Chain '+c.name)
            pylab.legend()
            pylab.savefig('dope_profile.png', dpi=65)
        except:
            pass
        i=i+1
        try:
            color=colors[i]
        except:
            i=0
            color=colors[i]


        try:
            (ga341, compactness, e_native_pair, e_native_surf, e_native_comb, \
                    z_pair, z_surf, z_comb) = selected_chain.assess_ga341()
            print >>fh, "%s SeqIdent %f\n\n%s ZDOPE %f\n\n%s GA341 %f\n%s Z-PAIR %f\n%s Z-SURF %f\n%s Z-COMBI %f\n%s Compactness %f\n" \
                % (c.name,selected_chain.seq_id,c.name,z_dope_score,c.name,ga341, c.name,z_pair, c.name,z_surf, c.name,z_comb, c.name,compactness)
            print >>fhxml, "    <modeller_results>\n" \
                           "        <model>%s</model>\n" \
                           "        <chain>%s</chain>\n" \
                           "        <sequence_identity>%f</sequence_identity>\n" \
                           "        <zdope>%f</zdope>\n" \
                           "        <ga341>%f</ga341>\n" \
                           "        <z_pair>%f</z_pair>\n" \
                           "        <z_surf>%f</z_surf>\n" \
                           "        <z_comb>%f</z_comb>\n" \
                           "        <compactness>%f</compactness>\n" \
                           "    </modeller_results>\n" \
                           % (opts.model,c.name,selected_chain.seq_id,z_dope_score,ga341,z_pair,z_surf,z_comb,compactness)
        except:
            if (opts.seq_ident):
                selected_chain.seq_id = float(opts.seq_ident)
                (ga341, compactness, e_native_pair, e_native_surf, e_native_comb, \
                      z_pair, z_surf, z_comb) = selected_chain.assess_ga341()
                print >>fh, "%s SeqIdent %f\n\n%s ZDOPE %f\n\n%s GA341 %f\n%s Z-PAIR %f\n%s Z-SURF %f\n%s Z-COMBI %f\n%s Compactness %f\n" \
                    % (c.name,selected_chain.seq_id,c.name,z_dope_score,c.name,ga341, c.name,z_pair, c.name,z_surf, c.name,z_comb, c.name,compactness)
                print >>fhxml, "    <modeller_results>\n        <model>%s</model>\n" \
                               "        <chain>%s</chain>\n" \
                               "        <sequence_identity>%f</sequence_identity>\n" \
                               "        <zdope>%f</zdope>\n" \
                               "        <ga341>%f</ga341>\n" \
                               "        <z_pair>%f</z_pair>\n" \
                               "        <z_surf>%f</z_surf>\n" \
                               "        <z_comb>%f</z_comb>\n" \
                               "        <compactness>%f</compactness>\n" \
                               "    </modeller_results>\n" \
                               % (opts.model,c.name,selected_chain.seq_id,z_dope_score,ga341,z_pair,z_surf,z_comb,compactness)
            else:
                pass
                print >>fh, "%s ZDOPE %f\n" % (c.name,z_dope_score)
                print >>fhxml, "    <modeller_results>\n" \
                           "        <model>%s</model>\n" \
                           "        <chain>%s</chain>\n" \
                           "        <zdope>%f</zdope>\n" \
                           "    </modeller_results>\n" \
                           % (opts.model,c.name,z_dope_score)
    fh.close
    fhxml.close



if __name__ == '__main__':
    main()
