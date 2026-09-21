"""Standalone file vectorizer; importing workers never imports Torch."""

__version__ = "0.1.0"

def __getattr__(name):
    if name == "Vectorizer":
        from .api import Vectorizer
        return Vectorizer
    raise AttributeError(name)
