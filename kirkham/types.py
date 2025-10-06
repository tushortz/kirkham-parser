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


class NLTKPOSTag(Enum):
    """NLTK Part-of-Speech tag enumeration."""

    # Nouns
    NN = "NN"  # noun, singular or mass
    NNS = "NNS"  # noun, plural
    NNP = "NNP"  # proper noun, singular
    NNPS = "NNPS"  # proper noun, plural

    # Pronouns
    PRP = "PRP"  # personal pronoun
    PRP_DOLLAR = "PRP$"  # possessive pronoun
    WP = "WP"  # wh-pronoun
    WP_DOLLAR = "WP$"  # possessive wh-pronoun

    # Verbs
    VB = "VB"  # verb, base form
    VBD = "VBD"  # verb, past tense
    VBG = "VBG"  # verb, gerund or present participle
    VBN = "VBN"  # verb, past participle
    VBP = "VBP"  # verb, non-3rd person singular present
    VBZ = "VBZ"  # verb, 3rd person singular present

    # Adjectives
    JJ = "JJ"  # adjective
    JJR = "JJR"  # adjective, comparative
    JJS = "JJS"  # adjective, superlative

    # Adverbs
    RB = "RB"  # adverb
    RBR = "RBR"  # adverb, comparative
    RBS = "RBS"  # adverb, superlative

    # Prepositions and conjunctions
    IN = "IN"  # preposition or subordinating conjunction
    CC = "CC"  # coordinating conjunction

    # Determiners and articles
    DT = "DT"  # determiner
    PDT = "PDT"  # predeterminer

    # Numbers
    CD = "CD"  # cardinal number

    # Other
    TO = "TO"  # to
    MD = "MD"  # modal
    EX = "EX"  # existential there
    FW = "FW"  # foreign word
    LS = "LS"  # list item marker
    POS = "POS"  # possessive ending
    RP = "RP"  # particle
    SYM = "SYM"  # symbol
    UH = "UH"  # interjection
    WDT = "WDT"  # wh-determiner
    WRB = "WRB"  # wh-adverb

    # Punctuation
    PERIOD = "."
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    EXCLAMATION = "!"
    QUESTION = "?"
    QUOTE_DOUBLE = '"'
    QUOTE_SINGLE = "'"
    PAREN_LEFT = "("
    PAREN_RIGHT = ")"
    BRACKET_LEFT = "["
    BRACKET_RIGHT = "]"
    BRACE_LEFT = "{"
    BRACE_RIGHT = "}"


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

    # Article Rules
    RULE_1 = "RULE_1"  # A/an agrees with its noun in the singular only
    RULE_2 = "RULE_2"  # The belongs to nouns to limit/define their meaning

    # Subject-Verb Agreement Rules
    RULE_3 = "RULE_3"  # Nominative case governs verb
    RULE_4 = "RULE_4"  # Verb agrees with subject in number and person
    RULE_5 = "RULE_5"  # Nominative independent (address)
    RULE_6 = "RULE_6"  # Nominative absolute
    RULE_7 = "RULE_7"  # Apposition
    RULE_8 = "RULE_8"  # Compound subjects need plural verb/pronoun
    RULE_9 = "RULE_9"  # Disjunctive conjunctions
    RULE_10 = "RULE_10"  # Collective nouns (unity)
    RULE_11 = "RULE_11"  # Nouns of multitude (plurality)
    RULE_12 = "RULE_12"  # Possessive governance

    # Pronoun Agreement Rules
    RULE_13 = "RULE_13"  # Personal pronouns agree with their nouns in gender and number
    RULE_14 = "RULE_14"  # Relative pronouns agree with antecedents
    RULE_15 = "RULE_15"  # Relative nominative case
    RULE_16 = "RULE_16"  # Relative governed by verb
    RULE_17 = "RULE_17"  # Interrogative pronoun agreement

    # Adjective Rules
    RULE_18 = "RULE_18"  # Adjectives qualify nouns
    RULE_19 = "RULE_19"  # Adjective pronouns belong to nouns

    # Verb and Case Rules
    RULE_20 = "RULE_20"  # Active-transitive verbs govern objective case
    RULE_21 = "RULE_21"  # To be admits the same case after it as before it
    RULE_22 = "RULE_22"  # Neuter verbs same case
    RULE_23 = "RULE_23"  # Infinitive governed by word
    RULE_24 = "RULE_24"  # Infinitive as nominative/object
    RULE_25 = "RULE_25"  # Bare infinitive after certain verbs
    RULE_26 = "RULE_26"  # Participles same government
    RULE_27 = "RULE_27"  # Present participle refers to subject
    RULE_28 = "RULE_28"  # Perfect participle belongs to noun/pronoun

    # Adverb Rules
    RULE_29 = (
        "RULE_29"  # Adverbs qualify verbs, participles, adjectives, and other adverbs
    )

    # Preposition Rules
    RULE_30 = "RULE_30"  # Prepositions are generally placed before the case they govern
    RULE_31 = "RULE_31"  # Prepositions govern the objective case
    RULE_32 = "RULE_32"  # Nouns governed by understood preposition
    RULE_33 = "RULE_33"  # Conjunctions connect same case
    RULE_34 = "RULE_34"  # Conjunctions connect like moods/tenses
    RULE_35 = "RULE_35"  # Noun/pronoun after than/as/but

    # Orthography (Spelling) Rules
    ORTHO_I = "ORTHO_I"  # Monosyllables ending in f, l, or s: double final consonant
    ORTHO_II = "ORTHO_II"  # Polysyllables ending in f, l, or s: accent-based doubling
    ORTHO_III = "ORTHO_III"  # Words ending in y after consonant: change y → i
    ORTHO_IV = "ORTHO_IV"  # Words ending in y after vowel: retain y
    ORTHO_V = "ORTHO_V"  # Suffixes -able, -ous: drop final e except after c/g
    ORTHO_VI = "ORTHO_VI"  # Final silent e: drop before vowel-initial suffix
    ORTHO_VII = "ORTHO_VII"  # Additional derivative/spelling cases
    ORTHO_VIII = "ORTHO_VIII"  # Additional derivative/spelling cases
    ORTHO_IX = "ORTHO_IX"  # Additional derivative/spelling cases
    ORTHO_X = "ORTHO_X"  # Adding -ing or -ish: drop final e

    # Punctuation Rules
    COMMA_1 = "COMMA_1"  # Simple sentence members not separated by comma
    COMMA_2 = (
        "COMMA_2"  # Long simple sentence: comma before verb if nominative has adjunct
    )
    COMMA_3 = "COMMA_3"  # Interrupted simple sentence: set off adjuncts with commas
    COMMA_4 = "COMMA_4"  # Nominative independent and nouns in apposition take commas
    COMMA_5 = "COMMA_5"  # Absolute/participial/infinitive phrases set off by commas
    COMMA_6 = "COMMA_6"  # Compound sentence: commas between members
    COMMA_7 = "COMMA_7"  # Comparatives and restrictive relatives: comma usage
    COMMA_8 = "COMMA_8"  # Pairs/series of words/clauses distinguished by commas
    COMMA_9 = "COMMA_9"  # Marked contrast takes commas at breaks
    COMMA_10 = "COMMA_10"  # Verb to be: comma governed by connection

    SEMICOLON_1 = "SEMICOLON_1"  # Divides compound members less closely connected
    SEMICOLON_2 = "SEMICOLON_2"  # Before "as" introducing examples

    COLON_1 = "COLON_1"  # Complete member followed by supplemental remark
    COLON_2 = "COLON_2"  # After semicolons when greater pause needed

    PERIOD_RULE = "PERIOD_RULE"  # Complete independent sentence ends with period
    DASH_RULE = "DASH_RULE"  # Sudden breaks, significant pauses, unexpected turns
    INTERROGATION_RULE = (
        "INTERROGATION_RULE"  # Direct questions end with interrogation mark
    )
    EXCLAMATION_RULE = "EXCLAMATION_RULE"  # Strong emotion ends with exclamation mark
    APOSTROPHE_RULE = "APOSTROPHE_RULE"  # Apostrophe usage rules
    QUOTATION_RULE = "QUOTATION_RULE"  # Quotation mark usage rules
