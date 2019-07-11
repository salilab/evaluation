import unittest
import saliweb.test
import os
import re

# Import the modeval frontend with mocks
evaluation = saliweb.test.import_mocked_frontend("evaluation", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):
    """Check submit page"""

    def test_submit_page(self):
        """Test submit page"""
        incoming = saliweb.test.TempDir()
        evaluation.app.config['DIRECTORIES_INCOMING'] = incoming.tmpdir
        c = evaluation.app.test_client()
        rv = c.post('/job')
        self.assertEqual(rv.status_code, 400)  # no license key

        modkey = saliweb.test.get_modeller_key()
        data={'modkey': modkey}
        rv = c.post('/job', data=data)
        self.assertEqual(rv.status_code, 400)  # no pdb file

        t = saliweb.test.TempDir()
        pdbf = os.path.join(t.tmpdir, 'test.pdb')
        with open(pdbf, 'w') as fh:
            fh.write("REMARK\n"
                     "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")

        # Successful submission (no email)
        data['model_file'] = open(pdbf)
        rv = c.post('/job', data=data)
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted.*You can check on your job',
                       re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

        # Successful submission (with email)
        data['email'] = 'test@test.com'
        data['model_file'] = open(pdbf)
        rv = c.post('/job', data=data)
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted.*You will be notified.*'
                       'You can check on your job', re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

    def test_submit_page_alignment(self):
        """Test submit page with alignment"""
        incoming = saliweb.test.TempDir()
        evaluation.app.config['DIRECTORIES_INCOMING'] = incoming.tmpdir
        c = evaluation.app.test_client()

        t = saliweb.test.TempDir()
        pdbf = os.path.join(t.tmpdir, 'test.pdb')
        with open(pdbf, 'w') as fh:
            fh.write("REMARK\n"
                     "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")
        alf = os.path.join(t.tmpdir, 'test.ali')
        with open(alf, 'w') as fh:
            fh.write("\n")

        data={'modkey': saliweb.test.get_modeller_key(),
              'model_file': open(pdbf),
              'alignment_file': open(alf),
              'job_name': 'test',
              'email': 'test@test.com'}
        rv = c.post('/job', data=data)
        self.assertEqual(rv.status_code, 200)
        r = re.compile('Your job has been submitted to the server! '
                       'Your job ID is testjob.*'
                       'notified at test@test.com when job results '
                       'are available',
                       re.MULTILINE | re.DOTALL)
        self.assertRegexpMatches(rv.data, r)

    def test_handle_seq_ident(self):
        """Test handle_seq_ident()"""
        # Default value
        self.assertEqual(evaluation.submit.handle_seq_ident(""), 30)

        # Correct value or percentage
        self.assertEqual(evaluation.submit.handle_seq_ident("42"), 42)
        self.assertEqual(evaluation.submit.handle_seq_ident("42%"), 42)

        # Not an integer
        self.assertRaises(saliweb.frontend.InputValidationError,
                          evaluation.submit.handle_seq_ident, "garbage")

        # Out of range value
        self.assertRaises(saliweb.frontend.InputValidationError,
                          evaluation.submit.handle_seq_ident, "-30")
        self.assertRaises(saliweb.frontend.InputValidationError,
                          evaluation.submit.handle_seq_ident, "300")


if __name__ == '__main__':
    unittest.main()
