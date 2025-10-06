"""Unit tests for NLTK integration in the Kirkham Grammar Parser.

Tests cover NLTK-specific functionality:
- NLTK tokenization and POS tagging
- NLTKPOSTag enum usage
- NLTK data downloads
- Integration with Kirkham grammar rules

Author: Based on Samuel Kirkham's English Grammar (1829)
"""

import unittest
from unittest.mock import MagicMock, patch

from kirkham import KirkhamParser
from kirkham.types import NLTKPOSTag, PartOfSpeech


class TestNLTKIntegration(unittest.TestCase):
    """Test suite for NLTK integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = KirkhamParser()

    def test_nltk_components_initialized(self):
        """Test that NLTK components are properly initialized."""
        # Check that NLTK components are available
        assert hasattr(self.parser, "sent_tokenizer")
        assert hasattr(self.parser, "word_tokenizer")
        assert hasattr(self.parser, "pos_tagger")

        # Check that they are callable
        assert callable(self.parser.word_tokenizer)
        assert callable(self.parser.pos_tagger)

    def test_nltk_tokenization(self):
        """Test NLTK tokenization functionality."""
        # Test word tokenization
        tokens = self.parser.word_tokenizer("The cat sat on the mat.")
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "The" in tokens
        assert "cat" in tokens

    def test_nltk_pos_tagging(self):
        """Test NLTK POS tagging functionality."""
        # Test POS tagging
        tokens = ["The", "cat", "sat", "on", "the", "mat", "."]
        tagged = self.parser.pos_tagger(tokens)
        assert isinstance(tagged, list)
        assert len(tagged) == len(tokens)

        # Check that each item is a tuple
        for item in tagged:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_nltk_sentence_tokenization(self):
        """Test NLTK sentence tokenization."""
        # Test sentence tokenization
        text = "The cat sat. The dog barked. Birds fly."
        sentences = self.parser.sent_tokenizer.tokenize(text)
        assert isinstance(sentences, list)
        assert len(sentences) >= 1

    def test_nltk_postag_enum_mapping(self):
        """Test mapping from NLTK POS tags to Kirkham POS."""
        # Test various NLTK tags
        test_cases = [
            ("NN", PartOfSpeech.NOUN),
            ("NNS", PartOfSpeech.NOUN),
            ("PRP", PartOfSpeech.PRONOUN),
            ("VB", PartOfSpeech.VERB),
            ("JJ", PartOfSpeech.ADJECTIVE),
            ("RB", PartOfSpeech.ADVERB),
            ("IN", PartOfSpeech.PREPOSITION),
            ("CC", PartOfSpeech.CONJUNCTION),
            ("DT", PartOfSpeech.ARTICLE),
        ]

        for nltk_tag, expected_pos in test_cases:
            result = self.parser._map_nltk_to_kirkham_pos(nltk_tag, "test")
            assert result == expected_pos, f"Failed for {nltk_tag}"

    def test_nltk_postag_enum_values(self):
        """Test NLTKPOSTag enum values."""
        # Test that enum values match NLTK tags
        assert NLTKPOSTag.NN.value == "NN"
        assert NLTKPOSTag.VB.value == "VB"
        assert NLTKPOSTag.JJ.value == "JJ"
        assert NLTKPOSTag.PRP.value == "PRP"

    def test_nltk_postag_enum_creation(self):
        """Test creating NLTKPOSTag enum from string."""
        # Test valid tags
        assert NLTKPOSTag("NN") == NLTKPOSTag.NN
        assert NLTKPOSTag("VB") == NLTKPOSTag.VB
        assert NLTKPOSTag("JJ") == NLTKPOSTag.JJ

    def test_nltk_postag_enum_invalid(self):
        """Test handling of invalid NLTK POS tags."""
        # Test invalid tag handling
        result = self.parser._map_nltk_to_kirkham_pos("INVALID", "test")
        assert result == PartOfSpeech.NOUN  # Should default to NOUN

    def test_nltk_punctuation_handling(self):
        """Test handling of punctuation in NLTK mapping."""
        # Test punctuation tags
        punctuation_cases = [".", ",", ":", ";", "!", "?", '"', "'"]

        for punct in punctuation_cases:
            result = self.parser._map_nltk_to_kirkham_pos(punct, punct)
            assert result == PartOfSpeech.PUNCTUATION

    def test_nltk_enhanced_tokens(self):
        """Test creation of enhanced tokens from NLTK output."""
        # Test enhanced token creation
        tagged = [("The", "DT"), ("cat", "NN"), ("sat", "VBD"), (".", ".")]
        sentence = "The cat sat."

        enhanced_tokens = self.parser._create_enhanced_tokens(tagged, sentence)

        assert len(enhanced_tokens) == 4
        assert enhanced_tokens[0].text == "The"
        assert enhanced_tokens[0].pos == PartOfSpeech.ARTICLE
        assert enhanced_tokens[1].text == "cat"
        assert enhanced_tokens[1].pos == PartOfSpeech.NOUN
        assert enhanced_tokens[2].text == "sat"
        assert enhanced_tokens[2].pos == PartOfSpeech.VERB

    def test_nltk_grammatical_features(self):
        """Test addition of grammatical features to tokens."""
        from kirkham.models import Token
        from kirkham.types import Case, Gender, Number, Person

        # Test pronoun features
        pronoun_token = Token(
            text="he", lemma="he", pos=PartOfSpeech.PRONOUN, start=0, end=2
        )
        self.parser._add_grammatical_features(pronoun_token)

        assert pronoun_token.case == Case.NOMINATIVE
        assert pronoun_token.number == Number.SINGULAR
        assert pronoun_token.person == Person.THIRD
        assert pronoun_token.gender == Gender.MASCULINE

    def test_nltk_verb_features(self):
        """Test addition of verb features to tokens."""
        from kirkham.models import Token

        # Test linking verb
        linking_token = Token(
            text="is", lemma="is", pos=PartOfSpeech.VERB, start=0, end=2
        )
        self.parser._add_grammatical_features(linking_token)

        assert linking_token.features is not None
        assert linking_token.features.get("is_verb") is True
        assert linking_token.features.get("is_linking") is True

    def test_nltk_integration_with_grammar_rules(self):
        """Test that NLTK integration works with grammar rules."""
        # Test that grammar rules can access NLTK-processed tokens
        result = self.parser.parse("The cats runs.")

        # Should have tokens with NLTK POS tags
        assert len(result.tokens) > 0
        assert all(hasattr(token, "pos") for token in result.tokens)

        # Should have grammar flags (subject-verb disagreement)
        rule_4_flags = [f for f in result.flags if f.rule.value == "RULE_4"]
        assert len(rule_4_flags) > 0

    def test_nltk_data_downloads(self):
        """Test that NLTK data downloads work."""
        # This test ensures that NLTK data is available
        # The actual download happens during parser initialization
        assert self.parser is not None

        # Test that we can use NLTK components
        tokens = self.parser.word_tokenizer("Test sentence.")
        assert len(tokens) > 0

    def test_nltk_error_handling(self):
        """Test error handling in NLTK integration."""
        # Test with malformed input
        result = self.parser.parse("")
        assert len(result.tokens) == 0

        # Test with unusual characters
        result = self.parser.parse("Test with émojis 🎉")
        assert len(result.tokens) > 0

    def test_nltk_performance(self):
        """Test NLTK integration performance."""
        import time

        # Test parsing speed
        start_time = time.time()
        result = self.parser.parse("The quick brown fox jumps over the lazy dog.")
        end_time = time.time()

        # Should complete quickly (less than 1 second)
        assert (end_time - start_time) < 1.0
        assert len(result.tokens) > 0

    def test_nltk_batch_processing(self):
        """Test NLTK integration with batch processing."""
        sentences = [
            "The cat sat on the mat.",
            "She gave me the book.",
            "I am happy.",
        ]

        results = self.parser.parse_batch(sentences)
        assert len(results) == 3

        # Each result should have NLTK-processed tokens
        for result in results:
            assert len(result.tokens) > 0
            assert all(hasattr(token, "pos") for token in result.tokens)

    def test_nltk_consistency(self):
        """Test consistency of NLTK processing."""
        # Parse the same sentence multiple times
        sentence = "The cat sat on the mat."
        results = []

        for _ in range(5):
            result = self.parser.parse(sentence)
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            assert len(results[i].tokens) == len(results[0].tokens)
            for j, token in enumerate(results[i].tokens):
                assert token.text == results[0].tokens[j].text
                assert token.pos == results[0].tokens[j].pos

    def test_nltk_edge_cases(self):
        """Test NLTK integration with edge cases."""
        edge_cases = [
            "A",  # Single character
            "Hello world!",  # Basic sentence
            "The quick brown fox jumps over the lazy dog.",  # Longer sentence
            "What? I said hello!",  # Questions and exclamations
            "Price: $29.99 (50% off!)",  # Numbers and symbols
        ]

        for sentence in edge_cases:
            result = self.parser.parse(sentence)
            assert len(result.tokens) > 0
            assert all(hasattr(token, "pos") for token in result.tokens)


if __name__ == "__main__":
    unittest.main()
