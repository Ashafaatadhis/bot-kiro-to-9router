#!/usr/bin/env python3
"""
Check the latest token and test 9router API
"""

import requests
import json
import base64

def test_9router_api(token):
    """Test sending token to 9router"""
    print(f"\nTesting 9router API with token...")
    print(f"Token: {token[:50]}...")

    # Try different payload formats
    payloads = [
        {"refreshToken": token},
        {"token": token},
        {"refresh_token": token},
        {"refreshToken": token, "source": "kiro_bot"},
        {"refresh_token": token, "provider": "kiro"}
    ]

    for i, payload in enumerate(payloads, 1):
        print(f"\nTest {i}: {json.dumps(payload)}")

        try:
            response = requests.post(
                "http://localhost:20128/api/oauth/kiro/import",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            print(f"Status: {response.status_code}")
            if response.text:
                print(f"Response: {response.text[:200]}")

                if response.status_code == 401:
                    print("401 Unauthorized - Check:")
                    print("1. Is 9router running on localhost:20128?")
                    print("2. Does the endpoint require authentication?")
                    print("3. Is the token format correct?")

        except Exception as e:
            print(f"Error: {e}")

def decode_token_if_jwt(token):
    """Try to decode token if it's JWT"""
    print(f"\nAnalyzing token format...")

    # Check token characteristics
    print(f"Token length: {len(token)}")
    print(f"First 20 chars: {token[:20]}")

    # Check if it looks like JWT (has dots)
    if '.' in token:
        parts = token.split('.')
        print(f"Looks like JWT with {len(parts)} parts")

        try:
            for i, part in enumerate(parts):
                if i < 2:  # Header and payload
                    try:
                        # Add padding for base64 decode
                        decoded = base64.b64decode(part + '==')
                        print(f"Part {i}: {decoded[:50]}...")
                    except:
                        print(f"Part {i}: Not base64")
        except Exception as e:
            print(f"Decode error: {e}")
    else:
        print("Not a JWT format (no dots)")

def main():
    # Get token from user
    token = input("Enter token to test (or leave empty to use default): ").strip()

    if not token:
        # Try to get from tokens.json
        try:
            with open('tokens.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('tokens'):
                token = list(data['tokens'].values())[0]
                print(f"Using token from tokens.json")
            else:
                token = "1783100894450-8e4x9l3y2fi"  # Example from log
                print(f"Using example token from log")
        except:
            token = "1783100894450-8e4x9l3y2fi"  # Example from log
            print(f"Using example token from log")

    decode_token_if_jwt(token)
    test_9router_api(token)

if __name__ == "__main__":
    print("=" * 60)
    print("9ROUTER API TESTER")
    print("=" * 60)
    main()