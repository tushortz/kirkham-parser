"""Type definitions and enumerations for the Kirkham Grammar Parser.

This module contains all the enumerations and type definitions used throughout
the parser, providing type safety and clear interfaces.
"""

from __future__ import annotations

from enum import Enum


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
