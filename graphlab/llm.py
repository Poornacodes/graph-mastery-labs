"""One function, call_llm(prompt) -> str, behind four interchangeable
providers. Choose with LLM_PROVIDER (and optionally LLM_MODEL):

  offline    no model at all. Returns "" so callers fall back to cached
             extractions (examples/athena) or to an extractive answer that
             simply lists the retrieved facts. Lets every lab run for free.
  ollama     a local model through Ollama (free; `ollama pull llama3.1`).
  anthropic  Claude through the Anthropic API (pip install anthropic;
             set ANTHROPIC_API_KEY or run `ant auth login`).
  bedrock    Claude on Amazon Bedrock (Chapter 13; pip install anthropic,
             AWS credentials, and AWS_REGION).
"""
from __future__ import annotations

import json
import urllib.request

from . import config

DEFAULT_MODELS = {
    "ollama": "llama3.1",
    "anthropic": "claude-opus-5-5",
    "bedrock": "anthropic.claude-opus-5-5",
}


class LLMRefused(RuntimeError):
    """The model declined the request (stop_reason == "refusal")."""


def model_name() -> str:
    return config.LLM_MODEL or DEFAULT_MODELS.get(config.LLM_PROVIDER, "")


def call_llm(prompt: str, max_tokens: int = 4000) -> str:
    provider = config.LLM_PROVIDER
    if provider == "offline":
        return ""
    if provider == "ollama":
        return _ollama(prompt)
    if provider in ("anthropic", "bedrock"):
        return _claude(prompt, max_tokens, bedrock=provider == "bedrock")
    raise ValueError(f"Unknown LLM_PROVIDER {provider!r} "
                     "(use offline, ollama, anthropic, or bedrock)")


def _ollama(prompt: str) -> str:
    body = json.dumps({"model": model_name(), "prompt": prompt,
                       "stream": False}).encode()
    req = urllib.request.Request(f"{config.OLLAMA_URL}/api/generate",
                                 data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())["response"]


def _claude(prompt: str, max_tokens: int, bedrock: bool) -> str:
    import anthropic

    messages = [{"role": "user", "content": prompt}]
    if bedrock:
        client = anthropic.AnthropicBedrockMantle(aws_region=config.AWS_REGION)
        response = client.messages.create(model=model_name(),
                                          max_tokens=max_tokens,
                                          messages=messages)
    else:
        client = anthropic.Anthropic()
        # If the model declines, the API retries on a fallback model in the
        # same call ("default" picks the fallback by refusal category).
        response = client.beta.messages.create(
            model=model_name(), max_tokens=max_tokens, messages=messages,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    if response.stop_reason == "refusal":
        raise LLMRefused("The model declined this request.")
    return "".join(b.text for b in response.content if b.type == "text")


def parse_json(raw: str):
    """Parse a model's JSON reply defensively (Chapter 11): tolerate a
    ```json fence or prose around the array; return None if unparseable."""
    if not raw:
        return None
    text = raw.strip()
    if "```" in text:
        text = text.split("```")[1].removeprefix("json").strip()
    start, end = text.find("["), text.rfind("]")
    if start != -1 and end > start:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
