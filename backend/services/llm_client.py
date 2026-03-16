"""
LLM provider abstraction layer.

All 5 analysis passes call `complete(system, user, max_tokens)` — this module
handles routing to the configured provider.

Configuration (via environment variables):
  LLM_PROVIDER   = anthropic (default) | openai

  For Anthropic:
    ANTHROPIC_API_KEY  your Anthropic key
    LLM_MODEL          model name (default: claude-sonnet-4-6)

  For OpenAI or any OpenAI-compatible API
  (Groq, Together.ai, Ollama, Azure OpenAI, LM Studio, etc.):
    OPENAI_API_KEY     your key
    OPENAI_BASE_URL    custom base URL (optional; omit for official OpenAI)
    LLM_MODEL          model name (default: gpt-4o)

  Legacy variable still honoured for backwards compatibility:
    CLAUDE_MODEL       treated as LLM_MODEL when LLM_MODEL is not set
"""

import concurrent.futures
import os

from services.errors import LLMTimeoutError

_client = None
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)


def _get_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic").lower()


def _get_model(provider: str) -> str:
    """Resolve the model name from env, with sensible per-provider defaults."""
    if model := os.environ.get("LLM_MODEL"):
        return model
    if model := os.environ.get("CLAUDE_MODEL"):  # backwards compat
        return model
    return "claude-sonnet-4-6" if provider == "anthropic" else "gpt-4o"


def get_timeout_seconds() -> float:
    raw_timeout = os.environ.get("LLM_TIMEOUT_SECONDS", "180")
    try:
        timeout = float(raw_timeout)
    except ValueError:
        timeout = 60.0
    return max(timeout, 1.0)


def _get_client(provider: str):
    global _client
    if _client is not None:
        return _client

    if provider == "anthropic":
        import anthropic  # type: ignore

        _client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            timeout=get_timeout_seconds(),
        )

    elif provider == "openai":
        try:
            import openai  # type: ignore
        except ImportError:
            raise RuntimeError(
                "The 'openai' package is required when LLM_PROVIDER=openai. "
                "Install it with: pip install openai"
            )
        kwargs: dict = {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "timeout": get_timeout_seconds(),
        }
        if base_url := os.environ.get("OPENAI_BASE_URL"):
            kwargs["base_url"] = base_url
        _client = openai.OpenAI(**kwargs)

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider!r}. Valid values: anthropic, openai"
        )

    return _client


def _is_sdk_timeout(exc: Exception) -> bool:
    """Return True if exc is a provider SDK timeout without importing SDK types."""
    # anthropic.APITimeoutError, openai.APITimeoutError, httpx.TimeoutException
    # all contain "Timeout" or "timeout" in their class name.
    return "timeout" in type(exc).__name__.lower()


def complete(system: str, user: str, max_tokens: int = 2048) -> str:
    """
    Call the configured LLM and return the response text.

    This is the single entry point used by all 5 analysis passes.
    Provider and model are resolved from environment variables.
    """
    provider = _get_provider()
    model = _get_model(provider)
    llm = _get_client(provider)

    future = _executor.submit(
        _complete_request, provider, model, llm, system, user, max_tokens
    )

    try:
        return future.result(timeout=get_timeout_seconds())
    except concurrent.futures.TimeoutError as exc:
        future.cancel()
        raise LLMTimeoutError(
            f"Analysis exceeded the {get_timeout_seconds():.0f}s model timeout. Please retry."
        ) from exc
    except Exception as exc:
        # SDK-level timeouts (e.g. anthropic.APITimeoutError, openai.APITimeoutError,
        # httpx.TimeoutException) raise before the futures timeout fires when the
        # configured timeout value is the same for both. Convert them to LLMTimeoutError
        # so callers get a 502 with a user-safe message instead of a 500.
        if _is_sdk_timeout(exc):
            raise LLMTimeoutError(
                f"Analysis exceeded the {get_timeout_seconds():.0f}s model timeout. Please retry."
            ) from exc
        raise


def _complete_request(
    provider: str, model: str, llm, system: str, user: str, max_tokens: int
) -> str:
    if provider == "anthropic":
        message = llm.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return message.content[0].text

    if provider == "openai":
        response = llm.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content

    raise ValueError(f"Unknown provider: {provider}")


def reset() -> None:
    """Reset the cached client. Used in tests to force re-initialisation."""
    global _client
    _client = None
