"""Mocked Gemini extraction tests; no network or API key required."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from invoice_extractor.core import extract_image, ExtractionError
import importlib.util

HAS_GEMINI = importlib.util.find_spec("google.genai") is not None if importlib.util.find_spec("google") else False


SAMPLE = Path(__file__).resolve().parents[1] / 'samples' / 'rivertech_invoice.png'

class GeminiTests(unittest.TestCase):
    @unittest.skipUnless(HAS_GEMINI, "google-genai not installed in this environment")
    def test_extract_image_normalizes_json(self):
        response = MagicMock()
        response.text = json.dumps({'invoice_number': 'TEST-1', 'invoice_date': '2024-10-14',
            'supplier_name': 'Supplier', 'currency': 'NPR', 'items': [],
            'subtotal': 100, 'tax_rate_percent': 13, 'tax_amount': 13, 'total_amount': 113})
        with patch('google.genai.Client') as client:
            client.return_value.models.generate_content.return_value = response
            result = extract_image(SAMPLE, api_key='test-only-key')
        self.assertEqual(result['total_amount'], 113.0)
        self.assertEqual(result['invoice_number'], 'TEST-1')
        self.assertEqual(client.return_value.models.generate_content.call_args.kwargs['model'], 'gemini-3.5-flash-lite')

    def test_missing_gemini_key(self):
        with patch.dict('os.environ', {'GEMINI_API_KEY': ''}):
            with self.assertRaisesRegex(ExtractionError, 'GEMINI_API_KEY'):
                extract_image(SAMPLE)

    @unittest.skipUnless(HAS_GEMINI, "google-genai not installed in this environment")
    def test_invalid_json(self):
        response = MagicMock(text='not json')
        with patch('google.genai.Client') as client:
            client.return_value.models.generate_content.return_value = response
            with self.assertRaisesRegex(ExtractionError, 'invalid JSON'):
                extract_image(SAMPLE, api_key='test-only-key')
