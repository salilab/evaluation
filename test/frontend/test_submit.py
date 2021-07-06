import unittest
import saliweb.test
import tempfile
import os
import re

# Import the modeval frontend with mocks
evaluation = saliweb.test.import_mocked_frontend("evaluation", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):
    """Check submit page"""

    def test_submit_page(self):
        """Test submit page"""
        with tempfile.TemporaryDirectory() as tmpdir:
            incoming = os.path.join(tmpdir, 'incoming')
            os.mkdir(incoming)
            evaluation.app.config['DIRECTORIES_INCOMING'] = incoming
            c = evaluation.app.test_client()
            rv = c.post('/job')
            self.assertEqual(rv.status_code, 400)  # no license key

            modkey = saliweb.test.get_modeller_key()
            data = {'modkey': modkey}
            rv = c.post('/job', data=data)
            self.assertEqual(rv.status_code, 400)  # no pdb file

            pdbf = os.path.join(tmpdir, 'test.pdb')
            with open(pdbf, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")

            # Successful submission (no email)
            data['pdb_file'] = open(pdbf, 'rb')
            rv = c.post('/job', data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 503)  # job not finished yet
            r = re.compile(b'Your job has been submitted.*You can check on',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

            # Successful submission (with email)
            data['email'] = 'test@test.com'
            data['pdb_file'] = open(pdbf, 'rb')
            rv = c.post('/job', data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 503)  # job not finished yet
            r = re.compile(
                b'Your job has been submitted.*You will be notified.*'
                b'You can check on', re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def test_submit_page_alignment(self):
        """Test submit page with alignment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            incoming = os.path.join(tmpdir, 'incoming')
            os.mkdir(incoming)
            evaluation.app.config['DIRECTORIES_INCOMING'] = incoming
            c = evaluation.app.test_client()

            pdbf = os.path.join(tmpdir, 'test.pdb')
            with open(pdbf, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")
            alf = os.path.join(tmpdir, 'test.ali')
            with open(alf, 'w') as fh:
                fh.write("\n")

            data = {'modkey': saliweb.test.get_modeller_key(),
                    'pdb_file': open(pdbf, 'rb'),
                    'alignment_file': open(alf, 'rb'),
                    'name': 'testjob',
                    'email': 'test@test.com'}
            rv = c.post('/job', data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 503)  # job not finished yet
            r = re.compile(b'Your job has been submitted to the server!.*'
                           b'Your job ID is testjob.*'
                           b'notified at test@test.com when job results '
                           b'are available',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def test_submit_page_xml(self):
        """Test submit page with XML output forced"""
        with tempfile.TemporaryDirectory() as tmpdir:
            incoming = os.path.join(tmpdir, 'incoming')
            os.mkdir(incoming)
            evaluation.app.config['DIRECTORIES_INCOMING'] = incoming
            c = evaluation.app.test_client()

            pdbf = os.path.join(tmpdir, 'test.pdb')
            with open(pdbf, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")

            modkey = saliweb.test.get_modeller_key()
            rv = c.post('/job',
                        data={'modkey': modkey,
                              'model_file': open(pdbf, 'rb')})
            self.assertEqual(rv.status_code, 200)
            r = re.compile(rb'<\?xml.*<job xlink:href=.*&amp;force_xml=1',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

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
