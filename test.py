"""
This module provide simple tests units.
"""
import io
import os
import unittest
from contextlib import redirect_stdout

from geojpg import main

base_dir = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """Unit test Test Case"""

    def test_1(self):
        """Case where jpg dates earlier gpx"""
        buf = io.StringIO()
        subfolder = './test/1/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn("26 files updated", buf.getvalue())
        self.assertIn(
            "before tracking: IMG_1116_11-31-13.JPG, IMG_1122_11-33-25.JPG",
            buf.getvalue(),
        )

    def test_2(self):
        """Case where jpg dates later gpx"""
        buf = io.StringIO()
        subfolder = './test/2/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn("6 files updated", buf.getvalue())
        self.assertIn(
            "after tracking: IMG_1299_12-51-32.JPG, IMG_1383_13-41-55.JPG",
            buf.getvalue(),
        )

    def test_3(self):
        """Case where jpg dates earlier and later gpx"""
        buf = io.StringIO()
        subfolder = './test/3/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 3 files updated",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made before tracking: IMG_1116_11-31-13.JPG",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made after tracking: IMG_1383_13-41-55.JPG",
            buf.getvalue(),
        )

    def test_4(self):
        """Case where jpg dates narrower gpx"""
        buf = io.StringIO()
        subfolder = './test/4/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 3 files updated",
            buf.getvalue(),
        )

    def test_5(self):
        """Case where there is gap inside gpx, all jpg within 15 min"""
        buf = io.StringIO()
        subfolder = './test/5/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 8 files updated",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made before tracking: IMG_1122_11-33-25.JPG",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made after tracking: IMG_1383_13-41-55.JPG",
            buf.getvalue(),
        )

    def test_6(self):
        """Case where there is wide gap inside gpx, some jpg within 15 min"""
        buf = io.StringIO()
        subfolder = './test/6/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 5 files updated",
            buf.getvalue(),
        )
        self.assertIn(
            "made before tracking: IMG_1116_11-31-13.JPG, IMG_1299_12-51-32.JPG",
            buf.getvalue(),
        )
        self.assertIn(
            "seemed made after tracking: IMG_1282_12-40-29.JPG",
            buf.getvalue(),
        )

    def test_7(self):
        """Case where no files update, jpg dates after gpx"""
        buf = io.StringIO()
        subfolder = './test/7/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Finished, but no files updated :(",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made after tracking: IMG_1367_13-26-52.JPG",
            buf.getvalue(),
        )

    def test_8(self):
        """Case where all jpgs before gpx, some within 15 min"""
        buf = io.StringIO()
        subfolder = './test/8/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 1 files updated",
            buf.getvalue(),
        )
        self.assertIn(
            "1 file(s) not updated, seemed made before tracking: IMG_1116_11-31-13.JPG",
            buf.getvalue(),
        )

    def test_9(self):
        """Case with 3 gpx with duplicates"""
        buf = io.StringIO()
        subfolder = './test/9/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Nice. 2 files updated",
            buf.getvalue(),
        )
        self.assertIn(
            "Duplicates removed: 3325\nGot 7533 gps points",
            buf.getvalue(),
        )

    def test_10(self):
        """Case with no gpx files"""
        buf = io.StringIO()
        subfolder = './test/10/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "START\n\nRead gpx...No gpx files found!\nIt took 0.0 seconds\n\nFINISH",
            buf.getvalue(),
        )

    def test_11(self):
        """Case with no jpg files"""
        buf = io.StringIO()
        subfolder = './test/11/'
        folder_gpx = os.path.join(base_dir, subfolder)
        folder_jpg = folder_gpx
        with redirect_stdout(buf):
            main(folder_gpx, folder_jpg)
        self.assertIn(
            "Read jpg...\nNo JPG files in folder!",
            buf.getvalue(),
        )


if __name__ == '__main__':
    unittest.main()
