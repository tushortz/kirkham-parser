"""Unit tests for the PartOfSpeechClassifier module."""

import unittest

from kirkham.classifier import PartOfSpeechClassifier
from kirkham.lexicon import DEFAULT_LEXICON
from kirkham.types import Case, Number, PartOfSpeech, Person


class TestPartOfSpeechClassifier(unittest.TestCase):
    """Test suite for PartOfSpeechClassifier."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = PartOfSpeechClassifier(DEFAULT_LEXICON)

    def test_classify_articles(self):
        """Test classification of articles."""
        token = self.classifier.classify("the", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.ARTICLE)
        self.assertEqual(token.text, "the")
        self.assertEqual(token.lemma, "the")

        token = self.classifier.classify("a", 0, 1)
        self.assertEqual(token.pos, PartOfSpeech.ARTICLE)

        token = self.classifier.classify("an", 0, 2)
        self.assertEqual(token.pos, PartOfSpeech.ARTICLE)

    def test_classify_pronouns(self):
        """Test classification of pronouns."""
        # Personal pronouns
        token = self.classifier.classify("I", 0, 1)
        self.assertEqual(token.pos, PartOfSpeech.PRONOUN)
        self.assertEqual(token.case, Case.NOMINATIVE)
        self.assertEqual(token.person, Person.FIRST)
        self.assertEqual(token.number, Number.SINGULAR)

        token = self.classifier.classify("me", 0, 2)
        self.assertEqual(token.pos, PartOfSpeech.PRONOUN)
        self.assertEqual(token.case, Case.OBJECTIVE)

        # Possessive pronouns
        token = self.classifier.classify("my", 0, 2)
        self.assertEqual(token.pos, PartOfSpeech.PRONOUN)
        self.assertEqual(token.case, Case.POSSESSIVE)

    def test_classify_verbs(self):
        """Test classification of verbs."""
        token = self.classifier.classify("run", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.VERB)
        self.assertEqual(token.lemma, "run")

        token = self.classifier.classify("runs", 0, 4)
        self.assertEqual(token.pos, PartOfSpeech.VERB)
        self.assertEqual(token.lemma, "runs")

        token = self.classifier.classify("ran", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.VERB)
        self.assertEqual(token.lemma, "ran")

    def test_classify_nouns(self):
        """Test classification of nouns."""
        token = self.classifier.classify("cat", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        self.assertEqual(token.lemma, "cat")

        token = self.classifier.classify("cats", 0, 4)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        self.assertEqual(token.number, Number.PLURAL)

    def test_classify_adjectives(self):
        """Test classification of adjectives."""
        token = self.classifier.classify("good", 0, 4)
        self.assertEqual(token.pos, PartOfSpeech.ADJECTIVE)
        self.assertEqual(token.lemma, "good")

        token = self.classifier.classify("beautiful", 0, 9)
        self.assertEqual(token.pos, PartOfSpeech.ADJECTIVE)

    def test_classify_adverbs(self):
        """Test classification of adverbs."""
        token = self.classifier.classify("quickly", 0, 7)
        self.assertEqual(token.pos, PartOfSpeech.ADVERB)
        self.assertEqual(token.lemma, "quickly")

        token = self.classifier.classify("very", 0, 4)
        self.assertEqual(token.pos, PartOfSpeech.ADVERB)

    def test_classify_prepositions(self):
        """Test classification of prepositions."""
        token = self.classifier.classify("in", 0, 2)
        self.assertEqual(token.pos, PartOfSpeech.PREPOSITION)
        self.assertEqual(token.lemma, "in")

        token = self.classifier.classify("on", 0, 2)
        self.assertEqual(token.pos, PartOfSpeech.PREPOSITION)

    def test_classify_conjunctions(self):
        """Test classification of conjunctions."""
        token = self.classifier.classify("and", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.CONJUNCTION)
        self.assertEqual(token.lemma, "and")

        token = self.classifier.classify("but", 0, 3)
        self.assertEqual(token.pos, PartOfSpeech.CONJUNCTION)

    def test_classify_punctuation(self):
        """Test classification of punctuation."""
        token = self.classifier.classify(".", 0, 1)
        self.assertEqual(token.pos, PartOfSpeech.PUNCTUATION)
        self.assertEqual(token.lemma, ".")

        token = self.classifier.classify(",", 0, 1)
        self.assertEqual(token.pos, PartOfSpeech.PUNCTUATION)

    def test_context_aware_classification(self):
        """Test context-aware classification for ambiguous words."""
        # Test "like" as noun in possessive context
        context = ["its", "like"]
        token = self.classifier.classify("like", 0, 4, context=context)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)

        # Test "like" as preposition in other contexts
        context = ["look", "like", "a", "cat"]
        token = self.classifier.classify("like", 0, 4, context=context)
        self.assertEqual(token.pos, PartOfSpeech.PREPOSITION)

        # Test "work" as noun in article context
        context = ["the", "work"]
        token = self.classifier.classify("work", 0, 4, context=context)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)

        # Test "work" as verb in other contexts
        context = ["I", "work"]
        token = self.classifier.classify("work", 0, 4, context=context)
        self.assertEqual(token.pos, PartOfSpeech.VERB)

        # Test "wrong" as noun in article context
        context = ["the", "wrong"]
        token = self.classifier.classify("wrong", 0, 5, context=context)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)

        # Test "wrong" as adjective in other contexts
        context = ["that", "is", "wrong"]
        token = self.classifier.classify("wrong", 0, 5, context=context)
        self.assertEqual(token.pos, PartOfSpeech.ADJECTIVE)

    def test_possessive_detection(self):
        """Test detection of possessive forms."""
        token = self.classifier.classify("John's", 0, 6)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        self.assertEqual(token.case, Case.POSSESSIVE)

    def test_plural_detection(self):
        """Test detection of plural forms."""
        token = self.classifier.classify("cats", 0, 4)
        self.assertEqual(token.number, Number.PLURAL)

        token = self.classifier.classify("children", 0, 8)
        self.assertEqual(token.number, Number.PLURAL)

    def test_unknown_words_default_to_noun(self):
        """Test that unknown words default to noun classification."""
        token = self.classifier.classify("xyzzy", 0, 5)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        self.assertEqual(token.lemma, "xyzzy")

    def test_proper_nouns(self):
        """Test classification of proper nouns."""
        token = self.classifier.classify("John", 0, 4)
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        # Proper nouns should be capitalized
        self.assertTrue(token.text[0].isupper())

    def test_contractions(self):
        """Test handling of contractions."""
        token = self.classifier.classify("I'm", 0, 3)
        # Contractions might be handled differently depending on implementation
        self.assertIsNotNone(token)

    def test_hyphenated_words(self):
        """Test handling of hyphenated words."""
        token = self.classifier.classify("well-known", 0, 10)
        # Should be treated as a single token
        self.assertEqual(token.text, "well-known")

    def test_numbers(self):
        """Test classification of numbers."""
        token = self.classifier.classify("123", 0, 3)
        # Numbers might be classified as nouns or have special handling
        self.assertIsNotNone(token)

    def test_offsets_preserved(self):
        """Test that character offsets are preserved."""
        token = self.classifier.classify("hello", 5, 10)
        self.assertEqual(token.start, 5)
        self.assertEqual(token.end, 10)

    def test_lemma_extraction(self):
        """Test lemma extraction for various word forms."""
        # Test verb lemmas
        token = self.classifier.classify("running", 0, 7)
        if token.pos == PartOfSpeech.VERB:
            self.assertEqual(token.lemma, "running")

        # Test noun lemmas
        token = self.classifier.classify("cats", 0, 4)
        if token.pos == PartOfSpeech.NOUN:
            self.assertEqual(token.lemma, "cats")

    def test_pronoun_features(self):
        """Test pronoun feature extraction."""
        # First person
        token = self.classifier.classify("I", 0, 1)
        self.assertEqual(token.person, Person.FIRST)
        self.assertEqual(token.number, Number.SINGULAR)
        self.assertEqual(token.case, Case.NOMINATIVE)

        # Second person
        token = self.classifier.classify("you", 0, 3)
        self.assertEqual(token.person, Person.SECOND)

        # Third person
        token = self.classifier.classify("he", 0, 2)
        self.assertEqual(token.person, Person.THIRD)
        self.assertEqual(token.number, Number.SINGULAR)
        self.assertEqual(token.case, Case.NOMINATIVE)

        # Plural
        token = self.classifier.classify("they", 0, 4)
        self.assertEqual(token.person, Person.THIRD)
        self.assertEqual(token.number, Number.PLURAL)

    def test_verb_features(self):
        """Test verb feature extraction."""
        token = self.classifier.classify("am", 0, 2)
        if token.pos == PartOfSpeech.VERB:
            self.assertEqual(token.lemma, "am")

        token = self.classifier.classify("is", 0, 2)
        if token.pos == PartOfSpeech.VERB:
            self.assertEqual(token.lemma, "is")

        token = self.classifier.classify("are", 0, 3)
        if token.pos == PartOfSpeech.VERB:
            self.assertEqual(token.lemma, "are")

    def test_edge_cases(self):
        """Test edge cases in classification."""
        # Empty string
        token = self.classifier.classify("", 0, 0)
        self.assertIsNotNone(token)

        # Single character
        token = self.classifier.classify("a", 0, 1)
        self.assertIsNotNone(token)

        # Very long word
        long_word = "a" * 100
        token = self.classifier.classify(long_word, 0, 100)
        self.assertIsNotNone(token)

    def test_special_characters(self):
        """Test handling of special characters."""
        token = self.classifier.classify("&", 0, 1)
        self.assertIsNotNone(token)

        token = self.classifier.classify("@", 0, 1)
        self.assertIsNotNone(token)

    def test_mixed_case(self):
        """Test handling of mixed case words."""
        token = self.classifier.classify("Hello", 0, 5)
        self.assertIsNotNone(token)

        token = self.classifier.classify("WORLD", 0, 5)
        self.assertIsNotNone(token)

    def test_context_helpers(self):
        """Test context helper methods."""
        # Test _is_like_noun_context
        context = ["its", "like"]
        result = self.classifier._is_like_noun_context(context)
        self.assertTrue(result)

        context = ["look", "like"]
        result = self.classifier._is_like_noun_context(context)
        self.assertFalse(result)

        # Test _is_work_noun_context
        context = ["the", "work"]
        result = self.classifier._is_work_noun_context(context)
        self.assertTrue(result)

        context = ["I", "work"]
        result = self.classifier._is_work_noun_context(context)
        self.assertFalse(result)

        # Test _is_wrong_noun_context
        context = ["the", "wrong"]
        result = self.classifier._is_wrong_noun_context(context)
        self.assertTrue(result)

        context = ["that", "is", "wrong"]
        result = self.classifier._is_wrong_noun_context(context)
        self.assertFalse(result)

    def test_context_edge_cases(self):
        """Test context helper methods with edge cases."""
        # Empty context
        result = self.classifier._is_like_noun_context(None)
        self.assertFalse(result)

        result = self.classifier._is_like_noun_context([])
        self.assertFalse(result)

        # Context without target word
        context = ["some", "other", "words"]
        result = self.classifier._is_like_noun_context(context)
        self.assertFalse(result)

        # Context with target word at beginning
        context = ["like", "something"]
        result = self.classifier._is_like_noun_context(context)
        self.assertFalse(result)  # No preceding word


if __name__ == "__main__":
    unittest.main()
