
import os
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "rpath.py"


def run_cli(args, cwd=None):
    env = os.environ.copy()
    # Avoid clipboard interactions by hiding pbcopy from PATH
    env["PATH"] = ""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd if cwd is not None else ROOT,
        text=True,
        capture_output=True,
    )
    return result


class TestRPathCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)
        # Create a couple of files
        (self.tmpdir / "a.txt").write_text("A")
        (self.tmpdir / "b.txt").write_text("B")
        self.a = "a.txt"
        self.b = "b.txt"
        self.missing = "missing.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_multiple_files_space_sep(self):
        res = run_cli([self.a, self.b], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        b_abs = os.path.realpath(str(self.tmpdir / self.b))
        self.assertEqual(res.stdout, f"{a_abs} {b_abs}\n")
        self.assertEqual(res.stderr, "")

    def test_enquote_affects_stdout_and_stderr_warn(self):
        # Include a missing file to trigger stderr; enquote should wrap names
        res = run_cli(["-q", self.a, self.missing], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        missing_abs = os.path.realpath(str(self.tmpdir / self.missing))
        self.assertEqual(res.stdout, f'"{a_abs}" "{missing_abs}"\n')
        self.assertEqual(res.stderr, f'"{self.missing}" does not exist!\n')

    def test_field_separator_tab(self):
        # Use escaped tab separator and two existing files
        res = run_cli(["-F", "\\t", self.a, self.b], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        b_abs = os.path.realpath(str(self.tmpdir / self.b))
        self.assertEqual(res.stdout, f"{a_abs}\t{b_abs}\n")
        self.assertEqual(res.stderr, "")

    def test_e_ignore_prints_missing_no_stderr(self):
        res = run_cli(["-e", "ignore", self.missing], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        missing_abs = os.path.realpath(str(self.tmpdir / self.missing))
        self.assertEqual(res.stdout, f"{missing_abs}\n")
        self.assertEqual(res.stderr, "")

    def test_e_ignore_skip_skips_missing(self):
        # With one existing and one missing, only existing printed
        res = run_cli(["-e", "ignoreSkip", self.a, self.missing], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        self.assertEqual(res.stdout, f"{a_abs}\n")
        self.assertEqual(res.stderr, "")

    def test_e_exit_silent_exits_without_error(self):
        # First file printed, then exit silently on missing
        res = run_cli(["-e", "exitSilent", self.a, self.missing], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        self.assertEqual(res.stdout, f"{a_abs}\n")
        self.assertEqual(res.stderr, "")

    def test_e_exit_exits_after_error(self):
        # First file printed, then error + exit on missing
        res = run_cli(["-e", "exit", self.a, self.missing], cwd=self.tmpdir)
        self.assertEqual(res.returncode, 0)
        a_abs = os.path.realpath(str(self.tmpdir / self.a))
        self.assertEqual(res.stdout, f"{a_abs}\n")
        self.assertEqual(res.stderr, f"{self.missing} does not exist!\n")