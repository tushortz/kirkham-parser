"""Simple unit tests for the GrammarRuleValidator module."""

import unittest

from kirkham.models import ParserConfig, ParseResult, Token
from kirkham.types import Case, Number, PartOfSpeech, Person, RuleID
from kirkham.validator import GrammarRuleValidator


class TestGrammarRuleValidatorSimple(unittest.TestCase):
    """Simple test suite for GrammarRuleValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ParserConfig()
        self.validator = GrammarRuleValidator(self.config)

    def create_token(self, text, pos, start=0, end=None, **kwargs):
        """Helper to create tokens for testing."""
        if end is None:
            end = start + len(text)
        return Token(
            text=text, lemma=text.lower(), pos=pos, start=start, end=end, **kwargs
        )

    def create_parse_result(self, tokens):
        """Helper to create parse results for testing."""
        return ParseResult(tokens=tokens)

    def test_validator_creation(self):
        """Test that validator can be created."""
        self.assertIsNotNone(self.validator)
        self.assertIsNotNone(self.validator.config)

    def test_rule_1_article_noun_agreement(self):
        """Test RULE 1: Article-noun agreement."""
        # Valid: a + singular noun
        tokens = [
            self.create_token("a", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN, number=Number.SINGULAR),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_1(result)
        self.assertTrue(result.rule_checks.get(RuleID.RULE_1.value, False))

    def test_rule_2_article_noun_relationship(self):
        """Test RULE 2: Article-noun relationship."""
        # Valid: the + noun
        tokens = [
            self.create_token("the", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_2(result)
        self.assertTrue(result.rule_checks.get(RuleID.RULE_2.value, False))

    def test_rule_12_possessive_governance(self):
        """Test RULE 12: Possessive governance."""
        # Valid: possessive + noun
        tokens = [
            self.create_token("my", PartOfSpeech.PRONOUN, case=Case.POSSESSIVE),
            self.create_token("cat", PartOfSpeech.NOUN),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_12(result)
        self.assertTrue(result.rule_checks.get("rule_12_possessive_governed", False))

    def test_rule_18_adjective_qualification(self):
        """Test RULE 18: Adjective qualification."""
        # Valid: adjective + noun (attributive)
        tokens = [
            self.create_token("good", PartOfSpeech.ADJECTIVE),
            self.create_token("book", PartOfSpeech.NOUN),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_18(result)
        self.assertTrue(len(result.flags) == 0)

    def test_rule_30_preposition_placement(self):
        """Test RULE 30: Preposition placement."""
        # Valid: preposition + noun
        tokens = [
            self.create_token("in", PartOfSpeech.PREPOSITION),
            self.create_token("the", PartOfSpeech.ARTICLE),
            self.create_token("house", PartOfSpeech.NOUN),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_30(result)
        self.assertTrue(result.rule_checks.get(RuleID.RULE_30.value, False))

    def test_rule_31_preposition_object_case(self):
        """Test RULE 31: Preposition object case."""
        # Valid: preposition + noun/pronoun
        tokens = [
            self.create_token("with", PartOfSpeech.PREPOSITION),
            self.create_token("me", PartOfSpeech.PRONOUN, case=Case.OBJECTIVE),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_31(result)
        self.assertTrue(len(result.flags) == 0)

    def test_agreement_checking(self):
        """Test subject-verb agreement checking."""
        # Test "be" verb agreement
        subject = self.create_token(
            "I", PartOfSpeech.PRONOUN, person=Person.FIRST, number=Number.SINGULAR
        )
        verb = self.create_token("am", PartOfSpeech.VERB)
        self.assertTrue(self.validator._check_agreement(subject, verb))

        subject = self.create_token(
            "he", PartOfSpeech.PRONOUN, person=Person.THIRD, number=Number.SINGULAR
        )
        verb = self.create_token("is", PartOfSpeech.VERB)
        self.assertTrue(self.validator._check_agreement(subject, verb))

    def test_pronoun_case_extraction(self):
        """Test pronoun case extraction."""
        token = self.create_token("I", PartOfSpeech.PRONOUN, case=Case.NOMINATIVE)
        case = self.validator._pron_case(token)
        self.assertEqual(case, Case.NOMINATIVE)

        token = self.create_token("me", PartOfSpeech.PRONOUN, case=Case.OBJECTIVE)
        case = self.validator._pron_case(token)
        self.assertEqual(case, Case.OBJECTIVE)

    def test_config_dependent_rules(self):
        """Test that rules respect configuration settings."""
        # Test with rule disabled
        config = ParserConfig(enforce_rule_1_strict=False)
        validator = GrammarRuleValidator(config)

        tokens = [
            self.create_token("a", PartOfSpeech.ARTICLE),
            self.create_token("cats", PartOfSpeech.NOUN, number=Number.PLURAL),
        ]
        result = self.create_parse_result(tokens)
        validator.validate(result)

        # Should not have RULE_1 flags when disabled
        rule_1_flags = [f for f in result.flags if f.rule == RuleID.RULE_1]
        self.assertEqual(len(rule_1_flags), 0)

    def test_extended_validation(self):
        """Test extended validation features."""
        config = ParserConfig(enable_extended_validation=True)
        validator = GrammarRuleValidator(config)

        tokens = [self.create_token("good", PartOfSpeech.ADJECTIVE)]
        result = self.create_parse_result(tokens)
        validator.validate(result)

        # Should have RULE_18 flags when extended validation is enabled
        rule_18_flags = [f for f in result.flags if f.rule == RuleID.RULE_18]
        self.assertTrue(len(rule_18_flags) > 0)

    def test_comparative_constructions(self):
        """Test comparative constructions in RULE_2."""
        # Test "the more...the better" pattern
        tokens = [
            self.create_token("the", PartOfSpeech.ARTICLE),
            self.create_token("more", PartOfSpeech.ADVERB),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_2(result)
        self.assertTrue(result.rule_checks.get(RuleID.RULE_2.value, False))

        tokens = [
            self.create_token("the", PartOfSpeech.ARTICLE),
            self.create_token("better", PartOfSpeech.ADJECTIVE),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_2(result)
        self.assertTrue(result.rule_checks.get(RuleID.RULE_2.value, False))

    def test_infinitive_constructions(self):
        """Test infinitive constructions in RULE_30/31."""
        # Test "to + verb" should not be flagged
        tokens = [
            self.create_token("to", PartOfSpeech.PREPOSITION),
            self.create_token("give", PartOfSpeech.VERB),
        ]
        result = self.create_parse_result(tokens)
        self.validator._check_rule_30(result)
        self.validator._check_rule_31(result)

        # Should not have flags for infinitive constructions
        to_flags = [f for f in result.flags if "to" in f.message]
        self.assertEqual(len(to_flags), 0)

    def test_validate_all_rules(self):
        """Test the main validate method calls all rules."""
        tokens = [
            self.create_token("The", PartOfSpeech.ARTICLE),
            self.create_token("cat", PartOfSpeech.NOUN),
            self.create_token("sat", PartOfSpeech.VERB),
            self.create_token(".", PartOfSpeech.PUNCTUATION),
        ]
        result = self.create_parse_result(tokens)
        self.validator.validate(result)

        # Should have rule checks
        self.assertTrue(len(result.rule_checks) > 0)

        # Should have boolean values
        for rule_id, check_result in result.rule_checks.items():
            self.assertIsInstance(check_result, bool)

    def test_edge_cases(self):
        """Test edge cases in validation."""
        # Empty tokens
        result = self.create_parse_result([])
        self.validator.validate(result)
        self.assertIsNotNone(result)

        # Single token
        tokens = [self.create_token("hello", PartOfSpeech.NOUN)]
        result = self.create_parse_result(tokens)
        self.validator.validate(result)
        self.assertIsNotNone(result)

    def test_validator_import(self):
        """Test that validator module can be imported."""
        try:
            from kirkham.validator import GrammarRuleValidator

            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import validator module: {e}")

    def test_validator_methods_exist(self):
        """Test that validator methods exist."""
        # Check that methods are callable
        self.assertTrue(callable(self.validator.validate))
        self.assertTrue(callable(self.validator._check_rule_1))
        self.assertTrue(callable(self.validator._check_rule_2))
        self.assertTrue(callable(self.validator._check_rule_12))
        self.assertTrue(callable(self.validator._check_rule_18))
        self.assertTrue(callable(self.validator._check_rule_30))
        self.assertTrue(callable(self.validator._check_rule_31))


if __name__ == "__main__":
    unittest.main()
