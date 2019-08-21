import unittest
import saliweb.test
import re


# Import the modeval frontend with mocks
evaluation = saliweb.test.import_mocked_frontend("evaluation", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):

    def test_results_file(self):
        """Test download of results files"""
        with saliweb.test.make_frontend_job('testjob') as j:
            for fname in ('bad.log', 'evaluation.xml', 'modeller.log'):
                j.make_file(fname)
            c = evaluation.app.test_client()
            # Prohibited file (that exists)
            rv = c.get('/job/testjob/bad.log?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 404)
            # Good files
            rv = c.get('/job/testjob/evaluation.xml?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 200)
            rv = c.get('/job/testjob/modeller.log?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 200)

    def test_ok_job(self):
        """Test display of OK job"""
        with saliweb.test.make_frontend_job('testjob2') as j:
            j.make_file("input.tsvmod.pred",
"""Modelfile|Chain|TSVMod type|Feature Count|Relax Count|Size|Predicted RMSD|Predicted NO35|GA341|Pair|Surf|Comb|z-Dope
input.pdb|A|MatchBySS|Reduced|1|420|18.314|0.104|0.694712|-0.6143005|-0.3749842|-0.6870231|0.1793957
""")
            j.make_file("modeller.results", """
A SeqIdent 30.000000

A ZDOPE 1.793957

A GA341 1.000000
A Z-PAIR -6.143005
A Z-SURF -3.749842
A Z-COMBI -6.870231
A Compactness 0.145962
""")
            j.make_file("input.profile_A", "")
            c = evaluation.app.test_client()

            # Test with no DOPE profile
            rv = c.get('/job/testjob2?passwd=%s' % j.passwd)
            r = re.compile('Predicted RMSD.*18\.314.*z-DOPE:.*1\.794.*'
                           'DOPE Profile not available',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

            # Test with PNG DOPE profile
            j.make_file("dope_profile.png")
            rv = c.get('/job/testjob2?passwd=%s' % j.passwd)
            r = re.compile('Predicted RMSD.*18\.314.*z-DOPE:.*1\.794.*'
                           'dope_profile\.png',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

            # Test with SVG DOPE profile
            j.make_file("dope_profile.svg")
            rv = c.get('/job/testjob2?passwd=%s' % j.passwd)
            r = re.compile('Predicted RMSD.*18\.314.*z-DOPE:.*1\.794.*'
                           'dope_profile\.svg.*'
                           'Download raw DOPE profile files:.*'
                           'input\.profile_A.*chain A',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

    def test_ok_job_with_errors(self):
        """Test display of OK job with no-TSVMod and Modeller errors"""
        with saliweb.test.make_frontend_job('testjob3') as j:
            j.make_file("input.tsvmod.pred")
            j.make_file("modeller.results", """
Error error1
Error error2
""")
            c = evaluation.app.test_client()
            rv = c.get('/job/testjob3?passwd=%s' % j.passwd)
            r = re.compile('TSVMod failed on input PDB file.*'
                           'Error error1.*Error error2.*'
                           'Multiple Errors occurred!',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

    def test_ok_job_with_tsvmod_errors(self):
        """Test display of OK job with TSVMod errors"""
        with saliweb.test.make_frontend_job('testjob3') as j:
            j.make_file("input.tsvmod.pred", "header\nerror: cannot parse PDB")
            j.make_file("modeller.results")
            c = evaluation.app.test_client()
            rv = c.get('/job/testjob3?passwd=%s' % j.passwd)
            r = re.compile('TSVMod Results.*error: cannot parse PDB.*'
                           'Modeller Scoring Results.*'
                           'DOPE Profile not available',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

    def test_ok_job_xml(self):
        """Test display of OK job, XML forced"""
        with saliweb.test.make_frontend_job('testjob3') as j:
            j.make_file("input.tsvmod.pred")
            j.make_file("modeller.results")
            c = evaluation.app.test_client()
            rv = c.get('/job/testjob3?passwd=%s&force_xml=1' % j.passwd)
            r = re.compile('<\?xml.*<results_file.*evaluation\.xml',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)

    def test_failed_job(self):
        """Test display of failed job"""
        with saliweb.test.make_frontend_job('testjob4') as j:
            c = evaluation.app.test_client()
            rv = c.get('/job/testjob4?passwd=%s' % j.passwd)
            r = re.compile('Your ModEval job.*failed to produce results',
                           re.MULTILINE | re.DOTALL)
            self.assertRegexpMatches(rv.data, r)


if __name__ == '__main__':
    unittest.main()
