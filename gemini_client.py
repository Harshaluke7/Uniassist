"""Thin wrapper around the Google Gemini API (google-genai SDK). Never raises: returns (text, error)."""
import config

_client = None


def available() -> bool:
    return bool(config.GEMINI_API_KEY)


def _get():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def generate(contents):
    """contents: a prompt string, or a list like [prompt, PIL.Image]. Returns (text|None, error|None)."""
    if not available():
        return None, "GEMINI_API_KEY is not set"
    try:
        resp = _get().models.generate_content(model=config.GEMINI_MODEL, contents=contents)
        return (resp.text or "").strip(), None
    except Exception as exc:  # network, quota, bad key ...
        return None, str(exc)
