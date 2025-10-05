"""Kirkham English Grammar Parser.

A comprehensive English language parser based on Samuel Kirkham's
English Grammar (1829). Provides syntactic analysis, grammar rule
validation, and linguistic feature detection.

Main Classes:
    KirkhamParser: Main parser class for analyzing English sentences
    ParserConfig: Configuration options for parsing behavior
    ParseResult: Complete analysis result with tokens, phrases, and flags
    Lexicon: Pluggable word lists for classification

Example:
    >>> from kirkham import KirkhamParser
    >>> parser = KirkhamParser()
    >>> result = parser.parse("The cat sat on the mat.")
    >>> print(result.subject.text)
    The cat

"""

from .parser import (
    DEFAULT_CONFIG,
    DEFAULT_LEXICON,
    Case,
    Flag,
    Gender,
    KirkhamParser,
    Lexicon,
    Number,
    ParserConfig,
    ParseResult,
    PartOfSpeech,
    Person,
    Phrase,
    RuleID,
    SentenceType,
    Span,
    Tense,
    Token,
    Voice,
)

__version__ = "1.0.0"
__author__ = "Kirkham Grammar Parser"
__email__ = "parser@kirkham.dev"

__all__ = [
    # Main classes
    "KirkhamParser",
    "ParserConfig",
    "ParseResult",
    "Token",
    "Phrase",
    "Flag",
    "Span",
    "Lexicon",
    # Enums
    "PartOfSpeech",
    "Case",
    "Gender",
    "Number",
    "Person",
    "Voice",
    "Tense",
    "SentenceType",
    "RuleID",
    # Defaults
    "DEFAULT_CONFIG",
    "DEFAULT_LEXICON",
]
