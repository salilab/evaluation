import unittest
import saliweb.test
import saliweb.backend
import sys

class DummyPyLab(object):
    pass

class DummyAutoModel(object):
    pass

class DummyScripts(object):
    def complete_pdb(self, *args, **keys):
        pass

class DummyModeller(object):
    pass

class ScoreModellerTests(saliweb.test.TestCase):
    """Check score_modeller script"""

    def setUp(self):
        # Provide fake modules for pylab and modeller
        sys.modules['pylab'] = DummyPyLab
        sys.modules['modeller'] = DummyModeller
        sys.modules['modeller.automodel'] = DummyAutoModel
        sys.modules['modeller.scripts'] = DummyScripts
        import evaluation.score_modeller
        self.scoremod = evaluation.score_modeller

    def tearDown(self):
        del sys.modules['pylab']
        del sys.modules['modeller']
        del sys.modules['modeller.automodel']
        del sys.modules['modeller.scripts']

    def test_get_profile(self):
        """Check get_profile function"""
        d = saliweb.test.RunInTempDir()
        f = open('profile', 'w')
        f.write('# comment\n')
        f.write('short\n')
        f.write('1.0 2.0 3.0 4.0\n')
        f.write('5.0 6.0 7.0\n')
        f.close()
        vals = self.scoremod.get_profile('profile')
        self.assertEqual(vals, [4.0, 7.0])

    def test_get_options(self):
        """Check get_options function"""
        old_argv = sys.argv
        try:
            sys.argv = ['foo', '--model', 'test.pdb', '--seq_ident', '50.0']
            opts = self.scoremod.get_options()
            self.assertEqual(opts.model, 'test.pdb')
            self.assertEqual(opts.seq_ident, '50.0')

            sys.argv = ['foo', '--seq_ident', '50.0']
            self.assertRaises(SystemExit, self.scoremod.get_options)
        finally:
            sys.argv = old_argv

if __name__ == '__main__':
    unittest.main()
