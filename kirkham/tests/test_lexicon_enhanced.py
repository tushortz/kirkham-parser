"""Unit tests for the enhanced Lexicon class.

Tests cover the expanded lexicon functionality:
- New word lists (collective nouns, multitude nouns, etc.)
- Context-aware classification support
- Comprehensive vocabulary coverage
- Performance optimizations

Author: Based on Samuel Kirkham's English Grammar (1829)
"""

import unittest

from kirkham.lexicon import Lexicon


class TestEnhancedLexicon(unittest.TestCase):
    """Test suite for enhanced Lexicon functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.lexicon = Lexicon()

    def test_collective_nouns(self):
        """Test collective nouns word list."""
        assert "team" in self.lexicon.collective_nouns
        assert "group" in self.lexicon.collective_nouns
        assert "family" in self.lexicon.collective_nouns
        assert "committee" in self.lexicon.collective_nouns
        assert "audience" in self.lexicon.collective_nouns

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.collective_nouns, frozenset)

    def test_multitude_nouns(self):
        """Test multitude nouns word list."""
        assert "people" in self.lexicon.multitude_nouns
        assert "men" in self.lexicon.multitude_nouns
        assert "women" in self.lexicon.multitude_nouns
        assert "children" in self.lexicon.multitude_nouns
        assert "police" in self.lexicon.multitude_nouns

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.multitude_nouns, frozenset)

    def test_linking_verbs(self):
        """Test linking verbs word list."""
        assert "be" in self.lexicon.linking_verbs
        assert "is" in self.lexicon.linking_verbs
        assert "are" in self.lexicon.linking_verbs
        assert "was" in self.lexicon.linking_verbs
        assert "were" in self.lexicon.linking_verbs
        assert "become" in self.lexicon.linking_verbs
        assert "seem" in self.lexicon.linking_verbs
        assert "appear" in self.lexicon.linking_verbs

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.linking_verbs, frozenset)

    def test_copulative_conjunctions(self):
        """Test copulative conjunctions word list."""
        assert "and" in self.lexicon.copulative_conjunctions
        assert "both...and" in self.lexicon.copulative_conjunctions
        assert "not only...but also" in self.lexicon.copulative_conjunctions
        assert "as well as" in self.lexicon.copulative_conjunctions

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.copulative_conjunctions, frozenset)

    def test_disjunctive_conjunctions(self):
        """Test disjunctive conjunctions word list."""
        assert "or" in self.lexicon.disjunctive_conjunctions
        assert "nor" in self.lexicon.disjunctive_conjunctions
        assert "either...or" in self.lexicon.disjunctive_conjunctions
        assert "neither...nor" in self.lexicon.disjunctive_conjunctions
        assert "but" in self.lexicon.disjunctive_conjunctions

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.disjunctive_conjunctions, frozenset)

    def test_bare_infinitive_verbs(self):
        """Test bare infinitive verbs word list."""
        assert "make" in self.lexicon.bare_infinitive_verbs
        assert "see" in self.lexicon.bare_infinitive_verbs
        assert "hear" in self.lexicon.bare_infinitive_verbs
        assert "let" in self.lexicon.bare_infinitive_verbs
        assert "help" in self.lexicon.bare_infinitive_verbs

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.bare_infinitive_verbs, frozenset)

    def test_understood_prep_nouns(self):
        """Test understood preposition nouns word list."""
        assert "home" in self.lexicon.understood_prep_nouns
        assert "distance" in self.lexicon.understood_prep_nouns
        assert "time" in self.lexicon.understood_prep_nouns
        assert "way" in self.lexicon.understood_prep_nouns
        assert "direction" in self.lexicon.understood_prep_nouns

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.understood_prep_nouns, frozenset)

    def test_comparison_conjunctions(self):
        """Test comparison conjunctions word list."""
        assert "than" in self.lexicon.comparison_conjunctions
        assert "as" in self.lexicon.comparison_conjunctions
        assert "like" in self.lexicon.comparison_conjunctions
        assert "as...as" in self.lexicon.comparison_conjunctions
        assert "more...than" in self.lexicon.comparison_conjunctions

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.comparison_conjunctions, frozenset)

    def test_past_tense_verbs(self):
        """Test past tense verbs word list."""
        assert "gave" in self.lexicon.past_tense_verbs
        assert "went" in self.lexicon.past_tense_verbs
        assert "came" in self.lexicon.past_tense_verbs
        assert "saw" in self.lexicon.past_tense_verbs
        assert "took" in self.lexicon.past_tense_verbs
        assert "made" in self.lexicon.past_tense_verbs

        # Should be a frozenset for performance
        assert isinstance(self.lexicon.past_tense_verbs, frozenset)

    def test_no_duplicates(self):
        """Test that there are no duplicate entries in word lists."""
        # Test collective nouns
        collective_list = list(self.lexicon.collective_nouns)
        assert len(collective_list) == len(set(collective_list))

        # Test multitude nouns
        multitude_list = list(self.lexicon.multitude_nouns)
        assert len(multitude_list) == len(set(multitude_list))

        # Test linking verbs
        linking_list = list(self.lexicon.linking_verbs)
        assert len(linking_list) == len(set(linking_list))

    def test_custom_lexicon_creation(self):
        """Test creating custom lexicon with new word lists."""
        # Create custom lexicon by extending defaults
        default_collective = Lexicon.COLLECTIVE_NOUNS | {"custom_team", "custom_group"}
        default_multitude = Lexicon.MULTITUDE_NOUNS | {"custom_people", "custom_men"}
        default_linking = Lexicon.LINKING_VERBS | {"custom_be", "custom_seem"}

        custom_lexicon = Lexicon(
            collective_nouns=default_collective,
            multitude_nouns=default_multitude,
            linking_verbs=default_linking,
        )

        assert "custom_team" in custom_lexicon.collective_nouns
        assert "custom_people" in custom_lexicon.multitude_nouns
        assert "custom_be" in custom_lexicon.linking_verbs

        # Should still have default words
        assert "team" in custom_lexicon.collective_nouns
        assert "people" in custom_lexicon.multitude_nouns

    def test_lexicon_performance(self):
        """Test lexicon lookup performance."""
        import time

        # Test lookup speed
        start_time = time.time()
        for _ in range(1000):
            _ = "team" in self.lexicon.collective_nouns
            _ = "people" in self.lexicon.multitude_nouns
            _ = "be" in self.lexicon.linking_verbs
        end_time = time.time()

        # Should be very fast (less than 0.1 seconds for 1000 lookups)
        assert (end_time - start_time) < 0.1

    def test_lexicon_memory_usage(self):
        """Test that lexicon uses memory efficiently."""
        # Test that frozensets are used (immutable, memory efficient)
        assert isinstance(self.lexicon.collective_nouns, frozenset)
        assert isinstance(self.lexicon.multitude_nouns, frozenset)
        assert isinstance(self.lexicon.linking_verbs, frozenset)
        assert isinstance(self.lexicon.copulative_conjunctions, frozenset)
        assert isinstance(self.lexicon.disjunctive_conjunctions, frozenset)

    def test_lexicon_completeness(self):
        """Test that lexicon has comprehensive coverage."""
        # Test that we have words for all major categories
        assert len(self.lexicon.collective_nouns) > 20
        assert len(self.lexicon.multitude_nouns) > 20
        assert len(self.lexicon.linking_verbs) > 10
        assert len(self.lexicon.copulative_conjunctions) > 5
        assert len(self.lexicon.disjunctive_conjunctions) > 5
        assert len(self.lexicon.bare_infinitive_verbs) > 10
        assert len(self.lexicon.understood_prep_nouns) > 15
        assert len(self.lexicon.comparison_conjunctions) > 10
        assert len(self.lexicon.past_tense_verbs) > 50

    def test_lexicon_consistency(self):
        """Test that lexicon entries are consistent."""
        # Test that all entries are strings
        for word in self.lexicon.collective_nouns:
            assert isinstance(word, str)
            assert len(word) > 0

        for word in self.lexicon.multitude_nouns:
            assert isinstance(word, str)
            assert len(word) > 0

        for word in self.lexicon.linking_verbs:
            assert isinstance(word, str)
            assert len(word) > 0

    def test_lexicon_case_sensitivity(self):
        """Test that lexicon handles case sensitivity correctly."""
        # Test that entries are lowercase
        for word in self.lexicon.collective_nouns:
            assert word.islower()

        for word in self.lexicon.multitude_nouns:
            assert word.islower()

        for word in self.lexicon.linking_verbs:
            assert word.islower()

    def test_lexicon_special_characters(self):
        """Test that lexicon handles special characters correctly."""
        # Test that multi-word entries are handled
        assert "both...and" in self.lexicon.copulative_conjunctions
        assert "not only...but also" in self.lexicon.copulative_conjunctions
        assert "as...as" in self.lexicon.comparison_conjunctions
        assert "more...than" in self.lexicon.comparison_conjunctions

    def test_lexicon_integration_with_parser(self):
        """Test that lexicon integrates properly with parser."""
        from kirkham import KirkhamParser

        # Test with default lexicon
        parser1 = KirkhamParser()
        result1 = parser1.parse("The team is playing.")

        # Test with custom lexicon
        custom_lexicon = Lexicon(collective_nouns={"custom_team"})
        parser2 = KirkhamParser(lexicon=custom_lexicon)
        result2 = parser2.parse("The custom_team is playing.")

        # Both should work
        assert len(result1.tokens) > 0
        assert len(result2.tokens) > 0


if __name__ == "__main__":
    unittest.main()
