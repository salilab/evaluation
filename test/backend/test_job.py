import unittest
import evaluation
import saliweb.test
import saliweb.backend
import os

class JobTests(saliweb.test.TestCase):
    """Check custom Job class"""

    def make_test_job(self, jobcls, state):
        j = saliweb.test.TestCase.make_test_job(self, jobcls, state)
        j.config.evaluation_script = 'evalscript'
        j.config.modeller = 'modpy'
        j.config.modeller_script = 'runmod'
        return j

    def test_run_sanity_check(self):
        """Test sanity checking in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        open('parameters.txt', 'w').write('SequenceIdentity: foo\n')
        self.assertRaises(TypeError, j.run)

    def assert_in_file(self, fname, srch):
        contents = open(fname).read()
        self.assert_(srch in contents,
                     "String %s not found in file %s contents: %s" \
                     % (srch, fname, contents))

    def test_run_seqid(self):
        """Test handling of sequence identity in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        for seqid, exp_seqid in (('50', '50.0'), ('0.1', '10.0')):
            f = open('parameters.txt', 'w')
            f.write('Dummy: foo\n')
            f.write('SequenceIdentity: %s\n' % seqid)
            f.close()
            r = j.run()
            self.assert_in_file('score_all.sh',
                    'modpy python runmod --model input.pdb  --seq_ident %s>' \
                    % exp_seqid)

    def test_run_align_model(self):
        """Test handling of alignment and model in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)

        r = j.run()
        self.assert_in_file('score_all.sh', 'evalscript>')

        open('alignment.pir', 'w')
        r = j.run()
        self.assert_in_file('score_all.sh',
                            'evalscript -alignment alignment.pir>')

        open('input.pdb', 'w')
        r = j.run()
        self.assert_in_file('score_all.sh',
                      'evalscript -model input.pdb -alignment alignment.pir>')

if __name__ == '__main__':
    unittest.main()
