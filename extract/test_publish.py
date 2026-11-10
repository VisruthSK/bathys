"""Check the public export: python3 -m unittest discover -s extract -p test_publish.py."""

import unittest

from publish import OUTPUT, PUBLIC_FILES, ROOT, publish


class Publication(unittest.TestCase):
    def test_export_contains_only_public_files(self):
        publish()
        (OUTPUT / "stale.txt").write_text("stale output must not be published")
        publish()
        actual = {
            file.relative_to(OUTPUT).as_posix()
            for file in OUTPUT.rglob("*")
            if file.is_file()
        }
        self.assertEqual(actual, set(PUBLIC_FILES))
        for name in PUBLIC_FILES:
            self.assertEqual(
                (ROOT / name).read_bytes(), (OUTPUT / name).read_bytes(), name
            )
        self.assertNotIn("extract/build.py", actual)
        self.assertNotIn("proof.html", actual)


if __name__ == "__main__":
    unittest.main()
