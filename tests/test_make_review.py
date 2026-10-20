"""Checks for the standalone review writer."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE = json.loads((ROOT / "examples/lumen-cell/review.json").read_text(encoding="utf-8"))


class MakeReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = pathlib.Path(self.tmp.name) / "review"
        self.folder.mkdir()
        self.review = json.loads(json.dumps(SAMPLE))

    def run_writer(self):
        (self.folder / "review.json").write_text(json.dumps(self.review), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(ROOT / "make_review.py"), str(self.folder)],
            text=True, capture_output=True, check=False,
        )

    def assert_rejected(self, message):
        result = self.run_writer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)
        self.assertFalse(list(self.folder.glob("* Review.html")))

    def test_script_breakout_is_escaped(self):
        attack = '</script><img src=x onerror=alert(1)><!--\u2028\u2029&'
        self.review["stops"][0]["text"] = [attack]
        result = self.run_writer()
        self.assertEqual(result.returncode, 0, result.stderr)
        html = next(self.folder.glob("* Review.html")).read_text(encoding="utf-8")
        self.assertNotIn(attack, html)
        self.assertIn("\\u003c/script\\u003e", html)
        self.assertIn("\\u2028\\u2029", html)
        block = html.split("const REVIEW = ", 1)[1].split(";\n/* ================== END OF EDITABLE BLOCK", 1)[0]
        self.assertEqual(json.loads(block)["stops"][0]["text"], [attack])

    def test_path_traversal_is_rejected(self):
        self.review["stops"][0]["img"] = "../outside.png"
        self.assert_rejected("must stay inside")

    def test_absolute_image_path_is_rejected(self):
        self.review["stops"][0]["img"] = "/tmp/outside.png"
        self.assert_rejected("must stay inside")

    def test_symlink_outside_folder_is_rejected(self):
        target = pathlib.Path(self.tmp.name) / "outside.png"
        target.write_bytes(b"png")
        (self.folder / "link.png").symlink_to(target)
        self.review["stops"][0]["img"] = "link.png"
        self.assert_rejected("must stay inside")

    def test_oversized_image_is_rejected(self):
        image = self.folder / "large.png"
        with image.open("wb") as stream:
            stream.truncate(5 * 1024 * 1024 + 1)
        self.review["stops"][0]["img"] = "large.png"
        self.assert_rejected("over 5 MB")

    def test_bad_page_is_rejected(self):
        self.review["stops"][0]["page"] = "<b>1</b>"
        self.assert_rejected("whole page number")

    def test_duplicate_change_id_is_rejected(self):
        self.review["stops"][1]["id"] = self.review["stops"][0]["id"]
        self.assert_rejected("unique id")

    def test_duplicate_question_id_is_rejected(self):
        self.review["questions"][1]["id"] = self.review["questions"][0]["id"]
        self.assert_rejected("unique id")

    def test_missing_linked_change_is_rejected(self):
        self.review["questions"][0]["stop"] = "missing"
        self.assert_rejected("does not exist")

    def test_identity_is_saved_once(self):
        del self.review["reviewId"]
        del self.review["questions"][0]["id"]
        first = self.run_writer()
        self.assertEqual(first.returncode, 0, first.stderr)
        saved = json.loads((self.folder / "review.json").read_text(encoding="utf-8"))
        self.assertTrue(saved["reviewId"])
        self.assertTrue(saved["questions"][0]["id"])
        self.review = saved
        second = self.run_writer()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(saved, json.loads((self.folder / "review.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
