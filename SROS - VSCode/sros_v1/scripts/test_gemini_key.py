"""
Safe Gemini key test script

Usage (dry-run):
  python scripts/test_gemini_key.py --prompt "Hello" 

To perform a live call (only run if you trust your environment):
  python scripts/test_gemini_key.py --prompt "Hello" --do-call

Environment variables:
  GEMINI_API_KEY      - your Gemini API key (sensitive)
  GEMINI_AUTH_METHOD - optional: 'bearer' or 'key' (default: 'bearer')
  GEMINI_BASE_URL     - optional base URL (default: https://generativelanguage.googleapis.com)
  GEMINI_MODEL        - optional model name (default: gemini-2.0-flash)

The script supports a dry-run mode that prints the exact request it will make.
"""
from __future__ import annotations
import os
import argparse
import json
from typing import Dict

try:
    import requests
except Exception:
    requests = None


def build_request(prompt: str) -> Dict:
    base = os.environ.get('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com')
    model = os.environ.get('GEMINI_MODEL', 'gemini-pro')
    # Google Generative Language API format: v1beta/models/MODEL:generateContent
    endpoint = f"{base}/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        # Minimal example; adapt to your API variant if needed
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 256
        }
    }

    auth_method = os.environ.get('GEMINI_AUTH_METHOD', 'key').lower()
    api_key = os.environ.get('GEMINI_API_KEY')

    headers = {
        'Content-Type': 'application/json'
    }

    if api_key and auth_method == 'bearer':
        headers['Authorization'] = f"Bearer {api_key}"

    return {
        'endpoint': endpoint,
        'payload': payload,
        'headers': headers,
        'api_key': api_key,
        'auth_method': auth_method
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', '-p', type=str, required=True, help='Prompt text')
    parser.add_argument('--do-call', action='store_true', help='Perform live HTTP call (make sure env vars are set)')
    args = parser.parse_args()

    req = build_request(args.prompt)

    print('\n=== Gemini Key Test - Dry Run ===')
    print('Endpoint: ', req['endpoint'])
    print('Auth method:', req['auth_method'])
    print('Headers:')
    for k, v in req['headers'].items():
        # Do not print full auth header value to avoid leaking to logs; show masked
        if k.lower() in ('authorization', 'x-api-key') and v:
            print(f"  {k}: <REDACTED>")
        else:
            print(f"  {k}: {v}")
    print('Payload:')
    print(json.dumps(req['payload'], indent=2))

    if not args.do_call:
        print('\nDry-run complete. To perform a live request, re-run with --do-call.\n')
        print('Example curl (if using bearer token):')
        print("curl -X POST '{url}' -H 'Content-Type: application/json' -H 'Authorization: Bearer $GEMINI_API_KEY' -d '{payload}'".format(url=req['endpoint'], payload=json.dumps(req['payload'])))
        return

    if not requests:
        print('\nError: requests library not available. Install with: pip install requests')
        return

    if not req['api_key']:
        print('\nError: GEMINI_API_KEY environment variable not set. Aborting live call.')
        return

    print('\nPerforming live request...')
    try:
        # If auth method == key, attach as ?key=API_KEY
        if req['auth_method'] == 'key':
            resp = requests.post(req['endpoint'] + f"?key={req['api_key']}", headers=req['headers'], json=req['payload'], timeout=20)
        else:
            resp = requests.post(req['endpoint'], headers=req['headers'], json=req['payload'], timeout=20)

        print('HTTP status:', resp.status_code)
        try:
            data = resp.json()
            print('Response JSON:')
            print(json.dumps(data, indent=2))
        except Exception:
            print('Response text:')
            print(resp.text)

    except Exception as e:
        print('Request failed:', str(e))


if __name__ == '__main__':
    main()
