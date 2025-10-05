"""Data models for the Kirkham Grammar Parser.

This module contains all the data structures used throughout the parser,
including configuration, tokens, phrases, and parse results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .types import (
    Case, Gender, Number, PartOfSpeech, Person, RuleID, SentenceType, Tense,
    Voice,
)


@dataclass
class ParserConfig:
    """Configuration options for the parser.

    Allows customization of parsing behavior and rule enforcement
    for different use cases (e.g., formal vs. informal English,
    strict vs. permissive grammar checking).

    Attributes:
        enforce_rule_20_strict: Strictly enforce transitive verb object requirement
        enforce_rule_12_strict: Strictly enforce possessive governance
        detect_get_passive: Enable get-passive voice detection
        detect_been_passive: Enable perfect passive (been + VBN) detection
        allow_informal_pronouns: Allow informal pronoun case (e.g., "It's me")
        check_subject_verb_agreement: Enable subject-verb agreement checking
        check_infinitive_detection: Enable infinitive phrase detection
        max_parse_depth: Maximum recursion depth for complex sentences

    """

    # Rule enforcement
    enforce_rule_1_strict: bool = True  # Article-noun agreement (a/an + singular)
    enforce_rule_2_strict: bool = True  # Article-noun relationship (the + noun)
    enforce_rule_3_strict: bool = True  # Subject required for verb
    enforce_rule_4_strict: bool = True  # Subject-verb agreement
    enforce_rule_8_strict: bool = True  # Compound subject agreement
    enforce_rule_12_strict: bool = True  # Possessive governance
    enforce_rule_13_strict: bool = True  # Personal pronoun agreement
    enforce_rule_18_strict: bool = True  # Adjective qualification
    enforce_rule_19_strict: bool = True  # Adjective pronoun validation
    enforce_rule_20_strict: bool = True  # Transitive verbs require objects
    enforce_rule_21_strict: bool = True  # Copula case agreement
    enforce_rule_25_strict: bool = True  # Bare infinitive detection
    enforce_rule_28_strict: bool = True  # Perfect participle agreement
    enforce_rule_29_strict: bool = True  # Adverb qualification
    enforce_rule_30_strict: bool = True  # Preposition placement
    enforce_rule_31_strict: bool = True  # Preposition object case

    # Orthography (Spelling) Rules
    enforce_ortho_rules: bool = True  # Enable orthography checking
    enforce_ortho_i: bool = True  # Monosyllables ending in f, l, or s
    enforce_ortho_ii: bool = True  # Polysyllables ending in f, l, or s
    enforce_ortho_iii: bool = True  # Words ending in y after consonant
    enforce_ortho_iv: bool = True  # Words ending in y after vowel
    enforce_ortho_v: bool = True  # Suffixes -able, -ous
    enforce_ortho_vi: bool = True  # Final silent e
    enforce_ortho_vii: bool = True  # Additional derivative cases
    enforce_ortho_viii: bool = True  # Additional derivative cases
    enforce_ortho_ix: bool = True  # Additional derivative cases
    enforce_ortho_x: bool = True  # Adding -ing or -ish

    # Punctuation Rules
    enforce_punctuation_rules: bool = True  # Enable punctuation checking
    enforce_comma_rules: bool = True  # Enable comma rules
    enforce_semicolon_rules: bool = True  # Enable semicolon rules
    enforce_colon_rules: bool = True  # Enable colon rules
    enforce_period_rules: bool = True  # Enable period rules
    enforce_dash_rules: bool = True  # Enable dash rules
    enforce_interrogation_rules: bool = True  # Enable interrogation rules
    enforce_exclamation_rules: bool = True  # Enable exclamation rules
    enforce_apostrophe_rules: bool = True  # Enable apostrophe rules
    enforce_quotation_rules: bool = True  # Enable quotation rules

    # Feature toggles
    detect_get_passive: bool = True  # Get-passive constructions
    detect_been_passive: bool = True  # Perfect passive (been + VBN)
    detect_infinitives: bool = True  # Infinitive phrase detection
    detect_sentence_type: bool = True  # Detect sentence types
    detect_tense: bool = True  # Detect verb tense

    # Permissiveness
    allow_informal_pronouns: bool = False  # "It's me" vs "It is I"
    allow_sentence_fragments: bool = False  # Allow sentences without verbs

    # Performance
    max_parse_depth: int = 100  # Prevent infinite recursion
    enable_extended_validation: bool = True  # Run all rule checks

    @classmethod
    def strict_formal(cls) -> ParserConfig:
        """Strict formal English configuration (academic, legal writing).

        Example:
            >>> parser = Parser(ParserConfig.strict_formal())
            >>> result = parser.parse("It is I.")  # Accepts formal pronouns

        """
        return cls(
            enforce_rule_20_strict=True,
            enforce_rule_12_strict=True,
            enforce_rule_4_strict=True,
            enforce_rule_3_strict=True,
            allow_informal_pronouns=False,
            allow_sentence_fragments=False,
            enable_extended_validation=True,
        )

    @classmethod
    def modern_permissive(cls) -> ParserConfig:
        """Modern permissive English configuration (casual writing, conversation).

        Example:
            >>> parser = Parser(ParserConfig.modern_permissive())
            >>> result = parser.parse("It's me.")  # Accepts informal pronouns

        """
        return cls(
            enforce_rule_20_strict=False,
            enforce_rule_12_strict=False,
            enforce_rule_4_strict=True,  # Still check agreement
            enforce_rule_3_strict=False,  # Allow fragments
            allow_informal_pronouns=True,
            allow_sentence_fragments=True,
            enable_extended_validation=False,
        )

    @classmethod
    def educational(cls) -> ParserConfig:
        """Educational configuration (teaching/learning, all checks enabled).

        Example:
            >>> parser = Parser(ParserConfig.educational())
            >>> result = parser.parse("The cat sat.")  # Full analysis

        """
        return cls(
            enforce_rule_20_strict=True,
            enforce_rule_12_strict=True,
            enforce_rule_4_strict=True,
            enforce_rule_3_strict=True,
            allow_informal_pronouns=False,
            allow_sentence_fragments=False,
            enable_extended_validation=True,
            detect_sentence_type=True,
            detect_tense=True,
        )


# Default configuration (strict, formal English)
DEFAULT_CONFIG = ParserConfig()


@dataclass
class Span:
    """Represents a character span in the original text.

    Used for precise error location and highlighting.
    Uses __slots__ for memory efficiency when processing large corpora.

    Attributes:
        start: Starting character position (inclusive)
        end: Ending character position (exclusive)

    """

    start: int
    end: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {"start": self.start, "end": self.end}


@dataclass
class Flag:
    """Represents a grammar rule violation or warning.

    Provides type-safe, structured error reporting with precise
    location information for highlighting in UIs.

    Attributes:
        rule: The rule identifier that was violated
        message: Human-readable description of the issue
        span: Optional character span where the issue occurs

    """

    rule: RuleID
    message: str
    span: Span | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"rule": self.rule.value, "message": self.message}
        if self.span:
            result["span"] = self.span.to_dict()
        return result


@dataclass
class Token:
    """Represents a single token (word or punctuation) in a sentence.

    Attributes:
        text: The original text of the token
        lemma: The base form of the word
        pos: Part of speech
        start: Character offset where token starts in original text
        end: Character offset where token ends in original text
        case: Grammatical case (for nouns and pronouns)
        gender: Grammatical gender
        number: Grammatical number
        person: Grammatical person
        features: Additional linguistic features

    """

    text: str
    lemma: str
    pos: PartOfSpeech
    start: int = 0
    end: int = 0
    case: Case | None = None
    gender: Gender | None = None
    number: Number | None = None
    person: Person | None = None
    features: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return string representation of token."""
        parts = [f"{self.text} [{self.pos.value}]"]
        if self.case:
            parts.append(f"case={self.case.value}")
        if self.number:
            parts.append(f"number={self.number.value}")
        if self.person:
            parts.append(f"person={self.person.value}")
        return " ".join(parts)

    def to_dict(self) -> dict:
        """Convert token to dictionary for JSON serialization."""
        result = {
            "text": self.text,
            "lemma": self.lemma,
            "pos": self.pos.value,
            "start": self.start,
            "end": self.end,
        }
        if self.case:
            result["case"] = self.case.value
        if self.gender:
            result["gender"] = self.gender.value
        if self.number:
            result["number"] = self.number.value
        if self.person:
            result["person"] = self.person.value
        if self.features:
            result["features"] = self.features
        return result


@dataclass
class Phrase:
    """Represents a phrase (group of related tokens).

    Attributes:
        tokens: List of tokens in the phrase
        phrase_type: Type of phrase (NP, VP, PP, etc.)
        head_index: Index of the head word in tokens list

    """

    tokens: list[Token]
    phrase_type: str
    head_index: int

    @property
    def head_token(self) -> Token:
        """Return the head token of the phrase."""
        return self.tokens[self.head_index]

    @property
    def text(self) -> str:
        """Return the text of the phrase."""
        return " ".join(t.text for t in self.tokens)


@dataclass
class ParseResult:
    """Complete parse result for a sentence.

    Attributes:
        tokens: All tokens in the sentence
        subject: Subject noun phrase
        verb_phrase: Main verb phrase
        object_phrase: Object phrase (if exists)
        voice: Voice of the main verb
        tense: Tense of the main verb
        sentence_type: Type of sentence (declarative, interrogative, etc.)
        rule_checks: Results of grammar rule validation (RuleID -> pass/fail)
        flags: List of rule violations and warnings with precise locations
        errors: Deprecated - use flags instead (kept for backwards compatibility)
        warnings: Deprecated - use flags instead (kept for backwards compatibility)
        notes: Additional parsing notes

    """

    tokens: list[Token]
    subject: Phrase | None = None
    verb_phrase: Phrase | None = None
    object_phrase: Phrase | None = None
    voice: Voice | None = None
    tense: Tense | None = None
    sentence_type: SentenceType | None = None
    rule_checks: dict[str, bool] = field(default_factory=dict)
    flags: list[Flag] = field(default_factory=list)
    # Backwards compatibility: keep these for existing code
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert parse result to dictionary for JSON serialization.
        Useful for APIs and UI applications that need to highlight tokens.
        """

        def phrase_to_dict(phrase: Phrase | None) -> dict | None:
            if not phrase:
                return None
            return {
                "text": phrase.text,
                "tokens": [t.to_dict() for t in phrase.tokens],
                "head_index": phrase.head_index,
                "start": phrase.tokens[0].start if phrase.tokens else 0,
                "end": phrase.tokens[-1].end if phrase.tokens else 0,
            }

        return {
            "tokens": [t.to_dict() for t in self.tokens],
            "subject": phrase_to_dict(self.subject),
            "verb_phrase": phrase_to_dict(self.verb_phrase),
            "object_phrase": phrase_to_dict(self.object_phrase),
            "voice": self.voice.value if self.voice else None,
            "tense": self.tense.value if self.tense else None,
            "sentence_type": self.sentence_type.value if self.sentence_type else None,
            "rule_checks": self.rule_checks,
            "flags": [flag.to_dict() for flag in self.flags],
            # Backwards compatibility
            "errors": self.errors,
            "warnings": self.warnings,
            "notes": self.notes,
        }
