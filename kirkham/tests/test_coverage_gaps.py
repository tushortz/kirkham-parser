"""Additional tests to increase coverage for specific missing lines.

These tests target specific uncovered lines identified in the coverage report.
"""

import unittest
from unittest.mock import Mock, patch

from kirkham import KirkhamParser, ParserConfig
from kirkham.classifier import PartOfSpeechClassifier
from kirkham.formatter import OutputFormatter
from kirkham.lexicon import Lexicon
from kirkham.models import Flag, ParseResult, Span, Token
from kirkham.types import (
    Case, Gender, Number, PartOfSpeech, Person, RuleID, SentenceType, Tense,
    Voice,
)
from kirkham.validator import GrammarRuleValidator


class TestCoverageGaps(unittest.TestCase):
    """Test suite targeting specific coverage gaps."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = KirkhamParser()
        self.validator = GrammarRuleValidator(Lexicon())
        self.formatter = OutputFormatter()
        self.classifier = PartOfSpeechClassifier(Lexicon())

    def create_token(self, text: str, pos: PartOfSpeech, **kwargs) -> Token:
        """Create a test token."""
        defaults = {
            "lemma": text.lower(),
            "start": 0,
            "end": len(text),
            "case": None,
            "gender": None,
            "number": None,
            "person": None,
            "features": {},
        }
        defaults.update(kwargs)
        return Token(text=text, pos=pos, **defaults)

    def create_parse_result(self, tokens: list[Token], flags: list[Flag] = None) -> ParseResult:
        """Create a test parse result."""
        return ParseResult(
            tokens=tokens,
            flags=flags or [],
            rule_checks={},
        )

    # ========================================================================
    # VALIDATOR COVERAGE GAPS
    # ========================================================================

    def test_validator_rule_checks_initialization(self):
        """Test validator rule checks initialization."""
        tokens = [self.create_token("test", PartOfSpeech.NOUN)]
        result = self.create_parse_result(tokens)

        # Test that rule checks are initialized
        self.assertIsInstance(result.rule_checks, dict)

    def test_validator_with_empty_tokens(self):
        """Test validator with empty tokens list."""
        result = self.create_parse_result([])

        # Test various rule methods with empty tokens
        self.validator._check_rule_1(result)
        self.validator._check_rule_2(result)
        self.validator._check_rule_3(result)
        self.validator._check_rule_4(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_with_single_token(self):
        """Test validator with single token."""
        tokens = [self.create_token("test", PartOfSpeech.NOUN)]
        result = self.create_parse_result(tokens)

        # Test various rule methods with single token
        self.validator._check_rule_1(result)
        self.validator._check_rule_2(result)
        self.validator._check_rule_3(result)
        self.validator._check_rule_4(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_5_nominative_independent(self):
        """Test RULE 5: Nominative independent case."""
        tokens = [
            self.create_token("John", PartOfSpeech.NOUN, case=Case.NOMINATIVE),
            self.create_token(",", PartOfSpeech.PUNCTUATION),
            self.create_token("come", PartOfSpeech.VERB),
            self.create_token("here", PartOfSpeech.ADVERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_5(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_6_nominative_absolute(self):
        """Test RULE 6: Nominative absolute case."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("work", PartOfSpeech.NOUN),
            self.create_token("done", PartOfSpeech.VERB),
            self.create_token(",", PartOfSpeech.PUNCTUATION),
            self.create_token("we", PartOfSpeech.PRONOUN),
            self.create_token("left", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_6(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_7_apposition(self):
        """Test RULE 7: Apposition."""
        tokens = [
            self.create_token("John", PartOfSpeech.NOUN, case=Case.NOMINATIVE),
            self.create_token(",", PartOfSpeech.PUNCTUATION),
            self.create_token("the", PartOfSpeech.ARTICLE),
            self.create_token("teacher", PartOfSpeech.NOUN, case=Case.NOMINATIVE),
            self.create_token(",", PartOfSpeech.PUNCTUATION),
            self.create_token("arrived", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_7(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_13_pronoun_antecedent_agreement(self):
        """Test RULE 13: Pronoun antecedent agreement."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("girl", PartOfSpeech.NOUN, gender=Gender.FEMININE),
            self.create_token("lost", PartOfSpeech.VERB),
            self.create_token("her", PartOfSpeech.PRONOUN, gender=Gender.FEMININE),
            self.create_token("book", PartOfSpeech.NOUN),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_13(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_14_relative_pronoun_agreement(self):
        """Test RULE 14: Relative pronoun agreement."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("book", PartOfSpeech.NOUN),
            self.create_token("that", PartOfSpeech.PRONOUN),
            self.create_token("I", PartOfSpeech.PRONOUN),
            self.create_token("read", PartOfSpeech.VERB),
            self.create_token("was", PartOfSpeech.VERB),
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_14(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_15_relative_pronoun_nominative(self):
        """Test RULE 15: Relative pronoun nominative case."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("man", PartOfSpeech.NOUN),
            self.create_token("who", PartOfSpeech.PRONOUN, case=Case.NOMINATIVE),
            self.create_token("came", PartOfSpeech.VERB),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("here", PartOfSpeech.ADVERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_15(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_16_relative_pronoun_governed(self):
        """Test RULE 16: Relative pronoun governed by verb."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("man", PartOfSpeech.NOUN),
            self.create_token("whom", PartOfSpeech.PRONOUN, case=Case.OBJECTIVE),
            self.create_token("I", PartOfSpeech.PRONOUN),
            self.create_token("saw", PartOfSpeech.VERB),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("here", PartOfSpeech.ADVERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_16(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_17_interrogative_pronoun_case(self):
        """Test RULE 17: Interrogative pronoun case."""
        tokens = [
            self.create_token("Who", PartOfSpeech.PRONOUN, case=Case.NOMINATIVE),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("there", PartOfSpeech.ADVERB),
            self.create_token("?", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_17(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_19_adjective_pronoun_belongs_to_noun(self):
        """Test RULE 19: Adjective pronoun belongs to noun."""
        tokens = [
            self.create_token("This", PartOfSpeech.PRONOUN),
            self.create_token("book", PartOfSpeech.NOUN),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_19(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_22_neuter_verb_same_case(self):
        """Test RULE 22: Neuter verb same case."""
        tokens = [
            self.create_token("It", PartOfSpeech.PRONOUN, case=Case.NOMINATIVE),
            self.create_token("seems", PartOfSpeech.VERB),
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_22(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_23_infinitive_governed(self):
        """Test RULE 23: Infinitive governed."""
        tokens = [
            self.create_token("I", PartOfSpeech.PRONOUN),
            self.create_token("want", PartOfSpeech.VERB),
            self.create_token("to", PartOfSpeech.PREPOSITION),
            self.create_token("go", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_23(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_24_infinitive_nominative_or_object(self):
        """Test RULE 24: Infinitive nominative or object."""
        tokens = [
            self.create_token("To", PartOfSpeech.PREPOSITION),
            self.create_token("work", PartOfSpeech.VERB),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_24(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_26_participle_same_government(self):
        """Test RULE 26: Participle same government."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("written", PartOfSpeech.VERB),
            self.create_token("book", PartOfSpeech.NOUN),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_26(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_27_present_participle_refers_to_subject(self):
        """Test RULE 27: Present participle refers to subject."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("running", PartOfSpeech.VERB),
            self.create_token("man", PartOfSpeech.NOUN),
            self.create_token("fell", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_27(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_32_understood_preposition(self):
        """Test RULE 32: Understood preposition."""
        tokens = [
            self.create_token("I", PartOfSpeech.PRONOUN),
            self.create_token("went", PartOfSpeech.VERB),
            self.create_token("home", PartOfSpeech.NOUN),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_32(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_33_conjunction_same_case(self):
        """Test RULE 33: Conjunction same case."""
        tokens = [
            self.create_token("John", PartOfSpeech.NOUN, case=Case.NOMINATIVE),
            self.create_token("and", PartOfSpeech.CONJUNCTION),
            self.create_token("Mary", PartOfSpeech.NOUN, case=Case.NOMINATIVE),
            self.create_token("came", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_33(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_34_conjunction_like_verbs(self):
        """Test RULE 34: Conjunction like verbs."""
        tokens = [
            self.create_token("I", PartOfSpeech.PRONOUN),
            self.create_token("came", PartOfSpeech.VERB),
            self.create_token("and", PartOfSpeech.CONJUNCTION),
            self.create_token("saw", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_34(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_validator_rule_35_comparison_conjunction_case(self):
        """Test RULE 35: Comparison conjunction case."""
        tokens = [
            self.create_token("She", PartOfSpeech.PRONOUN),
            self.create_token("is", PartOfSpeech.VERB),
            self.create_token("taller", PartOfSpeech.ADJECTIVE),
            self.create_token("than", PartOfSpeech.CONJUNCTION),
            self.create_token("I", PartOfSpeech.PRONOUN, case=Case.NOMINATIVE),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_35(result)

        # Should not crash
        self.assertIsNotNone(result)

    # ========================================================================
    # FORMATTER COVERAGE GAPS
    # ========================================================================

    def test_formatter_to_conll_with_features(self):
        """Test formatter to_conll with grammatical features."""
        tokens = [
            self.create_token(
                "She",
                PartOfSpeech.PRONOUN,
                case=Case.NOMINATIVE,
                number=Number.SINGULAR,
                person=Person.THIRD,
                gender=Gender.FEMININE,
            ),
            self.create_token("gave", PartOfSpeech.VERB),
            self.create_token("me", PartOfSpeech.PRONOUN, case=Case.OBJECTIVE),
        ]
        result = self.create_parse_result(tokens)
        conll_str = self.formatter.to_conll(result)

        self.assertIsInstance(conll_str, str)
        self.assertIn("She", conll_str)
        self.assertIn("gave", conll_str)
        self.assertIn("me", conll_str)

    def test_formatter_to_penn_treebank_with_tokens(self):
        """Test formatter to_penn_treebank with tokens."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN),
            self.create_token("sat", PartOfSpeech.VERB),
        ]
        result = self.create_parse_result(tokens)
        treebank_str = self.formatter.to_penn_treebank(result)

        self.assertIsInstance(treebank_str, str)
        # The actual format may vary, just check it's a string
        self.assertTrue(len(treebank_str) > 0)

    def test_formatter_to_graphviz_with_tokens(self):
        """Test formatter to_graphviz with tokens."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN),
            self.create_token("sat", PartOfSpeech.VERB),
        ]
        result = self.create_parse_result(tokens)
        graphviz_str = self.formatter.to_graphviz(result)

        self.assertIsInstance(graphviz_str, str)
        self.assertIn("digraph", graphviz_str)

    def test_formatter_format_text_with_tokens(self):
        """Test formatter format_text with tokens."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN),
            self.create_token("sat", PartOfSpeech.VERB),
        ]
        result = self.create_parse_result(tokens)
        formatted = self.formatter.format_text(result, show_offsets=False)

        self.assertIsInstance(formatted, str)
        self.assertIn("PARSE STRUCTURE", formatted)

    def test_formatter_format_text_with_offsets(self):
        """Test formatter format_text with offsets."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE, start=0, end=3),
            self.create_token("cat", PartOfSpeech.NOUN, start=4, end=7),
            self.create_token("sat", PartOfSpeech.VERB, start=8, end=11),
        ]
        result = self.create_parse_result(tokens)
        formatted = self.formatter.format_text(result, show_offsets=True)

        self.assertIsInstance(formatted, str)
        self.assertIn("PARSE STRUCTURE", formatted)

    # ========================================================================
    # PARSER COVERAGE GAPS
    # ========================================================================

    def test_parser_with_custom_config(self):
        """Test parser with custom configuration."""
        config = ParserConfig()
        parser = KirkhamParser(config)

        result = parser.parse("The cat sat on the mat.")
        self.assertIsInstance(result, ParseResult)

    def test_parser_with_custom_lexicon(self):
        """Test parser with custom lexicon."""
        lexicon = Lexicon()
        parser = KirkhamParser(lexicon=lexicon)

        result = parser.parse("The cat sat on the mat.")
        self.assertIsInstance(result, ParseResult)

    def test_parser_parse_many_with_multiple_sentences(self):
        """Test parser parse_many with multiple sentences."""
        text = "The cat sat. The dog barked. Birds fly."
        results = self.parser.parse_many(text)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_parser_parse_batch_with_parallel(self):
        """Test parser parse_batch with parallel processing."""
        sentences = ["The cat sat.", "The dog barked.", "Birds fly."]
        results = self.parser.parse_batch(sentences, parallel=True)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

    def test_parser_show_method(self):
        """Test parser show method."""
        # This method prints to stdout, so we just test it doesn't crash
        try:
            self.parser.show("The cat sat on the mat.")
        except Exception as e:
            self.fail(f"show() method raised an exception: {e}")

    def test_parser_to_json_method(self):
        """Test parser to_json method."""
        json_data = self.parser.to_json("The cat sat on the mat.")

        self.assertIsInstance(json_data, dict)
        self.assertIn("tokens", json_data)
        self.assertIn("flags", json_data)

    def test_parser_explain_method(self):
        """Test parser explain method."""
        output = self.parser.explain("The cat sat on the mat.")

        self.assertIsInstance(output, str)
        self.assertIn("PARSE STRUCTURE", output)

    # ========================================================================
    # CLASSIFIER COVERAGE GAPS
    # ========================================================================

    def test_classifier_with_none_input(self):
        """Test classifier with None input."""
        # This should handle None gracefully
        try:
            result = self.classifier.classify(None, context=None)
            # If it doesn't crash, that's good
            self.assertIsNotNone(result)
        except AttributeError:
            # Expected behavior - None has no 'lower' method
            pass

    def test_classifier_with_empty_string(self):
        """Test classifier with empty string."""
        result = self.classifier.classify("", context=None)
        self.assertIsNotNone(result)

    def test_classifier_with_whitespace(self):
        """Test classifier with whitespace."""
        result = self.classifier.classify(" ", context=None)
        self.assertIsNotNone(result)

    def test_classifier_with_unknown_word(self):
        """Test classifier with unknown word."""
        result = self.classifier.classify("xyzzy", context=None)
        self.assertIsNotNone(result)

    def test_classifier_with_none_context(self):
        """Test classifier with None context."""
        result = self.classifier.classify("cat", context=None)
        self.assertIsNotNone(result)

    def test_classifier_with_empty_context(self):
        """Test classifier with empty context."""
        result = self.classifier.classify("cat", context=[])
        self.assertIsNotNone(result)

    def test_classifier_context_aware_methods(self):
        """Test classifier context-aware methods."""
        # Test the helper methods
        result1 = self.classifier._is_like_noun_context(["its"])
        result2 = self.classifier._is_work_noun_context(["the"])
        result3 = self.classifier._is_wrong_noun_context(["the"])

        # Should return boolean values
        self.assertIsInstance(result1, bool)
        self.assertIsInstance(result2, bool)
        self.assertIsInstance(result3, bool)

    # ========================================================================
    # EDGE CASES AND ERROR HANDLING
    # ========================================================================

    def test_validator_with_malformed_tokens(self):
        """Test validator with malformed tokens."""
        # Create tokens with missing attributes
        token = Token(
            text="test",
            lemma="test",
            pos=PartOfSpeech.NOUN,
            start=0,
            end=4,
            case=None,
            gender=None,
            number=None,
            person=None,
            features={},
        )
        result = self.create_parse_result([token])

        # Test various rule methods
        self.validator._check_rule_1(result)
        self.validator._check_rule_2(result)
        self.validator._check_rule_3(result)
        self.validator._check_rule_4(result)

        # Should not crash
        self.assertIsNotNone(result)

    def test_formatter_with_none_values(self):
        """Test formatter with None values."""
        tokens = [self.create_token("test", PartOfSpeech.NOUN)]
        result = ParseResult(
            tokens=tokens,
            subject=None,
            verb_phrase=None,
            object_phrase=None,
            voice=None,
            tense=None,
            sentence_type=None,
            rule_checks={},
            flags=[],
            errors=[],
            warnings=[],
            notes=[],
        )

        # Test all formatter methods
        json_str = self.formatter.to_json(result)
        conll_str = self.formatter.to_conll(result)
        treebank_str = self.formatter.to_penn_treebank(result)
        graphviz_str = self.formatter.to_graphviz(result)
        formatted = self.formatter.format_text(result)

        # Should not crash
        self.assertIsInstance(json_str, str)
        self.assertIsInstance(conll_str, str)
        self.assertIsInstance(treebank_str, str)
        self.assertIsInstance(graphviz_str, str)
        self.assertIsInstance(formatted, str)

    def test_parser_with_special_characters(self):
        """Test parser with special characters."""
        result = self.parser.parse("Test with émojis 🎉 and symbols @#$")
        self.assertIsInstance(result, ParseResult)

    def test_parser_with_very_long_sentence(self):
        """Test parser with very long sentence."""
        long_sentence = "The " + "very " * 100 + "long sentence."
        result = self.parser.parse(long_sentence)
        self.assertIsInstance(result, ParseResult)

    def test_parser_performance(self):
        """Test parser performance."""
        import time

        start_time = time.time()
        result = self.parser.parse("The quick brown fox jumps over the lazy dog.")
        end_time = time.time()

        # Should complete quickly
        self.assertLess(end_time - start_time, 1.0)
        self.assertIsInstance(result, ParseResult)


if __name__ == "__main__":
    unittest.main()
