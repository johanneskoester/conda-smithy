from contextlib import contextmanager
import os
import shutil
import tempfile
import unittest

import conda_build.metadata
import conda.api

import conda_smithy.configure_feedstock as cnfgr_fdstk


@contextmanager
def tmp_directory():
    tmp_dir = tempfile.mkdtemp('recipe_')
    yield tmp_dir
    shutil.rmtree(tmp_dir)


class Test_fudge_subdir(unittest.TestCase):
    def test_metadata_reading(self):
        with tmp_directory() as recipe_dir:
            with open(os.path.join(recipe_dir, 'meta.yaml'), 'w') as fh:
                fh.write("""
                        package:
                           name: foo_win  # [win]
                           name: foo_osx  # [osx]
                           name: foo_the_rest  # [not (win or osx)]
                         """)
            meta = conda_build.metadata.MetaData(recipe_dir)
            with cnfgr_fdstk.fudge_subdir('win-64'):
                meta.parse_again()
                self.assertEqual(meta.name(), 'foo_win')

            with cnfgr_fdstk.fudge_subdir('osx-64'):
                meta.parse_again()
                self.assertEqual(meta.name(), 'foo_osx')

    def test_fetch_index(self):
        # Get the index for OSX and Windows. They should be different.

        with cnfgr_fdstk.fudge_subdir('win-64'):
            win_index = conda.api.get_index()
        with cnfgr_fdstk.fudge_subdir('osx-64'):
            osx_index = conda.api.get_index()
        self.assertNotEqual(win_index.keys(), osx_index.keys(),
                            ('The keys for the Windows and OSX index were the same.'
                             ' Subdir is not working and will result in mis-rendering '
                             '(e.g. https://github.com/SciTools/conda-build-all/issues/49).'))



if __name__ == '__main__':
    unittest.main()