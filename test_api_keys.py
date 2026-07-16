#!/usr/bin/env python3
"""
test_api_keys.py — Test de connectivité API Anthropic et DeepSeek
Usage: python test_api_keys.py
"""
import os
import sys
from pathlib import Path

# Charger .env
from dotenv import load_dotenv
load_dotenv()

REPO = Path(__file__).parent


def test_anthropic():
    """Test Anthropic API avec claude-sonnet-4-5"""
    from anthropic import Anthropic

    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return False, "ANTHROPIC_API_KEY non défini"

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=10,
            messages=[{"role": "user", "content": "Reply: OK"}]
        )
        if response.content and len(response.content) > 0:
            return True, f"Anthropic OK - réponse: {response.content[0].text[:50]}"
        return False, "Anthropic: réponse vide"
    except Exception as e:
        return False, f"Anthropic erreur: {type(e).__name__}: {e}"


def test_deepseek():
    """Test DeepSeek API avec deepseek-v4-flash"""
    from openai import OpenAI

    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        return False, "DEEPSEEK_API_KEY non défini"

    try:
        client = OpenAI(base_url="https://api.deepseek.com/v1", api_key=key)
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            max_tokens=10,
            messages=[{"role": "user", "content": "Reply: OK"}]
        )
        if response.choices and len(response.choices) > 0:
            return True, f"DeepSeek OK - réponse: {response.choices[0].message.content[:50]}"
        return False, "DeepSeek: réponse vide"
    except Exception as e:
        return False, f"DeepSeek erreur: {type(e).__name__}: {e}"


def main():
    print("🔑 Test des clés API Agora")
    print("=" * 50)

    ok_anthropic, msg_anthropic = test_anthropic()
    print(f"{'✅' if ok_anthropic else '❌'} Anthropic: {msg_anthropic}")

    ok_deepseek, msg_deepseek = test_deepseek()
    print(f"{'✅' if ok_deepseek else '❌'} DeepSeek: {msg_deepseek}")

    print("=" * 50)
    if ok_anthropic and ok_deepseek:
        print("🎉 Les deux APIs sont accessibles !")
        return 0
    else:
        print("⚠️  Au moins une API a échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())