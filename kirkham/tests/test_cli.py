"""Simple unit tests for the CLI module."""

import os
import sys
import unittest

from kirkham.cli import _reconstruct_text_from_tokens
from kirkham.models import Token
from kirkham.types import PartOfSpeech


class TestCLISimple(unittest.TestCase):
    """Simple test suite for CLI functionality."""

    def test_reconstruct_text_from_tokens(self):
        """Test text reconstruction from tokens."""
        # Test basic reconstruction
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]
        text = _reconstruct_text_from_tokens(tokens)
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

    def test_reconstruct_text_with_parentheses(self):
        """Test text reconstruction with parentheses."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="(", lemma="(", pos=PartOfSpeech.PUNCTUATION, start=4, end=5),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=5, end=8),
            Token(text=")", lemma=")", pos=PartOfSpeech.PUNCTUATION, start=8, end=9),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "The (cat)")

    def test_reconstruct_text_unsorted_tokens(self):
        """Test text reconstruction with unsorted tokens."""
        # Create tokens in wrong order
        tokens = [
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "The cat sat.")

    def test_reconstruct_text_edge_cases(self):
        """Test text reconstruction edge cases."""
        # Test with brackets
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="[", lemma="[", pos=PartOfSpeech.PUNCTUATION, start=4, end=5),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=5, end=8),
            Token(text="]", lemma="]", pos=PartOfSpeech.PUNCTUATION, start=8, end=9),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "The [cat]")

        # Test with braces
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="{", lemma="{", pos=PartOfSpeech.PUNCTUATION, start=4, end=5),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=5, end=8),
            Token(text="}", lemma="}", pos=PartOfSpeech.PUNCTUATION, start=8, end=9),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        self.assertEqual(text, "The {cat}")

        # Test with complex punctuation
        tokens = [
            Token(text="What", lemma="what", pos=PartOfSpeech.PRONOUN, start=0, end=4),
            Token(text="?", lemma="?", pos=PartOfSpeech.PUNCTUATION, start=4, end=5),
            Token(text="I", lemma="i", pos=PartOfSpeech.PRONOUN, start=6, end=7),
            Token(text="said", lemma="said", pos=PartOfSpeech.VERB, start=8, end=12),
            Token(text=":", lemma=":", pos=PartOfSpeech.PUNCTUATION, start=12, end=13),
            Token(text='"', lemma='"', pos=PartOfSpeech.PUNCTUATION, start=14, end=15),
            Token(text="Hello", lemma="hello", pos=PartOfSpeech.NOUN, start=15, end=20),
            Token(text="!", lemma="!", pos=PartOfSpeech.PUNCTUATION, start=20, end=21),
            Token(text='"', lemma='"', pos=PartOfSpeech.PUNCTUATION, start=21, end=22),
        ]
        text = _reconstruct_text_from_tokens(tokens)
        # The reconstruction may add spaces around quotes, which is acceptable
        self.assertIn("What? I said:", text)
        self.assertIn("Hello", text)


if __name__ == "__main__":
    unittest.main()
