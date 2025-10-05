"""Utility functions for text processing in the Kirkham Grammar Parser.

This module contains text processing utilities including tokenization,
morphology analysis, and word classification helpers.
"""

from __future__ import annotations

import re


class TextUtils:
    """Utility functions for text processing."""

    # Pre-compiled regex patterns for performance
    # Handles: contractions, possessives, hyphenated words, Unicode apostrophes,
    # curly quotes, em/en-dashes, numbers
    TOKEN_PATTERN = re.compile(
        r"""
        # Hyphenated words and internal apostrophes (supports ASCII and Unicode ')
        [A-Za-z]+(?:['\u2019][A-Za-z]+)*(?:-[A-Za-z]+)*
        |
        # Numbers (integers and decimals)
        \d+(?:\.\d+)?
        |
        # Punctuation incl. straight & curly quotes and dashes
        [.,;:!?()\[\]{}"'\u2018\u2019\u201C\u201D\u2014\u2013-]
        """,
        re.VERBOSE | re.UNICODE,
    )

    # Pre-compiled pattern for adjective suffix matching (micro-optimization)
    ADJECTIVE_SUFFIX_PATTERN = re.compile(
        r"(ous|ive|ful|less|al|able|ible|ic|ish|ent|ant)$", re.IGNORECASE
    )

    # Cached set of irregular past participles (avoid repeated set creation)
    IRREGULAR_PARTICIPLES = frozenset(
        {
            "been",
            "seen",
            "known",
            "given",
            "taken",
            "written",
            "spoken",
            "broken",
            "chosen",
            "frozen",
            "stolen",
            "beaten",
            "eaten",
            "fallen",
            "forgotten",
            "hidden",
            "driven",
            "risen",
            "sworn",
            "torn",
            "worn",
            "born",
            "borne",
            "drawn",
            "grown",
            "shown",
            "thrown",
            "flown",
            "blown",
            "sown",
            "mown",
            "gone",
            "done",
            "made",
            "said",
            "heard",
            "told",
            "found",
            "felt",
            "kept",
            "slept",
            "left",
            "meant",
            "built",
            "sent",
            "spent",
            "lost",
            "won",
            "met",
            "sat",
            "stood",
            "caught",
            "taught",
            "brought",
            "fought",
            "thought",
            "bought",
            "sought",
            "sold",
            "held",
            "read",
        }
    )

    # Cached set of irregular plural nouns
    IRREGULAR_PLURALS = frozenset(
        {
            "men",
            "women",
            "children",
            "people",
            "teeth",
            "feet",
            "mice",
            "geese",
            "oxen",
            "sheep",
            "deer",
            "fish",
            "species",
            "series",
            "aircraft",
            "offspring",
            # Latin/Greek plurals
            "data",
            "criteria",
            "phenomena",
            "bacteria",
            "alumni",
            "fungi",
            "nuclei",
            "syllabi",
            "stimuli",
            "analyses",
            "bases",
            "crises",
            "diagnoses",
            "hypotheses",
            "oases",
            "parentheses",
            "syntheses",
            "theses",
            "appendices",
            "indices",
            "matrices",
            "vertices",
        }
    )

    @staticmethod
    def tokenize(text: str) -> list[tuple[str, int, int]]:
        """Tokenize text into words and punctuation with character offsets.

        Args:
            text: Input text string

        Returns:
            List of tuples (token_text, start_offset, end_offset)

        Example:
            >>> TextUtils.tokenize("It's a "nice" day—really!")
            [("It's", 0, 4), ('a', 5, 6), ('"', 7, 8), ...]

        """
        return [
            (m.group(0), m.start(), m.end())
            for m in TextUtils.TOKEN_PATTERN.finditer(text)
        ]

    @staticmethod
    def is_capitalized(word: str) -> bool:
        """Check if word is properly capitalized (first letter upper, rest lower)."""
        if not word:
            return False
        return word[0].isupper() and word[1:].islower()

    @staticmethod
    def strip_possessive(word: str) -> tuple[str, bool]:
        """Strip possessive marker from word.

        Returns:
            Tuple of (base_word, is_possessive)

        """
        if word.endswith("'s"):
            return word[:-2], True
        if word.endswith("'"):
            return word[:-1], True
        return word, False

    @staticmethod
    def is_plural_noun(word: str) -> bool:
        """Improved heuristic check if word is a plural noun.

        Handles:
        - Irregular plurals (men, women, children, data, etc.)
        - Genitives (strips possessive markers)
        - Latin/Greek plurals (criteria, phenomena, etc.)
        - Common exceptions (ss, us endings)

        Note: Still heuristic-based, not 100% accurate for all cases.
        """
        # Check for possessive FIRST (should not be considered plural)
        if word.endswith(("'s", "s'")):
            return False

        # Strip possessive markers and normalize
        w = word.lower().strip("'")
        if w.endswith("'s"):
            w = w[:-2]
        elif w.endswith("s'"):
            w = w[:-1]

        # Check irregular plurals (including Latin/Greek)
        if w in TextUtils.IRREGULAR_PLURALS:
            return True

        # Singular exceptions that end in 's' or similar
        if w.endswith(("ss", "us", "is")):
            return False

        # General plural rule: ends with 's' but not genitives
        return w.endswith("s")

    @staticmethod
    def is_past_participle(word: str) -> bool:
        """Check if word appears to be a past participle."""
        w = word.lower()
        # Use pre-cached irregular participles (micro-optimization)
        if w in TextUtils.IRREGULAR_PARTICIPLES:
            return True
        # Regular participles ending in -ed
        return w.endswith("ed")

    @staticmethod
    def is_present_participle(word: str) -> bool:
        """Check if word appears to be a present participle."""
        return word.lower().endswith("ing")
