import unittest
import evaluation
import saliweb.test
import saliweb.backend


class JobTests(saliweb.test.TestCase):
    """Check custom Job class"""

    def make_test_job(self, jobcls, state):
        j = saliweb.test.TestCase.make_test_job(self, jobcls, state)
        j.config.evaluation_script = 'evalscript'
        j.config.modeller_setup = 'module load modeller'
        j.config.modeller_script = 'runmod'
        return j

    def test_run_sanity_check(self):
        """Test sanity checking in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        with open('parameters.txt', 'w') as fh:
            fh.write('SequenceIdentity: foo\n')
        self.assertRaises(TypeError, j.run)
        del d

    def assert_in_file(self, fname, srch):
        with open(fname) as fh:
            contents = fh.read()
        self.assertIn(srch, contents,
                      "String %s not found in file %s contents: %s"
                      % (srch, fname, contents))

    def test_run_seqid(self):
        """Test handling of sequence identity in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        for seqid, exp_seqid in (('', '30.0'), ('50', '50.0'),
                                 ('0.1', '10.0')):
            with open('parameters.txt', 'w') as f:
                f.write('Dummy: foo\n')
                f.write('SequenceIdentity: %s\n' % seqid)
            _ = j.run()
            self.assert_in_file('score_all.sh', 'module load modeller')
            self.assert_in_file(
                'score_all.sh',
                'python3 runmod --model input.pdb  --seq_ident %s>'
                % exp_seqid)
        del d

    def test_run_align_model(self):
        """Test handling of alignment and model in run method"""
        j = self.make_test_job(evaluation.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)

        _ = j.run()
        self.assert_in_file('score_all.sh', 'evalscript>')

        with open('alignment.pir', 'w'):
            pass
        _ = j.run()
        self.assert_in_file('score_all.sh',
                            'evalscript -alignment alignment.pir>')

        with open('input.pdb', 'w'):
            pass
        _ = j.run()
        self.assert_in_file(
            'score_all.sh',
            'evalscript -model input.pdb -alignment alignment.pir>')
        del d

    def test_postprocess(self):
        """Test Job.postprocess()"""
        j = self.make_test_job(evaluation.Job, 'COMPLETED')
        d = saliweb.test.RunInDir(j.directory)
        self.assertRaises(evaluation.MissingOutputError, j.postprocess)
        with open('modeller.results', 'w'):
            pass
        self.assertRaises(evaluation.MissingOutputError, j.postprocess)
        with open('input.tsvmod.results', 'w'):
            pass
        j.postprocess()
        del d


if __name__ == '__main__':
    unittest.main()
