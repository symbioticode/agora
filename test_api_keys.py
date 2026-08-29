#!/usr/bin/env python3
"""
test_api_keys.py — Test de connectivité API Anthropic et DeepSeek
Usage: python test_api_keys.py
"""
import os
import sys
from pathlib import Path

import pytest

# Charger .env
from dotenv import load_dotenv
load_dotenv()

REPO = Path(__file__).parent


def check_anthropic():
    """Test Anthropic API avec claude-sonnet-5"""
    from anthropic import Anthropic

    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return False, "ANTHROPIC_API_KEY non défini"

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=64,
            messages=[{"role": "user", "content": "Reply: OK"}]
        )
        if response.content and len(response.content) > 0:
            return True, f"Anthropic OK - réponse: {response.content[0].text[:50]}"
        return False, "Anthropic: réponse vide"
    except Exception as e:
        return False, f"Anthropic erreur: {type(e).__name__}: {e}"


def check_deepseek():
    """Test DeepSeek API avec deepseek-v4-flash"""
    from openai import OpenAI

    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        return False, "DEEPSEEK_API_KEY non défini"

    try:
        client = OpenAI(base_url="https://api.deepseek.com/v1", api_key=key)
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            # Un plafond de 10 peut être entièrement consommé par le
            # raisonnement du modèle et produire un faux « contenu vide ».
            max_tokens=512,
            messages=[{"role": "user", "content": "Reply: OK"}]
        )
        if response.choices:
            choice = response.choices[0]
            content = (choice.message.content or "").strip()
            if content:
                return True, f"DeepSeek OK - réponse: {content[:50]} (fin={choice.finish_reason})"
            reasoning_seen = bool(getattr(choice.message, "reasoning_content", None))
            return False, (
                "DeepSeek: réponse finale vide "
                f"(fin={choice.finish_reason}, raisonnement_present={reasoning_seen})"
            )
        return False, "DeepSeek: aucun choix retourné"
    except Exception as e:
        return False, f"DeepSeek erreur: {type(e).__name__}: {e}"


@pytest.mark.skipif(os.getenv("RUN_API") != "1", reason="Nécessite RUN_API=1 (appel API)")
def test_anthropic():
    ok, message = check_anthropic()
    assert ok, message


@pytest.mark.skipif(os.getenv("RUN_API") != "1", reason="Nécessite RUN_API=1 (appel API)")
def test_deepseek():
    ok, message = check_deepseek()
    assert ok, message


def main():
    if os.getenv("RUN_API") != "1":
        print("Refus: définir RUN_API=1 pour autoriser les appels API.", file=sys.stderr)
        return 2
    print("🔑 Test des clés API Agora")
    print("=" * 50)

    ok_anthropic, msg_anthropic = check_anthropic()
    print(f"{'✅' if ok_anthropic else '❌'} Anthropic: {msg_anthropic}")

    ok_deepseek, msg_deepseek = check_deepseek()
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
