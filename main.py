"""Command-line interface for AI-powered invoice extraction."""
import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from invoice_extractor.core import ExtractionError, extract_image, validate

def main():
    parser = argparse.ArgumentParser(description='Extract structured JSON from an invoice image using AI.')
    parser.add_argument('image', nargs='?', help='Path to invoice PNG/JPG/WEBP image')
    parser.add_argument('--validate-sample', action='store_true', help='Validate manually transcribed reference JSON offline (no AI call)')
    parser.add_argument('-o', '--output', default='output/extracted_invoice.json', help='Output JSON file')
    parser.add_argument('--model', default='gemini-3.5-flash-lite', help='Gemini vision-capable model')
    args = parser.parse_args()
    load_dotenv()
    try:
        if args.validate_sample:
            fixture = Path(__file__).resolve().parent / 'sample_expected.json'
            invoice = json.loads(fixture.read_text(encoding='utf-8'))['invoice']
            print('OFFLINE DEMO: validating manually transcribed reference data; no AI extraction performed.', file=sys.stderr)
        else:
            if not args.image:
                parser.error('provide an invoice image or use --validate-sample')
            invoice = extract_image(args.image, model=args.model)
        result = {'invoice': invoice, 'validation': validate(invoice)}
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f'\nSaved: {target}')
        return 0 if result['validation']['status'] == 'passed' else 2
    except (ExtractionError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
