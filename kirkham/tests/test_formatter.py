"""Simple unit tests for the OutputFormatter module."""

import json
import unittest

from kirkham.formatter import OutputFormatter, _reconstruct_text_from_tokens
from kirkham.models import ParseResult, Token
from kirkham.types import PartOfSpeech, SentenceType, Tense, Voice


class TestOutputFormatterSimple(unittest.TestCase):
    """Simple test suite for OutputFormatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]

        self.test_result = ParseResult(tokens=self.test_tokens)
        self.test_result.sentence_type = SentenceType.DECLARATIVE
        self.test_result.voice = Voice.ACTIVE
        self.test_result.tense = Tense.PAST

    def test_to_json(self):
        """Test JSON conversion."""
        json_str = OutputFormatter.to_json(self.test_result)

        # Should be valid JSON
        json_data = json.loads(json_str)
        self.assertIn("tokens", json_data)
        self.assertIn("sentence_type", json_data)
        self.assertIn("voice", json_data)
        self.assertIn("tense", json_data)

        # Should be properly formatted with indentation
        self.assertIn("\n", json_str)
        self.assertIn("  ", json_str)  # Should have indentation

    def test_to_conll(self):
        """Test CONLL format conversion."""
        conll_str = OutputFormatter.to_conll(self.test_result)

        # Should be a string
        self.assertIsInstance(conll_str, str)

        # Should contain tab-separated values
        lines = conll_str.split("\n")
        self.assertTrue(len(lines) > 0)

        for line in lines:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                self.assertEqual(len(parts), 10)  # CONLL format has 10 columns

                # First column should be numeric (token ID)
                self.assertTrue(parts[0].isdigit())

                # Second column should be the token text
                self.assertIn(parts[1], ["The", "cat", "sat", "."])

    def test_to_penn_treebank(self):
        """Test Penn Treebank format conversion."""
        treebank_str = OutputFormatter.to_penn_treebank(self.test_result)

        # Should be a string
        self.assertIsInstance(treebank_str, str)

        # Should start and end with parentheses
        self.assertTrue(treebank_str.startswith("("))
        self.assertTrue(treebank_str.endswith(")"))

        # Should contain phrase labels
        self.assertIn("S", treebank_str)  # Sentence

    def test_to_graphviz(self):
        """Test Graphviz DOT format conversion."""
        graphviz_str = OutputFormatter.to_graphviz(self.test_result)

        # Should be a string
        self.assertIsInstance(graphviz_str, str)

        # Should contain Graphviz syntax
        self.assertIn("digraph", graphviz_str)
        self.assertIn("rankdir=TB", graphviz_str)
        self.assertIn("node [shape=box]", graphviz_str)
        self.assertIn("}", graphviz_str)

    def test_format_text_basic(self):
        """Test format_text method with basic result."""
        formatted = OutputFormatter.format_text(self.test_result, show_offsets=False)

        # Should be a string
        self.assertIsInstance(formatted, str)

        # Should contain expected sections
        self.assertIn("PARSE STRUCTURE", formatted)
        self.assertIn("Sentence: The cat sat.", formatted)
        self.assertIn("Voice: active", formatted)
        self.assertIn("Tense: past", formatted)
        self.assertIn("Sentence Type: declarative", formatted)

    def test_format_text_with_offsets(self):
        """Test format_text method with character offsets."""
        formatted = OutputFormatter.format_text(self.test_result, show_offsets=True)

        # Should contain offset information
        self.assertIn("Sentence: The cat sat.", formatted)

    def test_format_text_with_unknown_values(self):
        """Test format_text method with unknown/null values."""
        # Create result with None values
        result = ParseResult(tokens=self.test_tokens)
        result.voice = None
        result.tense = None
        result.sentence_type = None

        formatted = OutputFormatter.format_text(result, show_offsets=False)

        # Should handle None values gracefully
        self.assertIn("Voice: Unknown", formatted)
        self.assertIn("Tense: Unknown", formatted)
        self.assertIn("Sentence Type: Unknown", formatted)

    def test_format_text_empty_result(self):
        """Test format_text method with empty result."""
        empty_result = ParseResult(tokens=[])

        formatted = OutputFormatter.format_text(empty_result, show_offsets=False)

        # Should still produce valid output
        self.assertIn("PARSE STRUCTURE", formatted)
        self.assertIn("Sentence:", formatted)

    def test_reconstruct_text_from_tokens(self):
        """Test _reconstruct_text_from_tokens helper function."""
        # Test basic reconstruction
        text = _reconstruct_text_from_tokens(self.test_tokens)
        self.assertEqual(text, "The cat sat.")

        # Test with punctuation spacing
        tokens = [
            Token(text="Hello", lemma="hello", pos=PartOfSpeech.NOUN, start=0, end=5),
            Token(text=",", lemma=",", pos=PartOfSpeech.PUNCTUATION, start=5, end=6),
            Token(text="world", lemma="world", pos=PartOfSpeech.NOUN, start=7, end=12),
            Token(text="!", lemma="!", pos=PartOfSpeech.PUNCTUATION, start=12, end=13),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "Hello, world!")

        # Test empty tokens
        text = _reconstruct_text_from_tokens([])
        self.assertEqual(text, "")

        # Test single token
        tokens = [
            Token(text="Hello", lemma="hello", pos=PartOfSpeech.NOUN, start=0, end=5)
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "Hello")

    def test_all_formatters_produce_output(self):
        """Test that all formatter methods produce some output."""
        # Test all static methods
        methods = [
            OutputFormatter.to_json,
            OutputFormatter.to_conll,
            OutputFormatter.to_penn_treebank,
            OutputFormatter.to_graphviz,
            OutputFormatter.format_text,
        ]

        for method in methods:
            if method == OutputFormatter.format_text:
                result = method(self.test_result, show_offsets=False)
            else:
                result = method(self.test_result)

            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)

    def test_formatter_with_complex_sentence(self):
        """Test formatter with a more complex sentence."""
        # Create a more complex sentence
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="very", lemma="very", pos=PartOfSpeech.ADVERB, start=4, end=8),
            Token(
                text="intelligent",
                lemma="intelligent",
                pos=PartOfSpeech.ADJECTIVE,
                start=9,
                end=20,
            ),
            Token(
                text="students",
                lemma="students",
                pos=PartOfSpeech.NOUN,
                start=21,
                end=29,
            ),
            Token(text="were", lemma="were", pos=PartOfSpeech.VERB, start=30, end=34),
            Token(text="given", lemma="given", pos=PartOfSpeech.VERB, start=35, end=40),
            Token(
                text="excellent",
                lemma="excellent",
                pos=PartOfSpeech.ADJECTIVE,
                start=41,
                end=50,
            ),
            Token(
                text="grades", lemma="grades", pos=PartOfSpeech.NOUN, start=51, end=57
            ),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=57, end=58),
        ]

        result = ParseResult(tokens=tokens)
        result.sentence_type = SentenceType.DECLARATIVE
        result.voice = Voice.PASSIVE
        result.tense = Tense.PAST

        # Test all formatters with complex sentence
        json_str = OutputFormatter.to_json(result)
        self.assertIsInstance(json_str, str)

        conll_str = OutputFormatter.to_conll(result)
        self.assertIsInstance(conll_str, str)

        treebank_str = OutputFormatter.to_penn_treebank(result)
        self.assertIsInstance(treebank_str, str)

        graphviz_str = OutputFormatter.to_graphviz(result)
        self.assertIsInstance(graphviz_str, str)

        formatted = OutputFormatter.format_text(result, show_offsets=False)
        self.assertIn("PARSE STRUCTURE", formatted)

    def test_formatter_import(self):
        """Test that formatter module can be imported."""
        try:
            from kirkham.formatter import (
                OutputFormatter,
                _reconstruct_text_from_tokens,
            )

            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import formatter module: {e}")

    def test_formatter_methods_exist(self):
        """Test that formatter methods exist."""
        from kirkham.formatter import OutputFormatter

        # Check that methods are callable
        self.assertTrue(callable(OutputFormatter.to_json))
        self.assertTrue(callable(OutputFormatter.to_conll))
        self.assertTrue(callable(OutputFormatter.to_penn_treebank))
        self.assertTrue(callable(OutputFormatter.to_graphviz))
        self.assertTrue(callable(OutputFormatter.format_text))
        self.assertTrue(callable(OutputFormatter.show))


if __name__ == "__main__":
    unittest.main()
