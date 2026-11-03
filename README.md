# AI-Powered Invoice Data Extraction

A small, maintainable Python CLI that uses an Google Gemini vision model to extract invoice data from an image into JSON and then **independently validates the financial arithmetic** using Python `Decimal`.

## Features

- Image inputs: PNG, JPG/JPEG, WEBP (up to 15 MB)
- AI extraction of invoice number, date, supplier, currency, line items, subtotal, tax and grand total
- JSON output with normalized dates and numeric values
- Line-item, subtotal, tax and grand-total validation (tolerance NPR 0.01)
- Missing-field and inconsistent-amount warnings; original extracted values are preserved
- Friendly error handling for bad input, missing API key, API failures and timeouts
- Automated unit tests, including negative cases

## Requirements

Python 3.10+ and a **Gemini API key** with access to `gemini-3.5-flash-lite`. Free-tier availability and limits depend on the account and region.

## Installation (Windows PowerShell)

```powershell
cd invoice_ai_submission
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `replace_with_your_gemini_api_key` with your own key. **Never commit or email the `.env` file.**

## Run

```powershell
python main.py samples/rivertech_invoice.png -o output/result.json
```

To use a different image:

```powershell
python main.py "C:\\path\\to\\invoice.jpg" -o output/another_invoice.json
```

For a different vision-capable model, supply `--model MODEL_NAME`.

## Offline demonstration (no API key required)

```powershell
python main.py --validate-sample -o output/sample_validation.json
```

This command **does not perform AI extraction**. It independently validates the manually transcribed reference data from `sample_expected.json` and writes a fresh JSON result. It is useful for evaluating arithmetic checks without spending API credits.

## Test without an API key

```powershell
python -m unittest discover -s tests -v
```

This verifies normalization and financial checks; it **does not** test live AI extraction. Live extraction requires your API key and network access.

## JSON output

The root object has `invoice` and `validation`. `invoice.items` contains `description`, `quantity`, `unit`, `unit_price`, `line_total` and `line_number`. `validation` contains a `status` (`passed` or `review_required`), `checks`, and `warnings`. Missing values are `null`, never invented. The app exits with code 0 on passed validation, 2 when review is required, and 1 for execution errors.

`sample_expected.json` is a **manually transcribed reference fixture** from the supplied invoice, not a claim of live AI extraction. The actual generated result is `output/result.json` after running with an API key.

## Design decisions

1. **AI for perception, deterministic code for verification:** OCR/vision handles variable layouts; `Decimal` avoids binary floating-point issues in validation.
2. **No silent correction:** the model's extracted values remain visible even when the totals disagree.
3. **Graceful uncertainty:** missing information produces warnings, not fabricated fields.
4. **Modularity:** extraction, normalization, validation and CLI are separate, allowing easy integration into a web service later.

## Limitations and future improvements

- AI may misread blurred, rotated, handwritten, or complex invoices; review flagged results.
- `null` checks mean information was missing, so financial validation could not be completed.
- The example is a single invoice; broader real-world accuracy needs evaluation on a varied invoice test set.
- This prototype handles image files, not multi-page PDFs. A production version should add PDF support, schema enforcement, retry/backoff, privacy controls and regression tests on multiple layouts.
- Images are sent to the selected external AI API; do not upload confidential invoices without authorization.

## Project structure

```text
invoice_ai_submission/
├── main.py
├── invoice_extractor/
│   ├── __init__.py
│   └── core.py
├── tests/test_core.py
├── samples/rivertech_invoice.png
├── sample_expected.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Submission checklist

1. Run the unit tests and offline demonstration.
2. Configure your own API key locally and run **real AI extraction** on `samples/rivertech_invoice.png`. Inspect `output/result.json` and ensure the values are correct.
3. Remove your local `.env` from any shared archive (the supplied `.gitignore` excludes it from Git).
4. Push the source to your own GitHub repository or attach the ZIP to your reply.
5. Mention clearly whether the live API test was performed.

### GitHub commands (after creating an empty repository)

```powershell
git init
git add .
git commit -m "Build AI invoice extraction and financial validation CLI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Never publish an API key or the `.env` file.

## Gemini integration

This version uses the Google `google-genai` SDK and defaults to `gemini-3.5-flash-lite`. It uses Gemini image input with JSON response mode, then applies the same independent `Decimal`-based validation. The free tier is subject to quotas and may change. A successful text-only connectivity test does **not** prove invoice-image extraction works: run the full invoice command and inspect its output before submission.
