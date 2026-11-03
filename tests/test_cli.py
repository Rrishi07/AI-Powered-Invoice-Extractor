"""CLI smoke tests that do not need an API key or network access."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CLITests(unittest.TestCase):
    def test_validate_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'result.json'
            process = subprocess.run([sys.executable, 'main.py', '--validate-sample', '-o', str(target)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(target.read_text(encoding='utf-8'))
            self.assertEqual(result['validation']['status'], 'passed')
            self.assertEqual(result['invoice']['total_amount'], 113565.0)

    def test_invalid_image_path(self):
        process = subprocess.run([sys.executable, 'main.py', 'samples/not_found.png'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 1)
        self.assertIn('File not found', process.stderr)
