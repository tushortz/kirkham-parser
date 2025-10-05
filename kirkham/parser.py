"""English Grammar Classifier and Parser
Based on Samuel Kirkham's English Grammar (1829).

This module implements a comprehensive English language parser that classifies
parts of speech and validates sentences according to traditional grammar rules.

Author: Generated based on Kirkham's Grammar
Date: 2025
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================


class PartOfSpeech(Enum):
    """Parts of speech enumeration."""

    NOUN = "noun"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    VERB = "verb"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    ARTICLE = "article"
    PARTICIPLE = "participle"
    PUNCTUATION = "punctuation"


class Case(Enum):
    """Grammatical case enumeration."""

    NOMINATIVE = "nominative"
    POSSESSIVE = "possessive"
    OBJECTIVE = "objective"


class Gender(Enum):
    """Grammatical gender enumeration."""

    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"


class Number(Enum):
    """Grammatical number enumeration."""

    SINGULAR = "singular"
    PLURAL = "plural"


class Person(Enum):
    """Grammatical person enumeration."""

    FIRST = "first"
    SECOND = "second"
    THIRD = "third"


class Voice(Enum):
    """Verb voice enumeration."""

    ACTIVE = "active"
    PASSIVE = "passive"
    NEUTER = "neuter"


class Tense(Enum):
    """Verb tense enumeration."""

    PRESENT = "present"
    PAST = "past"
    FUTURE = "future"
    PRESENT_PERFECT = "present_perfect"
    PAST_PERFECT = "past_perfect"
    FUTURE_PERFECT = "future_perfect"


class SentenceType(Enum):
    """Sentence type enumeration."""

    DECLARATIVE = "declarative"  # Statement: "The cat sat."
    INTERROGATIVE = "interrogative"  # Question: "Did the cat sit?"
    IMPERATIVE = "imperative"  # Command: "Sit down!"
    EXCLAMATORY = "exclamatory"  # Exclamation: "What a cat!"


class RuleID(str, Enum):
    """Kirkham's Grammar Rules enumeration.

    Provides type-safe identifiers for grammar rules.
    Inherits from str for JSON serialization compatibility.
    """

    # Subject-Verb Agreement Rules
    RULE_3 = "RULE_3"  # Nominative case governs verb
    RULE_4 = "RULE_4"  # Verb agrees with subject in number and person
    RULE_12 = "RULE_12"  # Possessive governance

    # Object and Transitive Verb Rules
    RULE_20 = "RULE_20"  # Active-transitive verbs govern objective case
    RULE_21 = "RULE_21"  # Transitive verbs must have objects

    # Passive Voice Rules
    RULE_22 = "RULE_22"  # Passive voice construction
    RULE_23 = "RULE_23"  # Passive voice agreement

    # Additional Rules (can be extended)
    RULE_5 = "RULE_5"  # Article usage
    RULE_6 = "RULE_6"  # Adjective placement
    RULE_10 = "RULE_10"  # Preposition governance
    RULE_18 = "RULE_18"  # Adjectives qualify nouns
    RULE_31 = "RULE_31"  # Prepositions govern the objective case


# ============================================================================
# LEXICON - Word Lists
# ============================================================================


@dataclass
class Lexicon:
    """Pluggable lexicon containing word lists for classification.

    Follows the vocabulary organization from Kirkham's Grammar.
    Users can extend or customize lexicons by creating a new instance:

    Example:
        custom_lex = Lexicon(
            transitive_verbs=Lexicon.DEFAULT_TRANSITIVE_VERBS | {"customize"},
        )
        parser = Parser(lexicon=custom_lex)

    Note: Using frozenset for immutable word lists provides micro-optimization
    for membership testing (O(1) lookup with slightly better cache performance).

    """

    # Default lexicon values (class-level constants for reference)
    DEFAULT_ARTICLES: frozenset[str] = frozenset({"the", "a", "an"})

    PERSONAL_PRONOUNS: set[str] = frozenset(
        {
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "thou",
            "thee",
            "ye",
        }
    )

    POSSESSIVE_PRONOUNS: set[str] = frozenset(
        {
            "my",
            "thy",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "thine",
            "yours",
            "hers",
            "ours",
            "theirs",
        }
    )

    DEMONSTRATIVE_PRONOUNS: set[str] = frozenset({"this", "that", "these", "those"})

    RELATIVE_PRONOUNS: set[str] = frozenset(
        {"who", "whom", "whose", "which", "that", "what"}
    )

    INTERROGATIVE_PRONOUNS: set[str] = frozenset(
        {"who", "whom", "whose", "which", "what"}
    )

    COORDINATING_CONJUNCTIONS: set[str] = frozenset(
        {"and", "or", "but", "nor", "for", "yet", "so"}
    )

    SUBORDINATING_CONJUNCTIONS: set[str] = frozenset(
        {
            "after",
            "although",
            "as",
            "because",
            "before",
            "if",
            "since",
            "than",
            "that",
            "though",
            "unless",
            "until",
            "when",
            "where",
            "whether",
            "while",
        }
    )

    PREPOSITIONS: set[str] = frozenset(
        {
            "of",
            "to",
            "in",
            "for",
            "on",
            "with",
            "at",
            "from",
            "by",
            "about",
            "as",
            "into",
            "like",
            "through",
            "after",
            "over",
            "between",
            "out",
            "against",
            "during",
            "without",
            "before",
            "under",
            "around",
            "among",
            "beneath",
            "beside",
            "beyond",
            "near",
            "above",
            "below",
            "across",
            "behind",
            "within",
        }
    )

    AUXILIARY_BE: set[str] = frozenset(
        {"am", "is", "are", "was", "were", "be", "been", "being"}
    )

    AUXILIARY_HAVE: set[str] = frozenset({"have", "has", "had", "having"})

    AUXILIARY_DO: set[str] = frozenset({"do", "does", "did"})

    # Get-passive auxiliary (for get-passive constructions like "got caught")
    AUXILIARY_GET: set[str] = frozenset({"get", "gets", "got", "getting", "gotten"})

    MODAL_VERBS: set[str] = frozenset(
        {
            "may",
            "might",
            "can",
            "could",
            "shall",
            "should",
            "will",
            "would",
            "must",
            "ought",
        }
    )

    COMMON_TRANSITIVE_VERBS: set[str] = frozenset(
        {
            "see",
            "sees",
            "saw",
            "seen",
            "know",
            "knows",
            "knew",
            "known",
            "make",
            "makes",
            "made",
            "take",
            "takes",
            "took",
            "taken",
            "give",
            "gives",
            "gave",
            "given",
            "find",
            "finds",
            "found",
            "tell",
            "tells",
            "told",
            "call",
            "calls",
            "called",
            "ask",
            "asks",
            "asked",
            "use",
            "uses",
            "used",
            "write",
            "writes",
            "wrote",
            "written",
            "love",
            "loves",
            "loved",
            "help",
            "helps",
            "helped",
            "build",
            "builds",
            "built",
            "read",
            "reads",
            "buy",
            "buys",
            "bought",
            "sell",
            "sells",
            "sold",
            "show",
            "shows",
            "showed",
            "shown",
            "bring",
            "brings",
            "brought",
            "send",
            "sends",
            "sent",
        }
    )

    COMMON_INTRANSITIVE_VERBS: set[str] = frozenset(
        {
            "go",
            "goes",
            "went",
            "gone",
            "come",
            "comes",
            "came",
            "run",
            "runs",
            "ran",
            "walk",
            "walks",
            "walked",
            "sit",
            "sits",
            "sat",
            "stand",
            "stands",
            "stood",
            "sleep",
            "sleeps",
            "slept",
            "die",
            "dies",
            "died",
            "arrive",
            "arrives",
            "arrived",
            "sing",
            "sings",
            "sang",
            "sung",
            "jump",
            "jumps",
            "jumped",
        }
    )

    COMMON_NOUNS: set[str] = frozenset(
        {
            "cat",
            "dog",
            "bird",
            "fox",
            "lion",
            "tiger",
            "man",
            "woman",
            "child",
            "person",
            "people",
            "house",
            "home",
            "building",
            "room",
            "door",
            "book",
            "paper",
            "pen",
            "pencil",
            "day",
            "night",
            "morning",
            "evening",
            "time",
            "year",
            "month",
            "week",
            "name",
            "place",
            "thing",
            "world",
            "hand",
            "eye",
            "face",
            "head",
            "city",
            "town",
            "country",
            "state",
            "school",
            "university",
            "college",
            "engineer",
            "teacher",
            "doctor",
            "student",
            "software",
            "hardware",
            "computer",
        }
    )

    COMMON_ADJECTIVES: set[str] = frozenset(
        {
            "good",
            "bad",
            "big",
            "small",
            "large",
            "little",
            "old",
            "new",
            "young",
            "long",
            "short",
            "hot",
            "cold",
            "warm",
            "cool",
            "quick",
            "slow",
            "fast",
            "lazy",
            "beautiful",
            "ugly",
            "pretty",
            "handsome",
            "happy",
            "sad",
            "angry",
            "glad",
            "red",
            "blue",
            "green",
            "yellow",
            "black",
            "white",
            "brown",
            "interesting",
            "boring",
            "difficult",
            "easy",
            "important",
            "necessary",
            "possible",
            "impossible",
        }
    )

    INTERJECTIONS: set[str] = frozenset(
        {"oh", "ah", "alas", "hello", "hey", "wow", "ouch", "hurray"}
    )

    ADVERBS: set[str] = frozenset(
        {
            "quickly",
            "slowly",
            "very",
            "quite",
            "rather",
            "well",
            "badly",
            "always",
            "never",
            "often",
            "sometimes",
            "here",
            "there",
            "now",
            "then",
            "today",
            "yesterday",
            "tomorrow",
        }
    )

    # Instance fields (pluggable lexicons)
    articles: frozenset[str] = field(default_factory=lambda: Lexicon.DEFAULT_ARTICLES)
    personal_pronouns: frozenset[str] = field(
        default_factory=lambda: Lexicon.PERSONAL_PRONOUNS
    )
    possessive_pronouns: frozenset[str] = field(
        default_factory=lambda: Lexicon.POSSESSIVE_PRONOUNS
    )
    demonstrative_pronouns: frozenset[str] = field(
        default_factory=lambda: Lexicon.DEMONSTRATIVE_PRONOUNS
    )
    relative_pronouns: frozenset[str] = field(
        default_factory=lambda: Lexicon.RELATIVE_PRONOUNS
    )
    interrogative_pronouns: frozenset[str] = field(
        default_factory=lambda: Lexicon.INTERROGATIVE_PRONOUNS
    )
    coordinating_conjunctions: frozenset[str] = field(
        default_factory=lambda: Lexicon.COORDINATING_CONJUNCTIONS
    )
    subordinating_conjunctions: frozenset[str] = field(
        default_factory=lambda: Lexicon.SUBORDINATING_CONJUNCTIONS
    )
    prepositions: frozenset[str] = field(default_factory=lambda: Lexicon.PREPOSITIONS)
    auxiliary_be: frozenset[str] = field(default_factory=lambda: Lexicon.AUXILIARY_BE)
    auxiliary_have: frozenset[str] = field(
        default_factory=lambda: Lexicon.AUXILIARY_HAVE
    )
    auxiliary_do: frozenset[str] = field(default_factory=lambda: Lexicon.AUXILIARY_DO)
    auxiliary_get: frozenset[str] = field(default_factory=lambda: Lexicon.AUXILIARY_GET)
    modal_verbs: frozenset[str] = field(default_factory=lambda: Lexicon.MODAL_VERBS)
    transitive_verbs: frozenset[str] = field(
        default_factory=lambda: Lexicon.COMMON_TRANSITIVE_VERBS
    )
    intransitive_verbs: frozenset[str] = field(
        default_factory=lambda: Lexicon.COMMON_INTRANSITIVE_VERBS
    )
    common_nouns: frozenset[str] = field(default_factory=lambda: Lexicon.COMMON_NOUNS)
    common_adjectives: frozenset[str] = field(
        default_factory=lambda: Lexicon.COMMON_ADJECTIVES
    )
    interjections: frozenset[str] = field(default_factory=lambda: Lexicon.INTERJECTIONS)
    adverbs: frozenset[str] = field(default_factory=lambda: Lexicon.ADVERBS)


# Default lexicon instance for backward compatibility
DEFAULT_LEXICON = Lexicon()


# ============================================================================
# DATA STRUCTURES
# ============================================================================


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
    enforce_rule_20_strict: bool = True  # Transitive verbs require objects
    enforce_rule_12_strict: bool = True  # Possessive governance
    enforce_rule_4_strict: bool = True  # Subject-verb agreement
    enforce_rule_3_strict: bool = True  # Subject required for verb

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


# ============================================================================
# UTILITIES
# ============================================================================


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
        r"(ous|ive|ful|less|al|ary|able|ible|ic|ish|ent|ant)$", re.IGNORECASE
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


# ============================================================================
# CLASSIFIER - Determines Part of Speech
# ============================================================================


class PartOfSpeechClassifier:
    """Classifies words into their parts of speech.
    Implements a rule-based classification system based on Kirkham's Grammar.
    """

    # Pre-compiled regex patterns for performance (class-level constants)
    PUNCTUATION_PATTERN = re.compile(r"[.,;:!?()]$")
    VERB_ENDING_PATTERN = re.compile(r"(s|ed|ing)$", re.IGNORECASE)
    NUMBER_PATTERN = re.compile(r"^\d+(\.\d+)?$")

    def __init__(self, lexicon: Lexicon | None = None) -> None:
        """Initialize the classifier with lexicon."""
        self.lex = lexicon or DEFAULT_LEXICON
        self.utils = TextUtils()

    def classify(
        self,
        word: str,
        start: int = 0,
        end: int = 0,
        context: list[str] | None = None,
    ) -> Token:
        """Classify a word into its part of speech.

        Args:
            word: The word to classify
            start: Character offset where word starts in original text
            end: Character offset where word ends in original text
            context: Optional context (surrounding words)

        Returns:
            Token object with classification

        """
        lemma = word.lower()
        base, is_possessive = self.utils.strip_possessive(lemma)

        # Check punctuation first (use pre-compiled pattern for performance)
        if len(word) == 1 and self.PUNCTUATION_PATTERN.fullmatch(word):
            return Token(
                text=word,
                lemma=word,
                pos=PartOfSpeech.PUNCTUATION,
                start=start,
                end=end,
            )

        # Check articles
        if lemma in self.lex.articles:
            return self._create_article_token(word, lemma, start, end)

        # Check pronouns
        if lemma in self.lex.personal_pronouns:
            return self._create_pronoun_token(word, lemma, start, end)

        if lemma in self.lex.possessive_pronouns or is_possessive:
            return self._create_possessive_token(
                word, lemma, base, is_possessive, start, end
            )

        if lemma in self.lex.demonstrative_pronouns:
            return self._create_demonstrative_token(word, lemma, start, end)

        if lemma in self.lex.relative_pronouns:
            return self._create_relative_pronoun_token(word, lemma, start, end)

        # Check conjunctions
        if (
            lemma in self.lex.coordinating_conjunctions
            or lemma in self.lex.subordinating_conjunctions
        ):
            return self._create_conjunction_token(word, lemma, start, end)

        # Check prepositions
        if lemma in self.lex.prepositions:
            return self._create_preposition_token(word, lemma, start, end)

        # Check interjections
        if lemma in self.lex.interjections:
            return self._create_interjection_token(word, lemma, start, end)

        # Check verbs (with higher priority for explicit verb forms)
        if self._is_verb(lemma):
            return self._create_verb_token(word, lemma, start, end)

        # Check adverbs
        if self._is_adverb(lemma):
            return self._create_adverb_token(word, lemma, start, end)

        # Check explicit adjectives list first
        if lemma in self.lex.common_adjectives:
            return self._create_adjective_token(word, lemma, start, end)

        # Check explicit nouns list
        if lemma in self.lex.common_nouns:
            return self._create_noun_token(word, lemma, is_possessive, start, end)

        # Check adjectives by suffix
        if self._is_adjective(word, lemma):
            return self._create_adjective_token(word, lemma, start, end)

        # Default to noun (proper nouns or unknown words)
        return self._create_noun_token(word, lemma, is_possessive, start, end)

    def _is_verb(self, lemma: str) -> bool:
        """Check if word is a verb."""
        # Handle common 3sg forms that might not be in lexicon
        if lemma in {"has", "does"}:
            return True

        # Explicit verb lists have highest priority
        if (
            lemma in self.lex.auxiliary_be
            or lemma in self.lex.auxiliary_have
            or lemma in self.lex.auxiliary_do
            or lemma in self.lex.auxiliary_get
            or lemma in self.lex.modal_verbs
            or lemma in self.lex.transitive_verbs
            or lemma in self.lex.intransitive_verbs
        ):
            return True

        # Don't treat as verb if it's in known noun/adjective lists
        if lemma in self.lex.common_nouns or lemma in self.lex.common_adjectives:
            return False

        # Check for verb suffixes, but be careful with -s (could be plural noun)
        # Only consider -ed and -ing as strong verb indicators
        if lemma.endswith(("ed", "ing")) and len(lemma) > 3:
            return True

        # For -s ending, only if not a common noun pattern
        if lemma.endswith("s") and not lemma.endswith(("ss", "us", "is")):
            # Remove the 's' and check if base form is a known verb
            base = lemma[:-1]
            if base in self.lex.transitive_verbs or base in self.lex.intransitive_verbs:
                return True

        return False

    def _is_adverb(self, lemma: str) -> bool:
        """Check if word is an adverb."""
        return lemma in self.lex.adverbs or lemma.endswith("ly")

    def _is_adjective(self, word: str, lemma: str) -> bool:
        """Check if word is an adjective (uses pre-compiled regex)."""
        return TextUtils.ADJECTIVE_SUFFIX_PATTERN.search(lemma) is not None

    def _create_article_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for article."""
        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.ARTICLE,
            start=start,
            end=end,
            features={"definite": lemma == "the"},
        )

    def _create_pronoun_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for personal pronoun."""
        # Determine person, number, and case
        person, number, case = self._analyze_pronoun(lemma)

        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.PRONOUN,
            start=start,
            end=end,
            person=person,
            number=number,
            case=case,
            features={"pronoun_type": "personal"},
        )

    def _create_possessive_token(
        self,
        word: str,
        lemma: str,
        base: str,
        is_possessive: bool,
        start: int,
        end: int,
    ) -> Token:
        """Create token for possessive pronoun or noun."""
        if lemma in self.lex.possessive_pronouns:
            return Token(
                text=word,
                lemma=lemma,
                pos=PartOfSpeech.PRONOUN,
                start=start,
                end=end,
                case=Case.POSSESSIVE,
                features={"pronoun_type": "possessive"},
            )
        # Possessive noun
        return Token(
            text=word,
            lemma=base,
            pos=PartOfSpeech.NOUN,
            start=start,
            end=end,
            case=Case.POSSESSIVE,
            features={"base": base},
        )

    def _create_demonstrative_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for demonstrative pronoun."""
        number = Number.PLURAL if lemma in {"these", "those"} else Number.SINGULAR
        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.PRONOUN,
            start=start,
            end=end,
            number=number,
            features={"pronoun_type": "demonstrative"},
        )

    def _create_relative_pronoun_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for relative pronoun."""
        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.PRONOUN,
            start=start,
            end=end,
            features={"pronoun_type": "relative"},
        )

    def _create_conjunction_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for conjunction."""
        conj_type = (
            "coordinating"
            if lemma in self.lex.coordinating_conjunctions
            else "subordinating"
        )
        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.CONJUNCTION,
            start=start,
            end=end,
            features={"conjunction_type": conj_type},
        )

    def _create_preposition_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for preposition."""
        return Token(
            text=word, lemma=lemma, pos=PartOfSpeech.PREPOSITION, start=start, end=end
        )

    def _create_interjection_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for interjection."""
        return Token(
            text=word, lemma=lemma, pos=PartOfSpeech.INTERJECTION, start=start, end=end
        )

    def _create_verb_token(self, word: str, lemma: str, start: int, end: int) -> Token:
        """Create token for verb."""
        features = {}

        # Check if auxiliary
        if lemma in self.lex.auxiliary_be:
            features["auxiliary"] = "be"
        elif lemma in self.lex.auxiliary_have:
            features["auxiliary"] = "have"
        elif lemma in self.lex.auxiliary_do:
            features["auxiliary"] = "do"
        elif lemma in self.lex.auxiliary_get:
            features["auxiliary"] = "get"
        elif lemma in self.lex.modal_verbs:
            features["modal"] = True

        # Check if transitive
        if lemma in self.lex.transitive_verbs:
            features["transitive"] = True
        elif lemma in self.lex.intransitive_verbs:
            features["transitive"] = False

        # Check third person singular
        if word.endswith("s") and not word.endswith(("ss", "us")):
            features["3sg"] = True
            person = Person.THIRD
            number = Number.SINGULAR
        else:
            person = None
            number = None

        # Check participles
        if self.utils.is_past_participle(lemma):
            features["participle"] = "past"
        elif self.utils.is_present_participle(lemma):
            features["participle"] = "present"

        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.VERB,
            start=start,
            end=end,
            person=person,
            number=number,
            features=features,
        )

    def _create_adverb_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for adverb."""
        return Token(
            text=word, lemma=lemma, pos=PartOfSpeech.ADVERB, start=start, end=end
        )

    def _create_adjective_token(
        self, word: str, lemma: str, start: int, end: int
    ) -> Token:
        """Create token for adjective."""
        return Token(
            text=word, lemma=lemma, pos=PartOfSpeech.ADJECTIVE, start=start, end=end
        )

    def _create_noun_token(
        self, word: str, lemma: str, is_possessive: bool, start: int, end: int
    ) -> Token:
        """Create token for noun."""
        # Determine number
        is_plural = self.utils.is_plural_noun(word)
        number = Number.PLURAL if is_plural else Number.SINGULAR

        # Determine case
        case = Case.POSSESSIVE if is_possessive else Case.NOMINATIVE

        # Check if proper noun (capitalized)
        is_proper = self.utils.is_capitalized(word)

        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.NOUN,
            start=start,
            end=end,
            case=case,
            number=number,
            person=Person.THIRD,
            features={"proper": is_proper},
        )

    def _analyze_pronoun(self, pronoun: str) -> tuple[Person, Number, Case]:
        """Analyze pronoun to determine person, number, and case.

        Returns:
            Tuple of (person, number, case)

        """
        # First person
        if pronoun == "i":
            return Person.FIRST, Number.SINGULAR, Case.NOMINATIVE
        if pronoun == "me":
            return Person.FIRST, Number.SINGULAR, Case.OBJECTIVE
        if pronoun == "we":
            return Person.FIRST, Number.PLURAL, Case.NOMINATIVE
        if pronoun == "us":
            return Person.FIRST, Number.PLURAL, Case.OBJECTIVE

        # Second person
        # Note: "you" is ambiguous (sg/pl) in modern English; BE verb handles both
        if pronoun in {"you", "ye"}:
            # Return SINGULAR as neutral; BE verb agreement will handle correctly
            return Person.SECOND, Number.SINGULAR, Case.NOMINATIVE
        if pronoun == "thou":
            return Person.SECOND, Number.SINGULAR, Case.NOMINATIVE
        if pronoun == "thee":
            return Person.SECOND, Number.SINGULAR, Case.OBJECTIVE

        # Third person singular
        if pronoun == "he":
            return Person.THIRD, Number.SINGULAR, Case.NOMINATIVE
        if pronoun == "him":
            return Person.THIRD, Number.SINGULAR, Case.OBJECTIVE
        if pronoun == "she":
            return Person.THIRD, Number.SINGULAR, Case.NOMINATIVE
        if pronoun == "her":
            return Person.THIRD, Number.SINGULAR, Case.OBJECTIVE
        if pronoun == "it":
            return Person.THIRD, Number.SINGULAR, Case.NOMINATIVE

        # Third person plural
        if pronoun == "they":
            return Person.THIRD, Number.PLURAL, Case.NOMINATIVE
        if pronoun == "them":
            return Person.THIRD, Number.PLURAL, Case.OBJECTIVE

        # Default
        return Person.THIRD, Number.SINGULAR, Case.NOMINATIVE


# ============================================================================
# PARSER - Syntactic Analysis
# ============================================================================


class SyntacticParser:
    """Performs syntactic analysis of sentences.
    Implements parsing based on Kirkham's grammatical rules.
    """

    # Adverb-like words that commonly intensify adjectives
    ADVERB_LIKE = frozenset(
        {
            "very",
            "quite",
            "rather",
            "too",
            "so",
            "more",
            "most",
            "less",
            "least",
            "really",
            "extremely",
            "fairly",
            "pretty",
            "highly",
            "incredibly",
            "particularly",
        }
    )

    def __init__(
        self, config: ParserConfig | None = None, lexicon: Lexicon | None = None
    ) -> None:
        """Initialize the parser with optional configuration and lexicon.

        Args:
            config: Parser configuration. If None, uses DEFAULT_CONFIG.
            lexicon: Custom lexicon. If None, uses DEFAULT_LEXICON.

        """
        self.config = config or DEFAULT_CONFIG
        self.lex = lexicon or DEFAULT_LEXICON
        self.classifier = PartOfSpeechClassifier(self.lex)
        self.validator = GrammarRuleValidator(self.config)

    def _looks_adverb(self, token: Token) -> bool:
        """Check if token looks like an adverb (intensifier or modifier).

        Handles common adverbial intensifiers that precede adjectives
        like "very good", "quite nice", "rather old".

        Args:
            token: Token to check

        Returns:
            True if token appears to be an adverb

        """
        # Check if it's in the adverb-like set
        if token.lemma in self.ADVERB_LIKE:
            return True

        # Check if explicitly classified as adverb
        if token.pos == PartOfSpeech.ADVERB:
            return True

        # Check for -ly ending (common adverb suffix)
        return bool(token.lemma.endswith("ly"))

    def _detect_sentence_type(self, tokens: list[Token]) -> SentenceType:
        """Detect the type of sentence based on structure and punctuation.

        Handles:
        - Questions (interrogatives): WH-words, question marks, inverted subjects
        - Commands (imperatives): Start with base verb, often no subject
        - Exclamations: Exclamation marks, intensifiers
        - Statements (declaratives): Default

        Args:
            tokens: List of tokens in the sentence

        Returns:
            SentenceType enum value

        Examples:
            "What time is it?" → INTERROGATIVE
            "Sit down!" → IMPERATIVE
            "What a beautiful day!" → EXCLAMATORY
            "The cat sat." → DECLARATIVE

        """
        if not tokens:
            return SentenceType.DECLARATIVE

        # Check punctuation marks
        last_token = tokens[-1]
        if last_token.text == "?":
            return SentenceType.INTERROGATIVE
        if last_token.text == "!":
            # Could be imperative or exclamatory
            # Check for exclamatory patterns: "What a...", "How..."
            if tokens[0].lemma in {"what", "how"} and len(tokens) > 2:
                if tokens[1].pos in {PartOfSpeech.ARTICLE, PartOfSpeech.ADJECTIVE}:
                    return SentenceType.EXCLAMATORY
            return SentenceType.IMPERATIVE

        # Check for WH-words at the start (questions)
        if tokens[0].lemma in {
            "who",
            "what",
            "where",
            "when",
            "why",
            "how",
            "which",
            "whom",
            "whose",
        }:
            return SentenceType.INTERROGATIVE

        # Check for inverted auxiliary (questions): "Do you...", "Is he...", "Can they..."
        if len(tokens) >= 2:
            first = tokens[0]
            second = tokens[1]
            if (
                first.pos == PartOfSpeech.VERB
                and first.lemma
                in Lexicon.AUXILIARY_BE
                | Lexicon.AUXILIARY_HAVE
                | Lexicon.AUXILIARY_DO
                | Lexicon.MODAL_VERBS
            ) and second.pos == PartOfSpeech.PRONOUN:
                return SentenceType.INTERROGATIVE

        # Check for imperatives: start with base verb, no subject before it
        if tokens[0].pos == PartOfSpeech.VERB:
            if self._is_base_verb_shape(tokens[0].lemma):
                # Check if there's a subject pronoun before verb (if not, likely imperative)
                # "You go" (declarative) vs "Go!" (imperative)
                return SentenceType.IMPERATIVE

        # Default to declarative
        return SentenceType.DECLARATIVE

    def _determine_tense(self, verb_phrase: Phrase) -> Tense:
        """Determine the tense of a verb phrase.

        Analyzes auxiliary verbs and main verb forms to determine tense.

        Args:
            verb_phrase: The verb phrase to analyze

        Returns:
            Tense enum value

        Examples:
            "will go" → FUTURE
            "has gone" → PRESENT_PERFECT
            "had gone" → PAST_PERFECT
            "will have gone" → FUTURE_PERFECT
            "goes" → PRESENT
            "went" → PAST

        """
        if not verb_phrase or not verb_phrase.tokens:
            return Tense.PRESENT

        lemmas = [t.lemma for t in verb_phrase.tokens]
        tokens = verb_phrase.tokens

        # Future: will/shall + base
        if any(m in lemmas for m in {"will", "shall"}):
            # Check for perfect: will have + past participle
            if "have" in lemmas or "has" in lemmas:
                return Tense.FUTURE_PERFECT
            return Tense.FUTURE

        # Perfect aspects (have/has/had + past participle)
        if any(aux in lemmas for aux in {"have", "has", "had"}):
            # Check if followed by past participle
            has_participle = any(t.features.get("participle") == "past" for t in tokens)
            if has_participle:
                if "had" in lemmas:
                    return Tense.PAST_PERFECT
                return Tense.PRESENT_PERFECT

        # Simple tenses: check main verb form
        main_verb = tokens[-1]  # Last verb is typically the main verb

        # Check for past tense markers
        if main_verb.lemma.endswith("ed") or TextUtils.is_past_participle(
            main_verb.lemma
        ):
            # Could be past or past participle (but not in perfect context)
            # Check for irregular past forms
            irregular_past = {
                "went",
                "came",
                "saw",
                "made",
                "took",
                "got",
                "gave",
                "found",
                "knew",
                "thought",
                "told",
                "became",
                "left",
                "felt",
                "brought",
                "began",
                "ran",
                "held",
                "heard",
                "kept",
                "meant",
                "met",
                "paid",
                "read",
                "said",
                "sat",
                "sent",
                "stood",
                "understood",
                "wrote",
            }
            if main_verb.lemma in irregular_past:
                return Tense.PAST

            # Check for "was/were" (past BE)
            if main_verb.lemma in {"was", "were"}:
                return Tense.PAST

            return Tense.PAST

        # Present tense (3rd person singular -s or base form with present context)
        if main_verb.features.get("3sg") or main_verb.text.endswith("s"):
            return Tense.PRESENT

        # Check for present BE forms
        if main_verb.lemma in {"am", "is", "are"}:
            return Tense.PRESENT

        # Default to present for base forms
        return Tense.PRESENT

    def parse(self, sentence: str) -> ParseResult:
        """Parse a sentence and return complete analysis.

        Args:
            sentence: Input sentence string

        Returns:
            ParseResult object with complete analysis

        """
        # Tokenize and classify (with character offsets)
        word_tokens = TextUtils.tokenize(sentence)
        tokens = [
            self.classifier.classify(word, start, end)
            for word, start, end in word_tokens
        ]

        # Store original sentence in result
        result = ParseResult(tokens=tokens)
        result.notes.append(
            f"Sentence length: {len(sentence)} chars, {len(tokens)} tokens"
        )

        # Detect sentence type (if enabled)
        if self.config.detect_sentence_type:
            result.sentence_type = self._detect_sentence_type(tokens)

        # Find verb phrase
        verb_phrase = self._find_verb_phrase(tokens)
        result.verb_phrase = verb_phrase

        if not verb_phrase:
            result.warnings.append("No finite verb found in sentence")
            return result

        # Find subject
        subject = self._find_subject(tokens, verb_phrase)
        result.subject = subject

        # Find object
        object_phrase = self._find_object(tokens, verb_phrase)
        result.object_phrase = object_phrase

        # Determine voice (pass tokens for look-ahead)
        result.voice = self._determine_voice(tokens, verb_phrase, object_phrase)

        # Determine tense (if enabled)
        if self.config.detect_tense and verb_phrase:
            result.tense = self._determine_tense(verb_phrase)

        # Validate grammar rules
        self.validator.validate(result)

        return result

    def _find_verb_phrase(self, tokens: list[Token]) -> Phrase | None:
        """Find the main verb phrase in the sentence.
        Implements identification of verb groups including auxiliaries.
        """
        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.VERB:
                # Extend through auxiliary chain
                j = i
                while j + 1 < len(tokens) and tokens[j + 1].pos == PartOfSpeech.VERB:
                    j += 1

                # Create verb phrase
                verb_tokens = tokens[i : j + 1]
                return Phrase(
                    tokens=verb_tokens,
                    phrase_type="VP",
                    head_index=j - i,  # Last verb is head
                )

        return None

    def _find_subject(self, tokens: list[Token], verb_phrase: Phrase) -> Phrase | None:
        """Find the subject noun phrase before the verb.
        Implements RULE 3: The nominative case governs the verb.
        """
        verb_start_idx = tokens.index(verb_phrase.tokens[0])

        # Look backwards from verb for noun/pronoun
        for i in range(verb_start_idx - 1, -1, -1):
            if tokens[i].pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                # Found potential subject, extend to include determiners/adjectives/adverbs
                start_idx = i

                # Include preceding articles, adjectives, possessives, and adverbs
                # Handles: "the very good book", "a rather old man", "John's brother's book"
                # Stop at prepositions to avoid crossing PP boundaries
                j = i - 1
                while j >= 0:
                    token = tokens[j]

                    # Stop at prepositions (don't cross PP boundary)
                    if token.pos == PartOfSpeech.PREPOSITION:
                        break

                    # Include possessives, articles, adjectives, adverbs
                    if (
                        token.case == Case.POSSESSIVE
                        or token.pos in {PartOfSpeech.ARTICLE, PartOfSpeech.ADJECTIVE}
                        or self._looks_adverb(token)
                    ):
                        start_idx = j
                        j -= 1
                    # Stop at anything else
                    else:
                        break

                subject_tokens = tokens[start_idx : i + 1]
                return Phrase(
                    tokens=subject_tokens, phrase_type="NP", head_index=i - start_idx
                )

        return None

    def _find_object(self, tokens: list[Token], verb_phrase: Phrase) -> Phrase | None:
        """Find the object noun phrase after the verb.
        Implements RULE 20: Active-transitive verbs govern the objective case.
        """
        verb_end_idx = tokens.index(verb_phrase.tokens[-1])

        # Look forward from verb for noun/pronoun
        start_idx = None
        end_idx = None

        i = verb_end_idx + 1
        while i < len(tokens):
            token = tokens[i]

            # Stop at punctuation or conjunction
            if token.pos in {PartOfSpeech.PUNCTUATION, PartOfSpeech.CONJUNCTION}:
                break

            # Stop at preposition if we haven't started collecting object
            if token.pos == PartOfSpeech.PREPOSITION and start_idx is None:
                break

            # Collect articles, adjectives, adverbs, nouns, pronouns
            # Handles: "a very good book", "the quite old man"
            if token.pos in {
                PartOfSpeech.ARTICLE,
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.NOUN,
                PartOfSpeech.PRONOUN,
            } or self._looks_adverb(token):
                if start_idx is None:
                    start_idx = i
                end_idx = i
            elif start_idx is not None:
                # Found end of object phrase
                break

            i += 1

        if start_idx is not None and end_idx is not None:
            object_tokens = tokens[start_idx : end_idx + 1]
            # Find head (last noun/pronoun)
            head_idx = 0
            for j, tok in enumerate(object_tokens):
                if tok.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                    head_idx = j

            return Phrase(tokens=object_tokens, phrase_type="NP", head_index=head_idx)

        return None

    def _determine_voice(
        self, tokens: list[Token], verb_phrase: Phrase, object_phrase: Phrase | None
    ) -> Voice:
        """Determine if the verb phrase is active, passive, or neuter voice.

        Handles:
        - Standard be-passive: "was written"
        - Get-passive: "got caught", "gets broken" (if enabled in config)
        - Been + VBN: "has been written"
        - Look-ahead for past participles just outside VP

        Args:
            tokens: All tokens in the sentence
            verb_phrase: The identified verb phrase
            object_phrase: The identified object phrase (if any)

        Returns:
            Voice.PASSIVE, Voice.ACTIVE, or Voice.NEUTER

        """
        if not verb_phrase:
            return Voice.NEUTER

        # Helper: check if token is past participle
        def is_vbn(tok: Token) -> bool:
            return tok.features.get("participle") == "past"

        # Determine which auxiliaries indicate passive
        aux_set = {"be"}
        if self.config.detect_get_passive:
            aux_set.add("get")

        # Check for passive auxiliary in VP
        has_aux = any(
            t.features.get("auxiliary") in aux_set for t in verb_phrase.tokens
        )

        # Check for past participle in VP
        has_vbn_in_vp = any(is_vbn(t) for t in verb_phrase.tokens)

        # Lookahead 2 tokens in case VBN is just outside VP
        vp_last_idx = tokens.index(verb_phrase.tokens[-1]) if verb_phrase.tokens else -1
        if vp_last_idx >= 0:
            lookahead = tokens[vp_last_idx + 1 : vp_last_idx + 3]
            vbn_lookahead = any(is_vbn(t) for t in lookahead)
        else:
            vbn_lookahead = False

        # Passive: has auxiliary (be/get) + past participle
        if has_aux and (has_vbn_in_vp or vbn_lookahead):
            return Voice.PASSIVE

        # Active: has object or explicitly transitive verb
        if object_phrase or any(
            t.features.get("transitive") for t in verb_phrase.tokens
        ):
            return Voice.ACTIVE

        return Voice.NEUTER

    def _is_base_verb_shape(self, lemma: str) -> bool:
        """Check if a lemma has a base verb shape (infinitive form).

        A base verb should:
        - Not be an auxiliary (BE, HAVE, DO, GET, modals)
        - Not end in -s (3rd person singular)
        - Not end in -ed (past tense)
        - Not end in -ing (present participle)
        - Not be irregular past tense (went, saw, etc.)

        Returns:
            True if lemma appears to be a base/infinitive lexical verb

        """
        # Reject auxiliaries - they don't function as infinitive heads
        # "to be", "to have", "to do", etc. are special cases
        if (
            lemma in Lexicon.AUXILIARY_BE
            or lemma in Lexicon.AUXILIARY_HAVE
            or lemma in Lexicon.AUXILIARY_DO
            or lemma in Lexicon.AUXILIARY_GET
            or lemma in Lexicon.MODAL_VERBS
        ):
            return False

        # Common irregular past tense forms (NOT base forms)
        irregular_past_tense = {
            "went",
            "came",
            "saw",
            "made",
            "took",
            "got",
            "gave",
            "found",
            "knew",
            "thought",
            "told",
            "became",
            "left",
            "felt",
            "brought",
            "began",
            "ran",
            "held",
            "heard",
            "kept",
            "meant",
            "met",
            "paid",
            "read",
            "said",
            "sat",
            "sent",
            "stood",
            "understood",
            "wrote",
            "ate",
            "fell",
            "grew",
            "threw",
            "wore",
            "won",
            "spoke",
            "broke",
            "chose",
            "drove",
            "rode",
            "sold",
            "taught",
            "caught",
            "fought",
            "bought",
            "sought",
        }

        # Reject irregular past tense forms
        if lemma in irregular_past_tense:
            return False

        # Reject -ing forms (present participle/gerund)
        if lemma.endswith("ing"):
            return False

        # Reject -ed forms (past tense/participle)
        if lemma.endswith("ed"):
            # Exception: short words like "red", "bed" are not verbs
            if len(lemma) <= 3:
                return False
            return False

        # Reject -s forms (3rd person singular)
        # But allow exceptions like "pass", "class", "bus"
        if lemma.endswith("s") and not lemma.endswith(("ss", "us", "as", "is", "ness")):
            # Check if removing 's' or 'es' gives us a known base verb
            base = lemma[:-1]
            if (
                base in Lexicon.COMMON_TRANSITIVE_VERBS
                or base in Lexicon.COMMON_INTRANSITIVE_VERBS
            ):
                # This is likely a conjugated form (e.g., "walks" -> "walk")
                return False
            # Try removing 'es' for verbs like "goes" -> "go"
            if lemma.endswith("es"):
                base = lemma[:-2]
                if (
                    base in Lexicon.COMMON_TRANSITIVE_VERBS
                    or base in Lexicon.COMMON_INTRANSITIVE_VERBS
                ):
                    return False

        # Known base form lexical verbs (auxiliaries already rejected above)
        if (
            lemma in Lexicon.COMMON_TRANSITIVE_VERBS
            or lemma in Lexicon.COMMON_INTRANSITIVE_VERBS
        ):
            return True

        # For unknown words, assume they might be base form if they pass checks
        return True

    def _find_infinitives(self, tokens: list[Token]) -> list[tuple[int, int]]:
        """Find infinitive phrases (to + verb) in the token sequence.

        Uses safer detection to avoid treating "to" as infinitive marker
        when it's actually a preposition (e.g., "to school", "to him").

        Requirements for infinitive:
        1. "to" followed by a token
        2. Next token must be classified as VERB
        3. Next token must have base verb shape (not tensed)
        4. Not followed by noun/pronoun/adjective (those indicate prepositional use)

        Returns:
            List of (start_idx, end_idx) tuples for infinitive spans

        """
        spans = []

        for i, token in enumerate(tokens):
            # Check for "to"
            if token.lemma == "to" and token.pos == PartOfSpeech.PREPOSITION:
                j = i + 1

                # Check if there's a next token
                if j < len(tokens):
                    next_token = tokens[j]

                    # MUST be classified as VERB
                    if next_token.pos == PartOfSpeech.VERB:
                        # MUST have base verb shape (infinitive form)
                        if self._is_base_verb_shape(next_token.lemma):
                            # This is a valid infinitive: to + base verb
                            spans.append((i, j))

        return spans


# ============================================================================
# GRAMMAR RULE VALIDATOR
# ============================================================================


class GrammarRuleValidator:
    """Validates sentences against Kirkham's grammar rules.
    Implements checking for the 35 rules of syntax from Kirkham's Grammar.
    """

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize validator with optional configuration.

        Args:
            config: Parser configuration. If None, uses DEFAULT_CONFIG.

        """
        self.config = config or DEFAULT_CONFIG

        # Verbs that govern infinitives with objective case subject
        self.gov_inf_verbs = frozenset(
            {
                "want",
                "wants",
                "wanted",
                "wish",
                "wishes",
                "wished",
                "expect",
                "expects",
                "expected",
                "ask",
                "asks",
                "asked",
                "tell",
                "tells",
                "told",
                "permit",
                "permits",
                "permitted",
                "allow",
                "allows",
                "allowed",
                "cause",
                "causes",
                "caused",
                "compel",
                "compels",
                "compelled",
                "advise",
                "advises",
                "advised",
                "encourage",
                "encourages",
                "encouraged",
            }
        )

    def _finite_verb_of_vp(self, vp: Phrase) -> Token:
        """Find the finite verb anchor in a verb phrase.

        Prefers modals, then tensed BE/DO/HAVE auxiliaries, then lexical verbs
        with -s/-ed endings. This helps correctly identify the verb for agreement
        checking in complex auxiliary chains.

        Args:
            vp: Verb phrase to analyze

        Returns:
            The finite verb token (modal, tensed auxiliary, or main verb)

        Example:
            "will have been going" → returns "will" (modal)
            "has been chosen" → returns "has" (tensed auxiliary)
            "walks" → returns "walks" (3sg lexical verb)

        """
        # Prefer modal first
        for t in vp.tokens:
            if t.features.get("modal"):
                return t

        # Then tensed BE/DO/HAVE (not participles)
        for t in vp.tokens:
            if t.features.get("auxiliary") in {
                "be",
                "do",
                "have",
            } and not t.features.get("participle"):
                return t

        # Then any -s/-ed lexical verb
        for t in vp.tokens:
            if t.pos == PartOfSpeech.VERB and (
                t.text.endswith("s") or t.text.endswith("ed")
            ):
                return t

        # Fallback: last verb in chain
        return vp.tokens[-1] if vp.tokens else vp.tokens[0]

    def _pron_case(self, tok: Token) -> Case | None:
        """Get the grammatical case of a pronoun token."""
        return tok.case

    def validate(self, parse_result: ParseResult) -> None:
        """Validate parse result against grammar rules.
        Modifies parse_result in place by adding rule checks and errors.
        Respects parser configuration for rule enforcement.

        Args:
            parse_result: ParseResult object to validate

        """
        # RULE 3: The nominative case governs the verb (if enabled)
        if self.config.enforce_rule_3_strict:
            self._check_rule_3(parse_result)

        # RULE 4: The verb must agree with its nominative in number and person (if enabled)
        if self.config.enforce_rule_4_strict:
            self._check_rule_4(parse_result)

        # RULE 12: Possessive case governed by noun it possesses (if enabled)
        if self.config.enforce_rule_12_strict:
            self._check_rule_12(parse_result)

        # RULE 18: Adjectives belong to and qualify nouns (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_18(parse_result)

        # RULE 20: Active-transitive verbs govern the objective case (if enabled)
        if self.config.enforce_rule_20_strict:
            self._check_rule_20(parse_result)

        # RULE 31: Prepositions govern the objective case (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_31(parse_result)

        # Additional case checks (prep object, copula, governed infinitives)
        if self.config.enable_extended_validation:
            self._check_prep_object_case(parse_result)
            self._check_copula_predicative_case(parse_result)
            self._check_governed_infinitives(parse_result)

    def _check_rule_3(self, parse_result: ParseResult) -> None:
        """RULE 3: The nominative case governs the verb.
        A sentence should have a subject (nominative) for its verb.
        """
        has_subject = parse_result.subject is not None
        parse_result.rule_checks[RuleID.RULE_3.value] = has_subject

        if not has_subject and parse_result.verb_phrase:
            # Create Flag with span for verb phrase
            vp_start = parse_result.verb_phrase.tokens[0].start
            vp_end = parse_result.verb_phrase.tokens[-1].end

            flag = Flag(
                rule=RuleID.RULE_3,
                message="Verb phrase found without subject (nominative)",
                span=Span(start=vp_start, end=vp_end),
            )
            parse_result.flags.append(flag)
            # Backwards compatibility
            parse_result.errors.append(
                "RULE 3 violation: Verb phrase found without subject (nominative)"
            )

    def _check_rule_4(self, parse_result: ParseResult) -> None:
        """RULE 4: The verb must agree with its nominative in number and person."""
        if not parse_result.subject or not parse_result.verb_phrase:
            return

        subject_head = parse_result.subject.head_token

        # For agreement, check the finite verb anchor (modal, tensed auxiliary, or main verb)
        # This handles complex chains like "will have been going" correctly
        verb_to_check = self._finite_verb_of_vp(parse_result.verb_phrase)

        # Check agreement
        agrees = self._check_agreement(subject_head, verb_to_check)
        parse_result.rule_checks[RuleID.RULE_4.value] = agrees

        if not agrees:
            # Create Flag with span covering subject and verb
            span_start = min(subject_head.start, verb_to_check.start)
            span_end = max(subject_head.end, verb_to_check.end)

            flag = Flag(
                rule=RuleID.RULE_4,
                message=f"Verb '{verb_to_check.text}' does not agree with "
                f"subject '{subject_head.text}' in number/person",
                span=Span(start=span_start, end=span_end),
            )
            parse_result.flags.append(flag)
            # Backwards compatibility
            parse_result.errors.append(
                f"RULE 4 violation: Verb '{verb_to_check.text}' does not agree with "
                f"subject '{subject_head.text}' in number/person"
            )

    def _check_agreement(self, subject: Token, verb: Token) -> bool:
        """Check if verb agrees with subject in number and person."""
        subj_number = subject.number or Number.SINGULAR
        subj_person = subject.person or Person.THIRD

        # For "be" verb
        if verb.lemma in Lexicon.AUXILIARY_BE:
            if verb.lemma == "am":
                return subj_person == Person.FIRST and subj_number == Number.SINGULAR
            if verb.lemma == "is":
                return subj_person == Person.THIRD and subj_number == Number.SINGULAR
            if verb.lemma == "are":
                # "are" works with plural OR second person (you are)
                return subj_number == Number.PLURAL or subj_person == Person.SECOND
            if verb.lemma == "was":
                # "was" for 1st/3rd singular (I was, he was) but NOT "you was"
                return subj_number == Number.SINGULAR and subj_person != Person.SECOND
            if verb.lemma == "were":
                # "were" for plural OR second person (you were)
                return subj_number == Number.PLURAL or subj_person == Person.SECOND

        # For regular verbs: 3rd person singular should have -s
        if subj_person == Person.THIRD and subj_number == Number.SINGULAR:
            return verb.text.endswith("s") or verb.features.get("3sg", False)
        # Other persons: verb should not have -s ending (except irregular)
        return not verb.text.endswith("s") or verb.lemma in Lexicon.AUXILIARY_BE

    def _check_rule_12(self, parse_result: ParseResult) -> None:
        """RULE 12: A noun or pronoun in the possessive case is governed by
        the noun which it possesses.
        """
        possessive_pairs = []

        for i, token in enumerate(parse_result.tokens):
            if token.case == Case.POSSESSIVE:
                # Look for following noun
                j = i + 1
                # Skip articles and adjectives
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ARTICLE,
                    PartOfSpeech.ADJECTIVE,
                }:
                    j += 1

                # Check if noun follows
                if (
                    j < len(parse_result.tokens)
                    and parse_result.tokens[j].pos == PartOfSpeech.NOUN
                ):
                    possessive_pairs.append((i, j))
                else:
                    flag = Flag(
                        rule=RuleID.RULE_12,
                        message=f"Possessive '{token.text}' not followed by noun",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 12: Possessive '{token.text}' not followed by noun"
                    )

        if possessive_pairs:
            parse_result.rule_checks["rule_12_possessive_governed"] = True
            parse_result.notes.append(
                f"Found {len(possessive_pairs)} possessive relationship(s)"
            )

    def _check_rule_18(self, parse_result: ParseResult) -> None:
        """RULE 18: Adjectives belong to, and qualify, nouns expressed or understood."""
        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.ADJECTIVE:
                # Check if followed by noun
                has_noun = False
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.NOUN:
                        has_noun = True
                        break
                    if parse_result.tokens[j].pos not in {
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.ARTICLE,
                    }:
                        break

                if not has_noun:
                    flag = Flag(
                        rule=RuleID.RULE_18,  # Adjectives qualify nouns
                        message=f"Adjective '{token.text}' may lack noun to qualify",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 18: Adjective '{token.text}' may lack noun to qualify"
                    )

    def _check_rule_20(self, parse_result: ParseResult) -> None:
        """RULE 20: Active-transitive verbs govern the objective case.
        A transitive verb should have an object.
        """
        if not parse_result.verb_phrase:
            return

        # Check if verb is transitive
        is_transitive = any(
            token.features.get("transitive", False)
            for token in parse_result.verb_phrase.tokens
        )

        if is_transitive and parse_result.voice == Voice.ACTIVE:
            has_object = parse_result.object_phrase is not None
            parse_result.rule_checks[RuleID.RULE_20.value] = has_object

            if not has_object:
                # Create Flag with span for verb phrase
                vp_start = parse_result.verb_phrase.tokens[0].start
                vp_end = parse_result.verb_phrase.tokens[-1].end

                flag = Flag(
                    rule=RuleID.RULE_20,
                    message="Transitive verb may require object (objective case)",
                    span=Span(start=vp_start, end=vp_end),
                )
                parse_result.flags.append(flag)
                # Backwards compatibility
                parse_result.warnings.append(
                    "RULE 20: Transitive verb may require object (objective case)"
                )

    def _check_rule_31(self, parse_result: ParseResult) -> None:
        """RULE 31: Prepositions govern the objective case.
        A preposition should be followed by a noun/pronoun in objective case.
        """
        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PREPOSITION:
                # Look for following noun/pronoun
                found_object = False
                for j in range(i + 1, min(i + 4, len(parse_result.tokens))):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        found_object = True
                        break
                    if parse_result.tokens[j].pos == PartOfSpeech.PUNCTUATION:
                        break

                if not found_object:
                    flag = Flag(
                        rule=RuleID.RULE_31,  # Prepositions govern the objective case
                        message=f"Preposition '{token.text}' lacks object",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 31: Preposition '{token.text}' lacks object"
                    )

    def _check_prep_object_case(self, pr: ParseResult) -> None:
        """Check that prepositions govern objective case pronouns.

        Flags nominative pronouns following prepositions (e.g., "between you and I").
        """
        for i, t in enumerate(pr.tokens):
            if t.pos == PartOfSpeech.PREPOSITION:
                k = i + 1
                # Scan short window for object, skipping articles/adjectives
                while k < len(pr.tokens) and pr.tokens[k].pos in {
                    PartOfSpeech.ARTICLE,
                    PartOfSpeech.ADJECTIVE,
                }:
                    k += 1

                if k < len(pr.tokens) and pr.tokens[k].pos == PartOfSpeech.PRONOUN:
                    if self._pron_case(pr.tokens[k]) == Case.NOMINATIVE:
                        pr.flags.append(
                            Flag(
                                RuleID.RULE_31,
                                f"Preposition '{t.text}' should govern objective case; "
                                f"found nominative '{pr.tokens[k].text}'",
                                Span(pr.tokens[k].start, pr.tokens[k].end),
                            )
                        )

    def _check_copula_predicative_case(self, pr: ParseResult) -> None:
        """Check predicative nominative after copula (be).

        In strict mode, flags objective pronouns after "to be" (e.g., "It is me").
        Respects allow_informal_pronouns config.
        """
        if not pr.verb_phrase:
            return

        # Check if verb phrase contains "be"
        if not any(
            tok.features.get("auxiliary") == "be" for tok in pr.verb_phrase.tokens
        ):
            return

        # Find next NP/pronoun after VP
        last = pr.verb_phrase.tokens[-1]
        start = pr.tokens.index(last) + 1

        if start < len(pr.tokens) and pr.tokens[start].pos == PartOfSpeech.PRONOUN:
            if self._pron_case(pr.tokens[start]) == Case.OBJECTIVE:
                if not self.config.allow_informal_pronouns:
                    pr.flags.append(
                        Flag(
                            RuleID.RULE_4,  # Using RULE_4 for agreement
                            f"After a form of 'to be', use nominative case; "
                            f"found '{pr.tokens[start].text}'",
                            Span(pr.tokens[start].start, pr.tokens[start].end),
                        )
                    )

    def _check_governed_infinitives(self, pr: ParseResult) -> None:
        """Check case of pronoun subject of governed infinitives.

        Verbs like "want", "expect", "tell" govern infinitives whose subject
        should be in objective case (e.g., "I want him to go", not "I want he to go").
        """
        # Find "to + V" sequences
        idxs = [i for i, t in enumerate(pr.tokens) if t.text.lower() == "to"]

        for i in idxs:
            j = i - 1  # Token before "to"
            if j <= 0:
                continue

            k = j - 1  # Token before that (potential governing verb)
            subj = pr.tokens[j]
            gov = pr.tokens[k]

            # Check: pronoun + to, with governing verb before
            if (
                subj.pos == PartOfSpeech.PRONOUN
                and gov.pos == PartOfSpeech.VERB
                and gov.lemma in self.gov_inf_verbs
            ) and self._pron_case(subj) == Case.NOMINATIVE:
                pr.flags.append(
                    Flag(
                        RuleID.RULE_20,  # Using RULE_20 for objective governance
                        f"Subject of governed infinitive after '{gov.text}' "
                        f"should be objective; found '{subj.text}'",
                        Span(subj.start, subj.end),
                    )
                )


# ============================================================================
# OUTPUT FORMATTER
# ============================================================================


class OutputFormatter:
    """Formats parse results for display."""

    @staticmethod
    def format_parse_result(result: ParseResult, show_offsets: bool = False) -> str:
        """Format a complete parse result as a readable string.

        Args:
            result: ParseResult to format
            show_offsets: Whether to show character offsets

        Returns:
            Formatted string representation

        """
        lines = []
        lines.append("=" * 70)
        lines.append("ENGLISH GRAMMAR PARSE RESULT")
        lines.append("=" * 70)

        # Tokens section
        lines.append("\nTOKENS:")
        lines.append("-" * 70)
        for i, token in enumerate(result.tokens):
            offset_str = f" [{token.start}:{token.end}]" if show_offsets else ""
            lines.append(f"{i:3d}. {str(token)}{offset_str}")

        # Parse structure
        lines.append("\nPARSE STRUCTURE:")
        lines.append("-" * 70)

        if result.subject:
            lines.append(f"Subject:  {result.subject.text}")
        else:
            lines.append("Subject:  [NOT FOUND]")

        if result.verb_phrase:
            lines.append(f"Verb:     {result.verb_phrase.text}")
        else:
            lines.append("Verb:     [NOT FOUND]")

        if result.object_phrase:
            lines.append(f"Object:   {result.object_phrase.text}")
        else:
            lines.append("Object:   [NONE]")

        if result.voice:
            lines.append(f"Voice:    {result.voice.value}")

        if result.tense:
            lines.append(f"Tense:    {result.tense.value}")

        if result.sentence_type:
            lines.append(f"Type:     {result.sentence_type.value}")

        # Grammar rule checks
        if result.rule_checks:
            lines.append("\nGRAMMAR RULE CHECKS:")
            lines.append("-" * 70)
            for rule, passed in result.rule_checks.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                lines.append(f"{status}  {rule}")

        # Errors
        if result.errors:
            lines.append("\nERRORS:")
            lines.append("-" * 70)
            for error in result.errors:
                lines.append(f"  ✗ {error}")

        # Warnings
        if result.warnings:
            lines.append("\nWARNINGS:")
            lines.append("-" * 70)
            for warning in result.warnings:
                lines.append(f"  ⚠ {warning}")

        # Notes
        if result.notes:
            lines.append("\nNOTES:")
            lines.append("-" * 70)
            for note in result.notes:
                lines.append(f"  • {note}")

        lines.append("=" * 70)

        return "\n".join(lines)


# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Sentence splitting regex (basic sentence boundary detection)
# Splits on sentence-ending punctuation followed by whitespace and a capital letter or quote
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\u201C])')


class KirkhamParser:
    """Main parser class for English grammar analysis.

    Provides a clean, reusable API for parsing and analyzing English
    sentences based on Kirkham's Grammar rules.

    This class maintains state (config, lexicons) and exposes a simple
    interface: parse(), explain(), to_json().
    """

    def __init__(
        self, cfg: ParserConfig = DEFAULT_CONFIG, lexicon: Lexicon | None = None
    ) -> None:
        """Initialize the parser with configuration and optional lexicon.

        Args:
            cfg: Parser configuration. Defaults to DEFAULT_CONFIG.
            lexicon: Custom lexicon for word lists. Defaults to DEFAULT_LEXICON.
                     Users can extend lexicons without editing code.

        Examples:
            # Default configuration
            parser = Parser()

            # Custom configuration
            cfg = ParserConfig(
                enforce_rule_20_strict=False,
                allow_informal_pronouns=True
            )
            parser = Parser(cfg)

            # Custom lexicon
            custom_lex = Lexicon(
                transitive_verbs=Lexicon.COMMON_TRANSITIVE_VERBS | {"customize", "extend"}
            )
            parser = Parser(lexicon=custom_lex)

        """
        self.cfg = cfg
        self.lex = lexicon or DEFAULT_LEXICON
        self._syntactic_parser = SyntacticParser(self.cfg, self.lex)
        self._formatter = OutputFormatter()

    def parse(self, text: str) -> ParseResult:
        """Parse an English sentence.

        Args:
            text: The sentence to parse

        Returns:
            ParseResult object with complete analysis

        Example:
            >>> parser = Parser()
            >>> result = parser.parse("The cat sat.")
            >>> result.subject.text
            'The cat'

        """
        return self._syntactic_parser.parse(text)

    def explain(self, text: str, show_offsets: bool = False) -> str:
        """Parse and return human-readable explanation.

        Args:
            text: The sentence to parse
            show_offsets: Whether to show character offsets

        Returns:
            Formatted explanation string

        Example:
            >>> parser = Parser()
            >>> print(parser.explain("The cat sat."))

        """
        result = self.parse(text)
        return self._formatter.format_parse_result(result, show_offsets)

    def to_json(self, text: str) -> dict:
        """Parse and return JSON-serializable dictionary.

        Useful for APIs and UIs that need structured data with
        token offsets for highlighting.

        Args:
            text: The sentence to parse

        Returns:
            Dictionary with complete parse information

        Example:
            >>> parser = Parser()
            >>> data = parser.to_json("The cat sat.")
            >>> data['tokens'][0]['text']
            'The'

        """
        result = self.parse(text)
        return result.to_dict()

    def parse_many(self, text: str) -> list[ParseResult]:
        """Parse multiple sentences from a text.

        Performs basic sentence splitting and parses each sentence independently.
        Useful for processing paragraphs or multi-sentence input.

        Args:
            text: Text containing one or more sentences

        Returns:
            List of ParseResult objects, one per sentence

        Example:
            >>> parser = Parser()
            >>> results = parser.parse_many("The cat sat. The dog barked.")
            >>> len(results)
            2
            >>> results[0].subject.text
            'The cat'

        """
        # Split on sentence boundaries
        parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]

        # If no splits found, treat as single sentence
        if not parts:
            parts = [text.strip()]

        # Parse each sentence
        return [self._syntactic_parser.parse(p) for p in parts]

    def show(
        self, text: str, json_only: bool = True, show_offsets: bool = False
    ) -> None:
        """Parse and display with deterministic output control.

        Args:
            text: The sentence to parse
            json_only: If True, output JSON. If False, formatted text.
            show_offsets: If json_only=False, show character offsets.

        Examples:
            >>> parser.show("The cat sat.")  # JSON (default)
            >>> parser.show("The cat sat.", json_only=False)

        """
        import json

        if json_only:
            # Deterministic JSON output
            json_data = self.to_json(text)
            print(json.dumps(json_data, indent=2, sort_keys=True))
        else:
            # Formatted text output (verbose mode)
            print(self.explain(text, show_offsets=show_offsets))

    def parse_batch(
        self, texts: list[str], parallel: bool = False
    ) -> list[ParseResult]:
        """Parse multiple texts efficiently.

        Args:
            texts: List of sentences/paragraphs to parse
            parallel: If True, use multiprocessing for parallel processing
                     (recommended for large batches, >1000 texts)

        Returns:
            List of ParseResult objects, one per text

        Example:
            >>> parser = Parser()
            >>> texts = ["The cat sat.", "The dog barked.", "Birds fly."]
            >>> results = parser.parse_batch(texts)
            >>> len(results)
            3
            >>> results[0].subject.text
            'The cat'

        Note:
            Parallel processing has overhead. For small batches (<100 texts),
            sequential processing may be faster. Test with your workload.

        """
        if parallel:
            try:
                from multiprocessing import Pool, cpu_count

                # Use number of CPUs - 1 to leave one core for OS
                num_processes = max(1, cpu_count() - 1)

                with Pool(processes=num_processes) as pool:
                    return pool.map(self.parse, texts)
            except ImportError:
                # Fallback to sequential if multiprocessing not available
                return [self.parse(text) for text in texts]
        else:
            return [self.parse(text) for text in texts]

    def parse_file(
        self, filepath: str, sentence_per_line: bool = False, encoding: str = "utf-8"
    ) -> list[ParseResult]:
        """Parse text from a file.

        Args:
            filepath: Path to text file to parse
            sentence_per_line: If True, treat each line as a separate sentence.
                              If False, auto-split sentences using parse_many().
            encoding: File encoding (default: utf-8)

        Returns:
            List of ParseResult objects

        Example:
            >>> parser = Parser()
            >>> # File with one sentence per line
            >>> results = parser.parse_file("sentences.txt", sentence_per_line=True)
            >>> # File with paragraphs (auto-split)
            >>> results = parser.parse_file("document.txt", sentence_per_line=False)

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is incorrect

        """
        with open(filepath, encoding=encoding) as f:
            if sentence_per_line:
                lines = [line.strip() for line in f if line.strip()]
                return self.parse_batch(lines)
            text = f.read()
            return self.parse_many(text)
