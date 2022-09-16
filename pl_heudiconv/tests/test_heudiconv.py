from unittest import TestCase, mock
from pl_heudiconv.heudiconv import Heudiconv
import base64, os, shutil, tempfile

class HeudiconvTests(TestCase):
    """
    Test Heudiconv.
    """
    def setUp(self):
        self.app = Heudiconv()
        self.inputdir = os.path.join(os.getcwd(), 'pl_heudiconv/tests/mock/inputdir')
        self.outputdir = tempfile.mkdtemp()

    def test_run(self):
        """
        Test the run code.
        """
        args = []
        args.append(self.inputdir)
        args.append(self.outputdir)

        options = self.app.parse_args(args)
        self.assertEqual(options.inputdir, self.inputdir)
        self.assertEqual(options.outputdir, self.outputdir)

        self.app.run(options)

        expected_files = ['CHANGES', 'README', 'dataset_description.json', 'participants.json', 'participants.tsv', 'scans.json']
        for expected in expected_files:
            self.assertTrue(os.path.exists(os.path.join(
                self.outputdir, 'Knee/(R)/', expected)))

    def tearDown(self):
        shutil.rmtree(self.outputdir)
