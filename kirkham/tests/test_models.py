"""Unit tests for the models module."""

import json
import unittest

from kirkham.models import Flag, ParserConfig, ParseResult, Phrase, Span, Token
from kirkham.types import (
    Case,
    Number,
    PartOfSpeech,
    Person,
    RuleID,
    SentenceType,
    Tense,
    Voice,
)


class TestModels(unittest.TestCase):
    """Test suite for models."""

    def test_parser_config_creation(self):
        """Test ParserConfig creation."""
        config = ParserConfig()
        self.assertIsNotNone(config)
        self.assertTrue(config.enforce_rule_1_strict)
        self.assertTrue(config.enforce_rule_2_strict)
        self.assertTrue(config.enforce_ortho_rules)

    def test_parser_config_customization(self):
        """Test ParserConfig customization."""
        config = ParserConfig(
            enforce_rule_1_strict=False,
            enforce_rule_2_strict=False,
            enforce_ortho_rules=False,
        )
        self.assertFalse(config.enforce_rule_1_strict)
        self.assertFalse(config.enforce_rule_2_strict)
        self.assertFalse(config.enforce_ortho_rules)

    def test_parser_config_presets(self):
        """Test ParserConfig presets."""
        # Test strict formal preset
        strict_config = ParserConfig.strict_formal()
        self.assertFalse(strict_config.allow_informal_pronouns)
        self.assertTrue(strict_config.enforce_rule_20_strict)

        # Test modern permissive preset
        permissive_config = ParserConfig.modern_permissive()
        self.assertTrue(permissive_config.allow_informal_pronouns)

        # Test educational preset
        educational_config = ParserConfig.educational()
        self.assertTrue(educational_config.enable_extended_validation)
        self.assertTrue(educational_config.detect_sentence_type)
        self.assertTrue(educational_config.detect_tense)

    def test_token_creation(self):
        """Test Token creation."""
        token = Token(
            text="hello", lemma="hello", pos=PartOfSpeech.NOUN, start=0, end=5
        )
        self.assertEqual(token.text, "hello")
        self.assertEqual(token.lemma, "hello")
        self.assertEqual(token.pos, PartOfSpeech.NOUN)
        self.assertEqual(token.start, 0)
        self.assertEqual(token.end, 5)

    def test_token_with_features(self):
        """Test Token creation with grammatical features."""
        token = Token(
            text="I",
            lemma="i",
            pos=PartOfSpeech.PRONOUN,
            start=0,
            end=1,
            case=Case.NOMINATIVE,
            person=Person.FIRST,
            number=Number.SINGULAR,
        )
        self.assertEqual(token.case, Case.NOMINATIVE)
        self.assertEqual(token.person, Person.FIRST)
        self.assertEqual(token.number, Number.SINGULAR)

    def test_token_str_representation(self):
        """Test Token string representation."""
        token = Token(
            text="hello", lemma="hello", pos=PartOfSpeech.NOUN, start=0, end=5
        )
        str_repr = str(token)
        self.assertIn("hello", str_repr)
        self.assertIn("noun", str_repr)

    def test_token_to_dict(self):
        """Test Token to_dict method."""
        token = Token(
            text="hello",
            lemma="hello",
            pos=PartOfSpeech.NOUN,
            start=0,
            end=5,
            case=Case.NOMINATIVE,
        )
        token_dict = token.to_dict()
        self.assertEqual(token_dict["text"], "hello")
        self.assertEqual(token_dict["lemma"], "hello")
        self.assertEqual(token_dict["pos"], "noun")
        self.assertEqual(token_dict["start"], 0)
        self.assertEqual(token_dict["end"], 5)
        self.assertEqual(token_dict["case"], "nominative")

    def test_phrase_creation(self):
        """Test Phrase creation."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
        ]
        phrase = Phrase(tokens=tokens, phrase_type="NP", head_index=1)
        self.assertEqual(phrase.tokens, tokens)
        self.assertEqual(phrase.phrase_type, "NP")
        self.assertEqual(phrase.head_index, 1)

    def test_phrase_head_token(self):
        """Test Phrase head_token property."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
        ]
        phrase = Phrase(tokens=tokens, phrase_type="NP", head_index=1)
        self.assertEqual(phrase.head_token, tokens[1])

    def test_phrase_text(self):
        """Test Phrase text property."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
        ]
        phrase = Phrase(tokens=tokens, phrase_type="NP", head_index=1)
        self.assertEqual(phrase.text, "The cat")

    def test_phrase_properties(self):
        """Test Phrase properties."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
        ]
        phrase = Phrase(tokens=tokens, phrase_type="NP", head_index=1)
        self.assertEqual(phrase.phrase_type, "NP")
        self.assertEqual(phrase.head_index, 1)
        self.assertEqual(phrase.tokens, tokens)
        self.assertEqual(phrase.head_token, tokens[1])
        self.assertEqual(phrase.text, "The cat")

    def test_parse_result_creation(self):
        """Test ParseResult creation."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]
        result = ParseResult(tokens=tokens)
        self.assertEqual(result.tokens, tokens)
        self.assertIsInstance(result.flags, list)
        self.assertIsInstance(result.warnings, list)
        self.assertIsInstance(result.errors, list)
        self.assertIsInstance(result.notes, list)
        self.assertIsInstance(result.rule_checks, dict)

    def test_parse_result_with_analysis(self):
        """Test ParseResult with grammatical analysis."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]

        subject_tokens = [tokens[0], tokens[1]]
        subject = Phrase(tokens=subject_tokens, phrase_type="NP", head_index=1)

        verb_tokens = [tokens[2]]
        verb_phrase = Phrase(tokens=verb_tokens, phrase_type="VP", head_index=0)

        result = ParseResult(tokens=tokens)
        result.subject = subject
        result.verb_phrase = verb_phrase
        result.sentence_type = SentenceType.DECLARATIVE
        result.voice = Voice.ACTIVE
        result.tense = Tense.PAST

        self.assertEqual(result.subject, subject)
        self.assertEqual(result.verb_phrase, verb_phrase)
        self.assertEqual(result.sentence_type, SentenceType.DECLARATIVE)
        self.assertEqual(result.voice, Voice.ACTIVE)
        self.assertEqual(result.tense, Tense.PAST)

    def test_parse_result_to_dict(self):
        """Test ParseResult to_dict method."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]
        result = ParseResult(tokens=tokens)
        result.sentence_type = SentenceType.DECLARATIVE
        result.voice = Voice.ACTIVE
        result.tense = Tense.PAST

        result_dict = result.to_dict()
        self.assertIn("tokens", result_dict)
        self.assertIn("sentence_type", result_dict)
        self.assertIn("voice", result_dict)
        self.assertIn("tense", result_dict)
        self.assertIn("flags", result_dict)
        self.assertIn("warnings", result_dict)
        self.assertIn("errors", result_dict)

    def test_flag_creation(self):
        """Test Flag creation."""
        span = Span(start=0, end=10)
        flag = Flag(rule=RuleID.RULE_4, message="Test flag message", span=span)
        self.assertEqual(flag.rule, RuleID.RULE_4)
        self.assertEqual(flag.message, "Test flag message")
        self.assertEqual(flag.span, span)

    def test_flag_without_span(self):
        """Test Flag creation without span."""
        flag = Flag(rule=RuleID.RULE_4, message="Test flag message", span=None)
        self.assertEqual(flag.rule, RuleID.RULE_4)
        self.assertEqual(flag.message, "Test flag message")
        self.assertIsNone(flag.span)

    def test_flag_to_dict(self):
        """Test Flag to_dict method."""
        span = Span(start=0, end=10)
        flag = Flag(rule=RuleID.RULE_4, message="Test flag message", span=span)
        flag_dict = flag.to_dict()
        self.assertEqual(flag_dict["rule"], "RULE_4")
        self.assertEqual(flag_dict["message"], "Test flag message")
        self.assertIn("span", flag_dict)

    def test_span_creation(self):
        """Test Span creation."""
        span = Span(start=0, end=10)
        self.assertEqual(span.start, 0)
        self.assertEqual(span.end, 10)

    def test_span_to_dict(self):
        """Test Span to_dict method."""
        span = Span(start=0, end=10)
        span_dict = span.to_dict()
        self.assertEqual(span_dict["start"], 0)
        self.assertEqual(span_dict["end"], 10)

    def test_parse_result_json_serialization(self):
        """Test ParseResult JSON serialization."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]
        result = ParseResult(tokens=tokens)
        result.sentence_type = SentenceType.DECLARATIVE
        result.voice = Voice.ACTIVE
        result.tense = Tense.PAST

        # Add a flag
        span = Span(start=0, end=10)
        flag = Flag(rule=RuleID.RULE_4, message="Test flag message", span=span)
        result.flags = [flag]

        # Test JSON serialization
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        parsed_dict = json.loads(json_str)
        self.assertIn("tokens", parsed_dict)
        self.assertIn("flags", parsed_dict)

    def test_parse_result_with_all_fields(self):
        """Test ParseResult with all possible fields."""
        tokens = [
            Token(text="The", lemma="the", pos=PartOfSpeech.ARTICLE, start=0, end=3),
            Token(text="cat", lemma="cat", pos=PartOfSpeech.NOUN, start=4, end=7),
            Token(text="sat", lemma="sat", pos=PartOfSpeech.VERB, start=8, end=11),
            Token(text=".", lemma=".", pos=PartOfSpeech.PUNCTUATION, start=11, end=12),
        ]

        subject_tokens = [tokens[0], tokens[1]]
        subject = Phrase(tokens=subject_tokens, phrase_type="NP", head_index=1)

        verb_tokens = [tokens[2]]
        verb_phrase = Phrase(tokens=verb_tokens, phrase_type="VP", head_index=0)

        result = ParseResult(tokens=tokens)
        result.subject = subject
        result.verb_phrase = verb_phrase
        result.sentence_type = SentenceType.DECLARATIVE
        result.voice = Voice.ACTIVE
        result.tense = Tense.PAST

        # Add flags, warnings, errors, notes
        span = Span(start=0, end=10)
        flag = Flag(rule=RuleID.RULE_4, message="Test flag", span=span)
        result.flags = [flag]
        result.warnings = ["Test warning"]
        result.errors = ["Test error"]
        result.notes = ["Test note"]
        result.rule_checks = {"rule_1": True, "rule_2": False}

        # Test serialization
        result_dict = result.to_dict()
        self.assertIn("subject", result_dict)
        self.assertIn("verb_phrase", result_dict)
        self.assertIn("sentence_type", result_dict)
        self.assertIn("voice", result_dict)
        self.assertIn("tense", result_dict)
        self.assertIn("flags", result_dict)
        self.assertIn("warnings", result_dict)
        self.assertIn("errors", result_dict)
        self.assertIn("notes", result_dict)
        self.assertIn("rule_checks", result_dict)

    def test_models_import(self):
        """Test that models module can be imported."""
        try:
            from kirkham.models import (
                Flag,
                ParserConfig,
                ParseResult,
                Phrase,
                Span,
                Token,
            )

            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import models module: {e}")

    def test_models_classes_exist(self):
        """Test that model classes exist and are instantiable."""
        # Test ParserConfig
        config = ParserConfig()
        self.assertIsNotNone(config)

        # Test Token
        token = Token(text="test", lemma="test", pos=PartOfSpeech.NOUN, start=0, end=4)
        self.assertIsNotNone(token)

        # Test Phrase
        phrase = Phrase(tokens=[token], phrase_type="NP", head_index=0)
        self.assertIsNotNone(phrase)

        # Test ParseResult
        result = ParseResult(tokens=[token])
        self.assertIsNotNone(result)

        # Test Flag
        span = Span(start=0, end=4)
        flag = Flag(rule=RuleID.RULE_1, message="Test", span=span)
        self.assertIsNotNone(flag)

        # Test Span
        self.assertIsNotNone(span)

    def test_parser_config_equality(self):
        """Test ParserConfig equality."""
        config1 = ParserConfig()
        config2 = ParserConfig()
        self.assertEqual(config1, config2)

        config3 = ParserConfig(enforce_rule_1_strict=False)
        self.assertNotEqual(config1, config3)

    def test_token_equality(self):
        """Test Token equality."""
        token1 = Token(text="test", lemma="test", pos=PartOfSpeech.NOUN, start=0, end=4)
        token2 = Token(text="test", lemma="test", pos=PartOfSpeech.NOUN, start=0, end=4)
        self.assertEqual(token1, token2)

        token3 = Token(text="test", lemma="test", pos=PartOfSpeech.VERB, start=0, end=4)
        self.assertNotEqual(token1, token3)

    def test_phrase_equality(self):
        """Test Phrase equality."""
        token = Token(text="test", lemma="test", pos=PartOfSpeech.NOUN, start=0, end=4)
        phrase1 = Phrase(tokens=[token], phrase_type="NP", head_index=0)
        phrase2 = Phrase(tokens=[token], phrase_type="NP", head_index=0)
        self.assertEqual(phrase1, phrase2)

        phrase3 = Phrase(tokens=[token], phrase_type="VP", head_index=0)
        self.assertNotEqual(phrase1, phrase3)

    def test_span_equality(self):
        """Test Span equality."""
        span1 = Span(start=0, end=4)
        span2 = Span(start=0, end=4)
        self.assertEqual(span1, span2)

        span3 = Span(start=0, end=5)
        self.assertNotEqual(span1, span3)

    def test_flag_equality(self):
        """Test Flag equality."""
        span = Span(start=0, end=4)
        flag1 = Flag(rule=RuleID.RULE_1, message="Test", span=span)
        flag2 = Flag(rule=RuleID.RULE_1, message="Test", span=span)
        self.assertEqual(flag1, flag2)

        flag3 = Flag(rule=RuleID.RULE_2, message="Test", span=span)
        self.assertNotEqual(flag1, flag3)

    def test_parse_result_equality(self):
        """Test ParseResult equality."""
        token = Token(text="test", lemma="test", pos=PartOfSpeech.NOUN, start=0, end=4)
        result1 = ParseResult(tokens=[token])
        result2 = ParseResult(tokens=[token])
        self.assertEqual(result1, result2)

        token2 = Token(
            text="test2", lemma="test2", pos=PartOfSpeech.NOUN, start=0, end=5
        )
        result3 = ParseResult(tokens=[token2])
        self.assertNotEqual(result1, result3)


if __name__ == "__main__":
    unittest.main()
