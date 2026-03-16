class AnalysisError(Exception):
    """Base class for user-safe analysis failures."""


class LLMOutputError(AnalysisError):
    """Raised when an LLM pass returns invalid structured output."""


class LLMTimeoutError(AnalysisError):
    """Raised when an LLM request exceeds the configured timeout."""
