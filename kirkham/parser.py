"""Main parser class for the Kirkham Grammar Parser.

This module provides the main KirkhamParser class that orchestrates
the parsing process using NLTK for tokenization and POS tagging,
while maintaining all Kirkham grammar rules.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count

import nltk

from .formatter import OutputFormatter
from .lexicon import Lexicon
from .models import (
    DEFAULT_CONFIG,
    Flag,
    ParserConfig,
    ParseResult,
    Span,
    Token,
)
from .types import (
    Case,
    Gender,
    NLTKPOSTag,
    Number,
    PartOfSpeech,
    Person,
    RuleID,
)

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

# Sentence splitting regex (basic sentence boundary detection)
# Splits on sentence-ending punctuation followed by whitespace and a capital
# letter or quote
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\u201C])')


@dataclass
class GrammarError:
    """Represents a grammar error with enhanced information."""

    rule: str
    message: str
    token: Token | None = None
    span: tuple[int, int] | None = None
    severity: str = "error"  # error, warning, info


class KirkhamParser:
    """Main parser class for English grammar analysis using NLTK.

    Provides a clean, reusable API for parsing and analyzing English
    sentences based on Kirkham's Grammar rules using NLTK for tokenization
    and part-of-speech tagging.

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
            parser = KirkhamParser()

            # Custom configuration
            cfg = ParserConfig(
                enforce_rule_20_strict=False,
                allow_informal_pronouns=True
            )
            parser = KirkhamParser(cfg)

            # Custom lexicon
            custom_lex = Lexicon(
                transitive_verbs=Lexicon.COMMON_TRANSITIVE_VERBS
                | {"customize", "extend"}
            )
            parser = KirkhamParser(lexicon=custom_lex)

        """
        self.cfg = cfg
        self.lex = lexicon or Lexicon()
        self._formatter = OutputFormatter()

        # Initialize NLTK components
        self.sent_tokenizer = nltk.data.load("tokenizers/punkt_tab/english.pickle")
        self.word_tokenizer = nltk.word_tokenize
        self.pos_tagger = nltk.pos_tag

    def parse(self, text: str) -> ParseResult:
        """Parse an English sentence using NLTK and Kirkham grammar rules.

        Args:
            text: The sentence to parse

        Returns:
            ParseResult object with complete analysis

        Example:
            >>> parser = KirkhamParser()
            >>> result = parser.parse("The cat sat.")
            >>> result.tokens[0].text
            'The'

        """
        # Split into sentences
        sentences = self.sent_tokenizer.tokenize(text)

        # For now, parse the first sentence (can be extended for multi-sentence)
        if sentences:
            return self._parse_sentence(sentences[0])
        # Return empty result if no sentences found
        return ParseResult(tokens=[], flags=[])

    def _parse_sentence(self, sentence: str) -> ParseResult:
        """Parse a single sentence using NLTK and Kirkham rules."""
        # Tokenize and tag using NLTK
        tokens = self.word_tokenizer(sentence)
        tagged = self.pos_tagger(tokens)

        # Convert to enhanced tokens
        enhanced_tokens = self._create_enhanced_tokens(tagged, sentence)

        # Apply all grammar rules
        flags = []
        rule_checks = {}

        # Check each rule and collect flags
        flags.extend(self._check_article_rules(enhanced_tokens))
        flags.extend(self._check_verb_agreement_rules(enhanced_tokens))
        flags.extend(self._check_pronoun_rules(enhanced_tokens))
        flags.extend(self._check_adjective_rules(enhanced_tokens))
        flags.extend(self._check_verb_case_rules(enhanced_tokens))
        flags.extend(self._check_infinitive_rules(enhanced_tokens))
        flags.extend(self._check_participle_rules(enhanced_tokens))
        flags.extend(self._check_adverb_rules(enhanced_tokens))
        flags.extend(self._check_preposition_rules(enhanced_tokens))
        flags.extend(self._check_conjunction_rules(enhanced_tokens))
        flags.extend(self._check_punctuation_rules(enhanced_tokens))
        flags.extend(self._check_capitalization_rules(enhanced_tokens))

        # Convert flags to the expected format
        kirkham_flags = []
        for flag in flags:
            kirkham_flags.append(
                Flag(
                    rule=RuleID(flag.rule),
                    message=flag.message,
                    span=Span(flag.span[0], flag.span[1]) if flag.span else None,
                )
            )

        return ParseResult(
            tokens=enhanced_tokens, flags=kirkham_flags, rule_checks=rule_checks
        )

    def _create_enhanced_tokens(
        self, tagged: list[tuple[str, str]], sentence: str
    ) -> list[Token]:
        """Convert NLTK tagged tokens to enhanced tokens with grammatical features."""
        enhanced_tokens = []
        char_pos = 0

        for word, pos_tag in tagged:
            # Find position in original sentence
            start = sentence.find(word, char_pos)
            if start == -1:
                start = char_pos
            end = start + len(word)
            char_pos = end

            # Map NLTK POS to Kirkham POS
            kirkham_pos = self._map_nltk_to_kirkham_pos(pos_tag, word)

            # Create enhanced token
            token = Token(
                text=word, lemma=word.lower(), pos=kirkham_pos, start=start, end=end
            )

            # Add grammatical features based on POS tag
            self._add_grammatical_features(token)

            enhanced_tokens.append(token)

        return enhanced_tokens

    def _map_nltk_to_kirkham_pos(self, nltk_pos: str, word: str) -> PartOfSpeech:
        """Map NLTK POS tags to Kirkham PartOfSpeech enum."""
        # Convert string to enum if possible
        try:
            nltk_tag = NLTKPOSTag(nltk_pos)
        except ValueError:
            # Handle punctuation and other characters not in enum
            if nltk_pos in [
                ".",
                ",",
                ":",
                ";",
                "!",
                "?",
                '"',
                "'",
                "(",
                ")",
                "[",
                "]",
                "{",
                "}",
            ]:
                return PartOfSpeech.PUNCTUATION
            return PartOfSpeech.NOUN  # Default fallback

        # Map NLTK tags to Kirkham POS
        mapping = {
            # Nouns
            NLTKPOSTag.NN: PartOfSpeech.NOUN,
            NLTKPOSTag.NNS: PartOfSpeech.NOUN,
            NLTKPOSTag.NNP: PartOfSpeech.NOUN,
            NLTKPOSTag.NNPS: PartOfSpeech.NOUN,
            # Pronouns
            NLTKPOSTag.PRP: PartOfSpeech.PRONOUN,
            NLTKPOSTag.PRP_DOLLAR: PartOfSpeech.PRONOUN,
            NLTKPOSTag.WP: PartOfSpeech.PRONOUN,
            NLTKPOSTag.WP_DOLLAR: PartOfSpeech.PRONOUN,
            # Verbs
            NLTKPOSTag.VB: PartOfSpeech.VERB,
            NLTKPOSTag.VBD: PartOfSpeech.VERB,
            NLTKPOSTag.VBG: PartOfSpeech.VERB,
            NLTKPOSTag.VBN: PartOfSpeech.VERB,
            NLTKPOSTag.VBP: PartOfSpeech.VERB,
            NLTKPOSTag.VBZ: PartOfSpeech.VERB,
            # Adjectives
            NLTKPOSTag.JJ: PartOfSpeech.ADJECTIVE,
            NLTKPOSTag.JJR: PartOfSpeech.ADJECTIVE,
            NLTKPOSTag.JJS: PartOfSpeech.ADJECTIVE,
            # Adverbs
            NLTKPOSTag.RB: PartOfSpeech.ADVERB,
            NLTKPOSTag.RBR: PartOfSpeech.ADVERB,
            NLTKPOSTag.RBS: PartOfSpeech.ADVERB,
            # Prepositions and conjunctions
            NLTKPOSTag.IN: PartOfSpeech.PREPOSITION,
            NLTKPOSTag.CC: PartOfSpeech.CONJUNCTION,
            # Determiners and articles
            NLTKPOSTag.DT: PartOfSpeech.ARTICLE,
            NLTKPOSTag.PDT: PartOfSpeech.ARTICLE,
            # Numbers
            NLTKPOSTag.CD: PartOfSpeech.NOUN,  # Cardinal number -> Noun
            # Other
            NLTKPOSTag.TO: PartOfSpeech.PREPOSITION,  # "to" as infinitive marker
            NLTKPOSTag.MD: PartOfSpeech.VERB,  # Modal verbs
            NLTKPOSTag.EX: PartOfSpeech.PRONOUN,  # Existential "there"
            NLTKPOSTag.FW: PartOfSpeech.NOUN,  # Foreign word
            NLTKPOSTag.LS: PartOfSpeech.PUNCTUATION,  # List marker
            NLTKPOSTag.POS: PartOfSpeech.PUNCTUATION,  # Possessive ending
            NLTKPOSTag.RP: PartOfSpeech.PREPOSITION,  # Particle
            NLTKPOSTag.SYM: PartOfSpeech.PUNCTUATION,  # Symbol
            NLTKPOSTag.UH: PartOfSpeech.INTERJECTION,  # Interjection
            NLTKPOSTag.WDT: PartOfSpeech.PRONOUN,  # Wh-determiner
            NLTKPOSTag.WRB: PartOfSpeech.ADVERB,  # Wh-adverb
            # Punctuation
            NLTKPOSTag.PERIOD: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.COMMA: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.COLON: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.SEMICOLON: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.EXCLAMATION: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.QUESTION: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.QUOTE_DOUBLE: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.QUOTE_SINGLE: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.PAREN_LEFT: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.PAREN_RIGHT: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.BRACKET_LEFT: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.BRACKET_RIGHT: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.BRACE_LEFT: PartOfSpeech.PUNCTUATION,
            NLTKPOSTag.BRACE_RIGHT: PartOfSpeech.PUNCTUATION,
        }

        return mapping.get(nltk_tag, PartOfSpeech.NOUN)  # Default to NOUN

    def _add_grammatical_features(self, token: Token) -> None:
        """Add grammatical features to token based on POS tag and word."""
        word = token.lemma

        # Determine case
        if token.pos == PartOfSpeech.PRONOUN:
            if word in ["i", "we", "he", "she", "they", "who"]:
                token.case = Case.NOMINATIVE
            elif word in ["me", "us", "him", "her", "them", "whom"]:
                token.case = Case.OBJECTIVE
            elif word in ["my", "our", "his", "her", "their", "whose"]:
                token.case = Case.POSSESSIVE
        elif token.pos == PartOfSpeech.NOUN:
            token.case = Case.NOMINATIVE  # Default for nouns

        # Determine number
        if word in ["i", "we"]:
            token.number = Number.PLURAL if word == "we" else Number.SINGULAR
        elif word in ["you", "they"]:
            token.number = Number.PLURAL
        elif word in ["he", "she", "it"]:
            token.number = Number.SINGULAR

        # Determine person
        if word in ["i", "we"]:
            token.person = Person.FIRST
        elif word in ["you"]:
            token.person = Person.SECOND
        elif word in ["he", "she", "it", "they"]:
            token.person = Person.THIRD

        # Determine gender
        if word in ["he", "him", "his"]:
            token.gender = Gender.MASCULINE
        elif word in ["she", "her", "hers"]:
            token.gender = Gender.FEMININE
        elif word in ["it", "its"]:
            token.gender = Gender.NEUTER

        # Add verb features
        if token.pos == PartOfSpeech.VERB:
            token.features = token.features or {}
            token.features["is_verb"] = True
            if word in self.lex.linking_verbs:
                token.features["is_linking"] = True
            if word in self.lex.transitive_verbs:
                token.features["is_transitive"] = True

    def _check_article_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 1 & 2: Article agreement."""
        errors = []

        for i, token in enumerate(tokens):
            if token.lemma in self.lex.articles:
                # Rule 1: 'a' or 'an' must agree with singular nouns
                if token.lemma in ["a", "an"]:
                    # Look for following noun
                    for j in range(i + 1, len(tokens)):
                        next_token = tokens[j]
                        if next_token.pos == PartOfSpeech.NOUN:
                            # Check if it's actually plural (ends with 's' but not possessive)
                            if next_token.text.endswith(
                                "s"
                            ) and not next_token.text.endswith("'s"):
                                errors.append(
                                    GrammarError(
                                        rule="RULE_1",
                                        message=f"Article '{token.text}' must agree with singular noun, but '{next_token.text}' appears to be plural",
                                        token=token,
                                        span=(token.start, next_token.end),
                                    )
                                )
                            break
                        if next_token.pos in [
                            PartOfSpeech.ADJECTIVE,
                            PartOfSpeech.ADVERB,
                        ]:
                            continue  # Skip adjectives/adverbs
                        break

                # Rule 2: 'the' can agree with singular or plural nouns
                elif token.lemma == "the":
                    # Look for following noun
                    noun_found = False
                    for j in range(i + 1, len(tokens)):
                        next_token = tokens[j]
                        if next_token.pos == PartOfSpeech.NOUN:
                            noun_found = True
                            break
                        if next_token.pos in [
                            PartOfSpeech.ADJECTIVE,
                            PartOfSpeech.ADVERB,
                        ]:
                            continue  # Skip adjectives/adverbs
                        break

                    if not noun_found:
                        errors.append(
                            GrammarError(
                                rule="RULE_2",
                                message=f"Article '{token.text}' should be followed by a noun",
                                token=token,
                            )
                        )

        return errors

    def _check_verb_agreement_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 3, 4, 8, 9, 10, 11: Verb agreement."""
        errors = []

        # Find subject-verb pairs
        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.VERB:
                # Find the subject for this verb
                subject = self._find_subject_for_verb(tokens, i)

                if subject:
                    # Rule 4: Verb must agree with subject in number and person
                    if not self._check_subject_verb_agreement(subject, token):
                        errors.append(
                            GrammarError(
                                rule="RULE_4",
                                message=f"Verb '{token.text}' does not agree with subject '{subject.text}' in number/person",
                                token=token,
                                span=(subject.start, token.end),
                            )
                        )

        return errors

    def _find_subject_for_verb(
        self, tokens: list[Token], verb_idx: int
    ) -> Token | None:
        """Find the subject for a given verb."""
        # Look backwards for the subject
        for i in range(verb_idx - 1, -1, -1):
            token = tokens[i]
            if token.pos in [PartOfSpeech.NOUN, PartOfSpeech.PRONOUN]:
                return token
            if token.pos in [
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
                PartOfSpeech.ARTICLE,
            ]:
                continue  # Skip modifiers
            break
        return None

    def _check_subject_verb_agreement(self, subject: Token, verb: Token) -> bool:
        """Check if subject and verb agree in number and person."""
        # Handle compound subjects (Rule 8)
        if self._is_compound_subject(subject):
            return verb.lemma in ["are", "were"] or verb.text in [
                "play",
                "run",
                "walk",
                "talk",
                "work",
                "study",
            ]

        # Handle collective nouns (Rules 10, 11)
        if subject.lemma in self.lex.collective_nouns:
            return verb.lemma in ["is", "was"]
        if subject.lemma in self.lex.multitude_nouns:
            return verb.lemma in ["are", "were"]

        # Check for obvious mismatches based on word form
        # If subject ends with 's' (likely plural) but verb is singular
        if (
            subject.text.endswith("s")
            and not subject.text.endswith("'s")
            and verb.text.endswith("s")
            and verb.lemma not in ["is", "was"]
        ):
            return False
        # If subject doesn't end with 's' (likely singular) but verb is plural
        # Past tense verbs (like "gave") agree with all subjects
        if (
            not subject.text.endswith("s")
            and not verb.text.endswith("s")
            and verb.lemma not in ["are", "were"]
            and not self._is_past_tense_verb(verb)
        ):
            return False

        # Check specific pronoun-verb combinations
        if subject.lemma == "i" and verb.lemma in ["is", "was"]:
            return False
        if subject.lemma == "you" and verb.lemma in ["is", "was"]:
            return False
        if subject.lemma in ["he", "she", "it"] and verb.lemma in ["are", "were"]:
            return False
        if subject.lemma in ["we", "they"] and verb.lemma in ["is", "was"]:
            return False

        return True  # Default to agreement if we can't determine

    def _is_past_tense_verb(self, verb: Token) -> bool:
        """Check if verb is past tense."""
        return verb.lemma in self.lex.past_tense_verbs

    def _is_compound_subject(self, subject: Token) -> bool:
        """Check if subject is compound (contains 'and')."""
        # This is a simplified check - in a full implementation,
        # you'd need to parse the phrase structure
        return "and" in subject.text.lower()

    def _check_pronoun_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 13, 14, 15, 16, 17: Pronoun rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.PRONOUN:
                # Rule 13: Personal pronouns must agree with antecedents
                antecedent = self._find_antecedent(tokens, i)
                if antecedent and not self._check_pronoun_antecedent_agreement(
                    token, antecedent
                ):
                    errors.append(
                        GrammarError(
                            rule="RULE_13",
                            message=f"Personal pronoun '{token.text}' does not agree with antecedent '{antecedent.text}'",
                            token=token,
                            span=(antecedent.start, token.end),
                        )
                    )

        return errors

    def _find_antecedent(self, tokens: list[Token], pronoun_idx: int) -> Token | None:
        """Find the antecedent for a pronoun."""
        # Look backwards for a noun
        for i in range(pronoun_idx - 1, -1, -1):
            token = tokens[i]
            if token.pos == PartOfSpeech.NOUN:
                return token
        return None

    def _check_pronoun_antecedent_agreement(
        self, pronoun: Token, antecedent: Token
    ) -> bool:
        """Check if pronoun agrees with its antecedent."""
        if antecedent.number and pronoun.number:
            return antecedent.number == pronoun.number
        if antecedent.gender and pronoun.gender:
            return antecedent.gender == pronoun.gender
        return True

    def _check_adjective_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 18, 19: Adjective rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.ADJECTIVE:
                # Rule 18: Adjectives qualify nouns
                if not self._adjective_qualifies_noun(tokens, i):
                    errors.append(
                        GrammarError(
                            rule="RULE_18",
                            message=f"Adjective '{token.text}' may lack noun to qualify",
                            token=token,
                        )
                    )

        return errors

    def _adjective_qualifies_noun(self, tokens: list[Token], adj_idx: int) -> bool:
        """Check if adjective qualifies a noun."""
        # Look for noun before or after
        for i in range(adj_idx - 1, -1, -1):
            if tokens[i].pos == PartOfSpeech.NOUN:
                return True
            if tokens[i].pos in [
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
                PartOfSpeech.ARTICLE,
            ]:
                continue
            break

        for i in range(adj_idx + 1, len(tokens)):
            if tokens[i].pos == PartOfSpeech.NOUN:
                return True
            if tokens[i].pos in [
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
                PartOfSpeech.ARTICLE,
            ]:
                continue
            break

        return False

    def _check_verb_case_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 20, 21, 22: Verb case rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.VERB:
                # Rule 20: Transitive verbs govern objective case
                if token.features and token.features.get("is_transitive"):
                    if not self._has_objective_object(tokens, i):
                        errors.append(
                            GrammarError(
                                rule="RULE_20",
                                message=f"Transitive verb '{token.text}' may require object (objective case)",
                                token=token,
                            )
                        )

        return errors

    def _has_objective_object(self, tokens: list[Token], verb_idx: int) -> bool:
        """Check if transitive verb has an objective object."""
        # Look for objective case after verb
        for i in range(verb_idx + 1, len(tokens)):
            token = tokens[i]
            if token.case == Case.OBJECTIVE:
                return True
            if token.pos == PartOfSpeech.NOUN:
                return True  # Assume objective for nouns after transitive verbs
            if token.pos in [
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
                PartOfSpeech.ARTICLE,
            ]:
                continue
            break
        return False

    def _check_infinitive_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 23, 24, 25: Infinitive rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.features and token.features.get("is_infinitive"):
                # Rule 23: Infinitive may be governed by verb, noun, adjective, participle, pronoun
                if not self._infinitive_has_governor(tokens, i):
                    errors.append(
                        GrammarError(
                            rule="RULE_23",
                            message=f"Infinitive '{token.text}' should be governed by a verb, noun, adjective, participle, or pronoun",
                            token=token,
                        )
                    )

        return errors

    def _infinitive_has_governor(self, tokens: list[Token], inf_idx: int) -> bool:
        """Check if infinitive has a governor."""
        # Look backwards for governor
        for i in range(inf_idx - 1, -1, -1):
            token = tokens[i]
            if token.pos in [
                PartOfSpeech.VERB,
                PartOfSpeech.NOUN,
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.PRONOUN,
            ]:
                return True
            if token.lemma == "to":
                continue  # Skip infinitive marker
            break
        return False

    def _check_participle_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 26, 27, 28: Participle rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.features and token.features.get("is_participle"):
                # Rule 27: Present participle refers to subject/actor
                if token.features.get("participle_type") == "present":
                    if not self._participle_refers_to_subject(tokens, i):
                        errors.append(
                            GrammarError(
                                rule="RULE_27",
                                message=f"Present participle '{token.text}' should refer to subject or actor",
                                token=token,
                            )
                        )

        return errors

    def _participle_refers_to_subject(self, tokens: list[Token], part_idx: int) -> bool:
        """Check if participle refers to subject."""
        # Look for subject before or after
        for i in range(part_idx - 1, -1, -1):
            if tokens[i].pos in [PartOfSpeech.NOUN, PartOfSpeech.PRONOUN]:
                return True
        for i in range(part_idx + 1, len(tokens)):
            if tokens[i].pos in [PartOfSpeech.NOUN, PartOfSpeech.PRONOUN]:
                return True
        return False

    def _check_adverb_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rule 29: Adverb rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.ADVERB:
                # Rule 29: Adverbs qualify verbs, participles, adjectives, other adverbs
                if not self._adverb_qualifies_word(tokens, i):
                    errors.append(
                        GrammarError(
                            rule="RULE_29",
                            message=f"Adverb '{token.text}' should qualify a verb, participle, adjective, or other adverb",
                            token=token,
                        )
                    )

        return errors

    def _adverb_qualifies_word(self, tokens: list[Token], adv_idx: int) -> bool:
        """Check if adverb qualifies appropriate word."""
        # Look for qualifiable words before or after
        for i in range(adv_idx - 1, -1, -1):
            token = tokens[i]
            if token.pos in [
                PartOfSpeech.VERB,
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
            ]:
                return True
        for i in range(adv_idx + 1, len(tokens)):
            token = tokens[i]
            if token.pos in [
                PartOfSpeech.VERB,
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
            ]:
                return True
        return False

    def _check_preposition_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 30, 31, 32: Preposition rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.PREPOSITION:
                # Rule 31: Prepositions govern objective case
                if not self._preposition_governs_objective(tokens, i):
                    errors.append(
                        GrammarError(
                            rule="RULE_31",
                            message=f"Preposition '{token.text}' should govern objective case",
                            token=token,
                        )
                    )

        return errors

    def _preposition_governs_objective(
        self, tokens: list[Token], prep_idx: int
    ) -> bool:
        """Check if preposition governs objective case."""
        # Look for objective case after preposition
        for i in range(prep_idx + 1, len(tokens)):
            token = tokens[i]
            if token.case == Case.OBJECTIVE:
                return True
            if token.pos == PartOfSpeech.NOUN:
                return True  # Assume objective for nouns after prepositions
            if token.pos in [
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.ADVERB,
                PartOfSpeech.ARTICLE,
            ]:
                continue
            break
        return False

    def _check_conjunction_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check Rules 33, 34, 35: Conjunction rules."""
        errors = []

        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.CONJUNCTION:
                # Rule 33: Conjunctions connect nouns/pronouns in same case
                if not self._conjunction_connects_same_case(tokens, i):
                    errors.append(
                        GrammarError(
                            rule="RULE_33",
                            message=f"Conjunction '{token.text}' should connect nouns/pronouns in same case",
                            token=token,
                        )
                    )

        return errors

    def _conjunction_connects_same_case(
        self, tokens: list[Token], conj_idx: int
    ) -> bool:
        """Check if conjunction connects same case."""
        # Find nouns/pronouns before and after
        before_case = None
        after_case = None

        for i in range(conj_idx - 1, -1, -1):
            if tokens[i].case:
                before_case = tokens[i].case
                break
        for i in range(conj_idx + 1, len(tokens)):
            if tokens[i].case:
                after_case = tokens[i].case
                break

        return before_case == after_case if before_case and after_case else True

    def _check_punctuation_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check punctuation rules."""
        errors = []

        # Check if sentence ends with proper punctuation
        if tokens and not tokens[-1].text.endswith((".", "!", "?")):
            errors.append(
                GrammarError(
                    rule="PERIOD_RULE",
                    message="Sentence should end with proper punctuation",
                    token=tokens[-1],
                )
            )

        return errors

    def _check_capitalization_rules(self, tokens: list[Token]) -> list[GrammarError]:
        """Check capitalization rules."""
        errors = []

        # First word should be capitalized
        if tokens and not tokens[0].text[0].isupper():
            errors.append(
                GrammarError(
                    rule="COMMA_1",  # Using a valid RuleID for capitalization
                    message="First word of sentence must be capitalized",
                    token=tokens[0],
                )
            )

        # 'I' and 'O' should be capitalized
        for token in tokens:
            if token.lemma in ["i", "o"] and not token.text.isupper():
                errors.append(
                    GrammarError(
                        rule="COMMA_1",  # Using a valid RuleID for capitalization
                        message=f"'{token.text}' must be capitalized",
                        token=token,
                    )
                )

        return errors

    def explain(self, text: str, show_offsets: bool = False) -> str:
        """Parse and return human-readable explanation.

        Args:
            text: The sentence to parse
            show_offsets: Whether to show character offsets

        Returns:
            Formatted explanation string

        Example:
            >>> parser = KirkhamParser()
            >>> print(parser.explain("The cat sat."))

        """
        result = self.parse(text)
        return self._formatter.format_text(result, show_offsets=show_offsets)

    def to_json(self, text: str) -> dict:
        """Parse and return JSON-serializable dictionary.

        Useful for APIs and UIs that need structured data with
        token offsets for highlighting.

        Args:
            text: The sentence to parse

        Returns:
            Dictionary with complete parse information

        Example:
            >>> parser = KirkhamParser()
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
            >>> parser = KirkhamParser()
            >>> results = parser.parse_many("The cat sat. The dog barked.")
            >>> len(results)
            2
            >>> results[0].tokens[0].text
            'The'

        """
        # Split on sentence boundaries
        parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]

        # If no splits found, treat as single sentence
        if not parts:
            parts = [text.strip()]

        # Parse each sentence
        return [self._parse_sentence(p) for p in parts]

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
            >>> parser = KirkhamParser()
            >>> texts = ["The cat sat.", "The dog barked.", "Birds fly."]
            >>> results = parser.parse_batch(texts)
            >>> len(results)
            3
            >>> results[0].tokens[0].text
            'The'

        Note:
            Parallel processing has overhead. For small batches (<100 texts),
            sequential processing may be faster. Test with your workload.

        """
        if parallel:
            try:
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
            >>> parser = KirkhamParser()
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
