import unittest
import saliweb.test

# Import the modeval frontend with mocks
evaluation = saliweb.test.import_mocked_frontend("evaluation", __file__,
                                                 '../../frontend')


class Tests(saliweb.test.TestCase):

    def test_index(self):
        """Test index page"""
        c = evaluation.app.test_client()
        rv = c.get('/')
        self.assertIn('An evaluation tool for protein structure models',
                      rv.data)

    def test_contact(self):
        """Test contact page"""
        c = evaluation.app.test_client()
        rv = c.get('/contact')
        self.assertIn('Please address inquiries to', rv.data)

    def test_help(self):
        """Test help page"""
        c = evaluation.app.test_client()
        rv = c.get('/help')
        self.assertIn('DOPE is based on an improved reference state', rv.data)

    def test_queue(self):
        """Test queue page"""
        c = evaluation.app.test_client()
        rv = c.get('/job')
        self.assertIn('No pending or running jobs', rv.data)


if __name__ == '__main__':
    unittest.main()
