"""Part-of-speech classifier for the Kirkham Grammar Parser.

This module implements a rule-based classification system that determines
the part of speech for each word based on Kirkham's Grammar rules.
"""

from __future__ import annotations

import re

from .lexicon import DEFAULT_LEXICON, Lexicon
from .models import Token
from .types import Case, Gender, Number, PartOfSpeech, Person
from .utils import TextUtils


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
        if lemma in self.lex.possessive_pronouns or is_possessive:
            return self._create_possessive_token(
                word, lemma, base, is_possessive, start, end
            )

        if lemma in self.lex.personal_pronouns:
            return self._create_pronoun_token(word, lemma, start, end)

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

        # Check prepositions (but consider context for ambiguous words)
        if lemma in self.lex.prepositions:
            # Special handling for ambiguous words that can be prepositions or other POS
            if lemma == "like" and self._is_like_noun_context(context):
                # "like" as noun (e.g., "its like", "my like", "the like")
                return self._create_noun_token(word, lemma, is_possessive, start, end)
            return self._create_preposition_token(word, lemma, start, end)

        # Check interjections
        if lemma in self.lex.interjections:
            return self._create_interjection_token(word, lemma, start, end)

        # Check verbs (with higher priority for explicit verb forms)
        # But consider context for ambiguous words that can be verbs or nouns
        if self._is_verb(lemma):
            # Special handling for ambiguous words that can be verbs or nouns
            if lemma == "work" and self._is_work_noun_context(context):
                # "work" as noun (e.g., "the work", "my work", "hard work")
                return self._create_noun_token(word, lemma, is_possessive, start, end)
            return self._create_verb_token(word, lemma, start, end)

        # Check adverbs
        if self._is_adverb(lemma):
            return self._create_adverb_token(word, lemma, start, end)

        # Check explicit adjectives list first
        if lemma in self.lex.common_adjectives:
            # Special handling for ambiguous words that can be adjectives or nouns
            if lemma == "wrong" and self._is_wrong_noun_context(context):
                # "wrong" as noun (e.g., "the wrong", "my wrong")
                return self._create_noun_token(word, lemma, is_possessive, start, end)
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
        # Determine person, number, case, and gender
        person, number, case = self._analyze_pronoun(lemma)
        gender = self._get_pronoun_gender(lemma)

        return Token(
            text=word,
            lemma=lemma,
            pos=PartOfSpeech.PRONOUN,
            start=start,
            end=end,
            person=person,
            number=number,
            case=case,
            gender=gender,
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
            # Determine gender and number for possessive pronouns
            gender = Gender.NEUTER
            number = Number.SINGULAR

            if lemma in {"my", "mine"}:
                gender = Gender.NEUTER  # First person - gender neutral
                number = Number.SINGULAR
            elif lemma in {"your", "yours"}:
                gender = Gender.NEUTER  # Second person - gender neutral
                number = Number.SINGULAR
            elif lemma in {"his"}:
                gender = Gender.MASCULINE
                number = Number.SINGULAR
            elif lemma in {"her", "hers"}:
                gender = Gender.FEMININE
                number = Number.SINGULAR
            elif lemma in {"its"}:
                gender = Gender.NEUTER
                number = Number.SINGULAR
            elif lemma in {"our", "ours"}:
                gender = Gender.NEUTER  # First person plural - gender neutral
                number = Number.PLURAL
            elif lemma in {"their", "theirs"}:
                gender = Gender.NEUTER  # Third person plural - gender neutral
                number = Number.PLURAL

            return Token(
                text=word,
                lemma=lemma,
                pos=PartOfSpeech.PRONOUN,
                start=start,
                end=end,
                case=Case.POSSESSIVE,
                gender=gender,
                number=number,
                person=self._get_person_from_pronoun(lemma),
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

    def _get_person_from_pronoun(self, lemma: str) -> Person:
        """Determine person from pronoun lemma."""
        if lemma in {"my", "mine", "our", "ours"}:
            return Person.FIRST
        if lemma in {"your", "yours"}:
            return Person.SECOND
        if lemma in {"his", "her", "hers", "its", "their", "theirs"}:
            return Person.THIRD
        return Person.THIRD  # Default fallback

    def _get_pronoun_gender(self, lemma: str) -> Gender:
        """Determine gender from pronoun lemma."""
        if lemma in {"i", "me", "we", "us", "my", "mine", "our", "ours"}:
            return Gender.NEUTER  # First person - gender neutral
        if lemma in {"you", "ye", "your", "yours", "thou", "thee", "thy", "thine"}:
            return Gender.NEUTER  # Second person - gender neutral
        if lemma in {"he", "him", "his"}:
            return Gender.MASCULINE
        if lemma in {"she", "her", "hers"}:
            return Gender.FEMININE
        if lemma in {"it", "its"}:
            return Gender.NEUTER
        if lemma in {"they", "them", "their", "theirs"}:
            return Gender.NEUTER  # Third person plural - gender neutral
        return Gender.NEUTER  # Default fallback

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

    def _is_like_noun_context(self, context: list[str] | None) -> bool:
        """Check if 'like' should be classified as a noun based on context.

        Args:
            context: List of surrounding words for context analysis

        Returns:
            True if 'like' should be a noun, False if it should be a preposition
        """
        if not context:
            return False

        # Check if preceded by possessive pronouns or determiners
        possessive_contexts = {
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
            "the",
            "a",
            "an",
            "this",
            "that",
            "these",
            "those",
        }

        # Look at the word immediately before "like"
        for i, word in enumerate(context):
            if word.lower() == "like" and i > 0:
                prev_word = context[i - 1].lower()
                if prev_word in possessive_contexts:
                    return True

        return False

    def _is_work_noun_context(self, context: list[str] | None) -> bool:
        """Check if 'work' should be classified as a noun based on context.

        Args:
            context: List of surrounding words for context analysis

        Returns:
            True if 'work' should be a noun, False if it should be a verb
        """
        if not context:
            return False

        # Check if preceded by articles, possessive pronouns, or adjectives
        noun_contexts = {
            "the",
            "a",
            "an",
            "this",
            "that",
            "these",
            "those",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
            "hard",
            "good",
            "bad",
            "great",
            "important",
            "difficult",
            "easy",
        }

        # Look at the word immediately before "work"
        for i, word in enumerate(context):
            if word.lower() == "work" and i > 0:
                prev_word = context[i - 1].lower()
                if prev_word in noun_contexts:
                    return True

        return False

    def _is_wrong_noun_context(self, context: list[str] | None) -> bool:
        """Check if 'wrong' should be classified as a noun based on context.

        Args:
            context: List of surrounding words for context analysis

        Returns:
            True if 'wrong' should be a noun, False if it should be an adjective
        """
        if not context:
            return False

        # Check if preceded by articles or possessive pronouns
        noun_contexts = {
            "the",
            "a",
            "an",
            "this",
            "that",
            "these",
            "those",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
        }

        # Look at the word immediately before "wrong"
        for i, word in enumerate(context):
            if word.lower() == "wrong" and i > 0:
                prev_word = context[i - 1].lower()
                if prev_word in noun_contexts:
                    return True

        return False
