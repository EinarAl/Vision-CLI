#!/usr/bin/env python3
"""
vision — CLI tool for image analysis via Google Gemini API.

Usage:
  python vision.py path/to/image.jpg
  python vision.py path/to/image.jpg "What UI framework is this?"
  python vision.py path/to/image.jpg --model gemini-2.5-flash

Requires GEMINI_API_KEY environment variable.
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image


API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.0-flash"
MAX_DIM = 1024


def resize_image(image: Image.Image, max_dim: int = MAX_DIM) -> Image.Image:
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)
    return image


def encode_image(image_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    img = resize_image(img)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def analyze(
    image_path: str,
    prompt: str = "Describe this image in detail.",
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> str:
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Error: GEMINI_API_KEY not set. Provide via --key or GEMINI_API_KEY env var.")

    img_b64 = encode_image(image_path)
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64,
                    }
                },
            ]
        }],
        "safetySettings": [
            {"category": f"HARM_CATEGORY_{c}", "threshold": "BLOCK_ONLY_HIGH"}
            for c in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
        ],
    }

    resp = requests.post(url, json=payload, timeout=30)
    data = resp.json()

    if "candidates" not in data or not data["candidates"]:
        reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
        sys.exit(f"Error: Request blocked or empty response ({reason}).")

    return data["candidates"][0]["content"]["parts"][0]["text"]


def main():
    parser = argparse.ArgumentParser(description="Analyze images with Gemini.")
    parser.add_argument("image", type=str, help="Path to image file")
    parser.add_argument("prompt", type=str, nargs="?", default="Describe this image in detail.",
                        help="Optional prompt (default: describe the image)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Gemini model (default: {DEFAULT_MODEL})")
    parser.add_argument("--key", type=str, default=None,
                        help="Gemini API key (falls back to GEMINI_API_KEY env var)")

    args = parser.parse_args()

    if not os.path.isfile(args.image):
        sys.exit(f"Error: File not found: {args.image}")

    result = analyze(args.image, args.prompt, args.model, args.key)
    print(result)


if __name__ == "__main__":
    main()
