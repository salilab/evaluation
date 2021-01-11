import unittest
import saliweb.test
import saliweb.backend
import sys


class DummyMatPlotLib(object):
    @staticmethod
    def use(*args, **keys):
        pass


class DummyPyLab(object):
    @staticmethod
    def figure(*args, **keys):
        pass

    @staticmethod
    def xlabel(*args, **keys):
        pass

    @staticmethod
    def ylabel(*args, **keys):
        pass

    @staticmethod
    def plot(*args, **keys):
        if DummyPyLab.error:
            raise ValueError("some error in pylab")

    @staticmethod
    def legend(*args, **keys):
        pass

    @staticmethod
    def savefig(*args, **keys):
        pass


class DummyAutoModel(object):
    pass


class DummyChain(object):
    def __init__(self, name):
        self.name = name
        self.residues = [0, 1, 2]


class DummyModel(object):
    def __init__(self):
        self.chains = [DummyChain(x) for x in ['', 'B']]
        if self.has_seq_id:
            self.seq_id = 37.0  # Simulate reading seq_id from PDB header

    def assess_normalized_dope(self):
        return -3.0

    def assess_ga341(self):
        if not hasattr(self, 'seq_id'):
            raise ValueError("Need to set seq_id")
        return (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0)


class DummyScripts(object):
    error = False

    def complete_pdb(*args, **keys):
        if DummyScripts.error:
            raise ValueError("Bad PDB")
        return DummyModel()
    complete_pdb = staticmethod(complete_pdb)


class DummyModeller(object):
    class log(object):
        def minimal(*args):
            pass
        minimal = staticmethod(minimal)

    class environ(object):
        class libs:
            class topology:
                def read(*args, **keys): pass
                read = staticmethod(read)

            class parameters:
                def read(*args, **keys): pass
                read = staticmethod(read)

    class selection(object):
        def __init__(self, *args):
            pass

        def assess_dope(self, *args, **keys):
            pass


class ScoreModellerTests(saliweb.test.TestCase):
    """Check score_modeller script"""

    def setUp(self):
        # Provide fake modules for pylab, matplotlib and modeller
        sys.modules['matplotlib'] = DummyMatPlotLib
        sys.modules['pylab'] = DummyPyLab
        sys.modules['modeller'] = DummyModeller
        sys.modules['modeller.automodel'] = DummyAutoModel
        sys.modules['modeller.scripts'] = DummyScripts
        import evaluation.score_modeller
        self.scoremod = evaluation.score_modeller

    def tearDown(self):
        del sys.modules['matplotlib']
        del sys.modules['pylab']
        del sys.modules['modeller']
        del sys.modules['modeller.automodel']
        del sys.modules['modeller.scripts']

    def test_get_profile(self):
        """Check get_profile function"""
        d = saliweb.test.RunInTempDir()
        with open('profile', 'w') as f:
            f.write('# comment\n')
            f.write('short\n')
            f.write('1.0 2.0 3.0 4.0\n')
            f.write('5.0 6.0 7.0\n')
        vals = self.scoremod.get_profile('profile')
        self.assertEqual(vals, [4.0, 7.0])
        del d

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

    def test_main(self):
        """Test score_modeller main function"""
        d = saliweb.test.RunInTempDir()
        old_argv = sys.argv
        try:
            DummyPyLab.error = True
            DummyModel.has_seq_id = True
            sys.argv = ['foo', '--model', 'test.pdb', '--seq_ident', '50.0']
            with open('input.profile_A', 'w') as fh:
                fh.write('1.0\n2.0\n')
            with open('input.profile_B', 'w') as fh:
                fh.write('3.0\n4.0\n')
            DummyScripts.error = True
            self.assertRaises(SystemExit, self.scoremod.main)
            self.assert_in_file('modeller.results', 'Not a valid PDB file')
            self.assert_in_file('modeller.results.xml', 'Not a valid PDB file')
            DummyScripts.error = False
            # Use seq_id from PDB header
            self.scoremod.main()
            self.assert_in_file('modeller.results.xml',
                                '<sequence_identity>37.0')
            # Use seq_id provided on command line
            DummyModel.has_seq_id = False
            self.scoremod.main()
            self.assert_in_file('modeller.results.xml',
                                '<sequence_identity>50.0')
            # Test with full pylab
            DummyPyLab.error = False
            self.scoremod.main()
            self.assert_in_file('modeller.results.xml',
                                '<sequence_identity>50.0')
            # No seq_id on command line
            sys.argv = ['foo', '--model', 'test.pdb']
            self.scoremod.main()
            with open('modeller.results.xml') as fh:
                contents = fh.read()
            self.assertEqual(contents, '')
        finally:
            sys.argv = old_argv
        del d

    def assert_in_file(self, fname, srch):
        with open(fname) as fh:
            contents = fh.read()
        self.assertIn(srch, contents,
                      "String %s not found in file %s contents: %s"
                      % (srch, fname, contents))


if __name__ == '__main__':
    unittest.main()
