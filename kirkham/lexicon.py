"""Lexicon module for the Kirkham Grammar Parser.

This module contains the word lists and vocabulary used for part-of-speech
classification and grammar analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
