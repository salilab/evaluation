import unittest
import evaluation
import os

class ConfigTest(unittest.TestCase):
    """Check Config class"""
    def test_init(self):
        """Check Config init"""
        with open('config', 'w') as fh:
            fh.write("""
[general]
admin_email: test@salilab.org
service_name: test_service
socket: test.socket

[backend]
user: test
state_file: state_file
check_minutes: 10

[database]
db: testdb
frontend_config: frontend.conf
backend_config: backend.conf
[directories]
install: /
incoming: /in
preprocessing: /preproc

[oldjobs]
archive: 1d
expire: 1d

[scoring]
evaluation_script: score_tsvmod.pl
modeller_setup: module load modeller
modeller_script: score_modeller.py
""")
        c = evaluation.Config('config')
        self.assertEqual(c.evaluation_script, 'score_tsvmod.pl')
        self.assertEqual(c.modeller_setup, 'module load modeller')
        self.assertEqual(c.modeller_script, 'score_modeller.py')
        os.unlink('config')


if __name__ == '__main__':
    unittest.main()
