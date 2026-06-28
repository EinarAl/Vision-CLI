# Vision CLI

Minimal CLI tool for image analysis via Google Gemini. Single-file, zero telemetry, communicates only with the Gemini API.

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
```

## Usage

```bash
python vision.py screenshot.png
python vision.py diagram.jpg "Explain this architecture"
python vision.py photo.png --model gemini-2.5-flash
```

## How it works

1. Reads image → resizes to max 1024px → JPEG @85 quality → base64
2. Sends to `gemini-2.0-flash` (or specified model) via Gemini API
3. Prints the AI description

## Security

- API key read from `GEMINI_API_KEY` env var or `--key` flag (never hardcoded)
- Only outbound connection: `generativelanguage.googleapis.com:443`
- No telemetry, no analytics, no data storage
