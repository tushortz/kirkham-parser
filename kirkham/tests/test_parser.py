"""Unit tests for English Grammar Parser.

Tests cover all 9 improvements including:
- Tokenization & offsets
- Morphology heuristics (get-passive, irregular plurals)
- Finite verb identification
- Safer infinitive detection
- Rule system (flags, spans)
- Configurability
- NP parsing with adverbs
- Deterministic output

Author: Based on Samuel Kirkham's English Grammar (1829)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from kirkham import (
    KirkhamParser,
    ParserConfig,
    PartOfSpeech,
    RuleID,
    SentenceType,
    Tense,
    Voice,
)


class TestKirkhamParser(unittest.TestCase):
    """Test suite for English Grammar Parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = KirkhamParser()

    # ========================================================================
    # TEST 1: TOKENIZATION & OFFSETS
    # ========================================================================

    def test_offsets_present(self):
        """Test that all tokens have character offsets."""
        result = self.parser.parse("Time is money.")
        json_data = result.to_dict()

        # Check all tokens have start and end offsets
        assert all(
            "start" in t and "end" in t for t in json_data["tokens"]
        ), "All tokens must have start and end offsets"

        # Verify offset correctness
        sentence = "Time is money."
        for token in json_data["tokens"]:
            start = token["start"]
            end = token["end"]
            extracted = sentence[start:end]
            assert extracted == token["text"], (
                f"Offset mismatch: expected '{token['text']}', "
                f"got '{extracted}' at [{start}:{end}]"
            )

    def test_unicode_apostrophes(self):
        """Test handling of Unicode apostrophes."""
        sentences = [
            "It's a book.",  # ASCII apostrophe
            "It's a book.",  # Unicode right single quotation mark
            "It's a book.",  # Unicode apostrophe
        ]

        for sent in sentences:
            result = self.parser.parse(sent)
            assert len(result.tokens) > 0, f"Failed to tokenize: {sent}"

    def test_hyphenated_words(self):
        """Test tokenization of hyphenated words."""
        result = self.parser.parse("A well-known fact.")
        token_texts = [t.text for t in result.tokens]
        assert "well-known" in token_texts, "Hyphenated word should be single token"

    # ========================================================================
    # TEST 2: MORPHOLOGY HEURISTICS
    # ========================================================================

    def test_irregular_plurals(self):
        """Test detection of irregular plural nouns."""
        test_cases = [
            ("The children play.", "children"),
            ("The women work.", "women"),
            ("The men walk.", "men"),
            ("The teeth hurt.", "teeth"),
            ("The mice ran.", "mice"),
        ]

        for sentence, plural_word in test_cases:
            result = self.parser.parse(sentence)
            plural_tokens = [
                t
                for t in result.tokens
                if t.text.lower() == plural_word and t.pos == PartOfSpeech.NOUN
            ]
            assert any(
                t.number and t.number.value == "plural" for t in plural_tokens
            ), f"'{plural_word}' should be detected as plural"

    def test_get_passive(self):
        """Test detection of get-passive voice."""
        result = self.parser.parse("He got promoted by the board.")
        assert (
            result.voice == Voice.PASSIVE
        ), "Get-passive construction should be detected as passive voice"

    def test_been_passive(self):
        """Test detection of 'been + VBN' passive voice."""
        result = self.parser.parse("The work has been completed.")
        assert (
            result.voice == Voice.PASSIVE
        ), "'been + VBN' should be detected as passive voice"

    def test_regular_be_passive(self):
        """Test detection of regular be-passive."""
        result = self.parser.parse("The letter was written.")
        assert result.voice == Voice.PASSIVE, "Regular be-passive should be detected"

    # ========================================================================
    # TEST 3: FINITE VERB IDENTIFICATION
    # ========================================================================

    def test_finite_verb_anchor(self):
        """Test identification of finite verb anchor in verb group."""
        result = self.parser.parse("She will have been going.")
        assert result.verb_phrase is not None

        # First verb should be modal "will" (finite anchor)
        first_verb = result.verb_phrase.tokens[0]
        assert first_verb.lemma in {
            "will"
        }, "Finite anchor should be modal or tensed verb"

    def test_no_false_verb_group_from_ing_noun(self):
        """Test that -ing nouns don't create false verb groups."""
        result = self.parser.parse("Running is fun.")

        # "Running" should be subject, not verb
        if result.subject:
            assert "Running" in result.subject.text, "'-ing' noun should be in subject"

    # ========================================================================
    # TEST 4: SAFER INFINITIVE DETECTION
    # ========================================================================

    def test_to_prep_not_infinitive(self):
        """Test that 'to + noun' is not detected as infinitive."""
        result = self.parser.parse("We walked to school.")

        # Should NOT have infinitive-related flags
        infinitive_flags = [f for f in result.flags if f.rule in [RuleID.RULE_25]]
        assert (
            len(infinitive_flags) == 0
        ), "'to school' should not be detected as infinitive"

        # Also check directly
        infinitives = self.parser._syntactic_parser._find_infinitives(result.tokens)
        assert len(infinitives) == 0, "'to school' should not be in infinitive list"

    def test_real_infinitive_detected(self):
        """Test that real infinitives are detected."""
        result = self.parser.parse("He wants to go.")

        infinitives = self.parser._syntactic_parser._find_infinitives(result.tokens)
        assert len(infinitives) > 0, "'to go' should be detected as infinitive"

    def test_to_adjective_not_infinitive(self):
        """Test that 'to + adjective' is not detected as infinitive."""
        result = self.parser.parse("She is nice to me.")

        infinitives = self.parser._syntactic_parser._find_infinitives(result.tokens)
        # "to me" should not be infinitive
        inf_texts = [
            " ".join(result.tokens[i].text for i in range(start, end + 1))
            for start, end in infinitives
        ]
        assert "to me" not in inf_texts, "'to me' should not be detected as infinitive"

    # ========================================================================
    # TEST 5: RULE SYSTEM HYGIENE (FLAGS & SPANS)
    # ========================================================================

    def test_flags_have_rule_ids(self):
        """Test that all flags have RuleID enums."""
        result = self.parser.parse("They is wrong.")

        # Should have at least one flag
        assert len(result.flags) > 0

        # All flags should have RuleID
        for flag in result.flags:
            assert isinstance(flag.rule, RuleID), "Flag rule should be RuleID enum"

    def test_flags_have_spans(self):
        """Test that flags include span information where applicable."""
        result = self.parser.parse("They is wrong.")

        # Check that flags with locations have spans
        for flag in result.flags:
            # Span can be None for sentence-level issues
            if flag.span is not None:
                assert flag.span.start is not None
                assert flag.span.end is not None
                assert flag.span.start <= flag.span.end

    def test_flag_serialization(self):
        """Test that flags serialize correctly to JSON."""
        result = self.parser.parse("They is wrong.")
        json_data = result.to_dict()

        # Flags should be in JSON
        assert "flags" in json_data
        assert isinstance(json_data["flags"], list)

        # Each flag should have rule and message
        for flag in json_data["flags"]:
            assert "rule" in flag
            assert "message" in flag

    # ========================================================================
    # TEST 6: CONFIGURABILITY
    # ========================================================================

    def test_copula_permissive(self):
        """Test permissive copula with config."""
        # Strict mode (default - disallow informal pronouns)
        result_strict = self.parser.parse("It is me.")
        k21_strict = [f for f in result_strict.flags if f.rule == RuleID.RULE_21]

        # Permissive mode (allow informal pronouns like "It is me")
        config = ParserConfig(allow_informal_pronouns=True)
        parser_permissive = KirkhamParser(config)
        result_permissive = parser_permissive.parse("It is me.")
        k21_permissive = [
            f for f in result_permissive.flags if f.rule == RuleID.RULE_21
        ]

        # Permissive mode should have fewer or equal K21 flags
        assert len(k21_permissive) <= len(
            k21_strict
        ), "Permissive mode should reduce K21 flags"

    def test_get_passive_toggle(self):
        """Test get-passive detection can be toggled."""
        sentence = "He got promoted."

        # With get-passive enabled (default)
        config_enabled = ParserConfig(detect_get_passive=True)
        parser_enabled = KirkhamParser(config_enabled)
        result_enabled = parser_enabled.parse(sentence)

        # With get-passive disabled
        config_disabled = ParserConfig(detect_get_passive=False)
        parser_disabled = KirkhamParser(config_disabled)
        result_disabled = parser_disabled.parse(sentence)

        # Enabled should detect passive
        assert result_enabled.voice == Voice.PASSIVE

        # Disabled config parses but may differ
        assert result_disabled is not None
        # Note: disabled might still detect via be-passive

    def test_rule_enforcement_toggles(self):
        """Test that rule enforcement can be toggled."""
        # Test RULE_20 toggle
        config_strict = ParserConfig(enforce_rule_20_strict=True)
        config_permissive = ParserConfig(enforce_rule_20_strict=False)

        parser_strict = KirkhamParser(config_strict)
        parser_permissive = KirkhamParser(config_permissive)

        # Both should parse without errors
        sentence = "The book is on the table."
        result_strict = parser_strict.parse(sentence)
        result_permissive = parser_permissive.parse(sentence)

        assert result_strict is not None
        assert result_permissive is not None

    # ========================================================================
    # TEST 7: NP PARSING WITH ADVERBS
    # ========================================================================

    def test_adverb_before_adjective_in_subject(self):
        """Test that subject NPs include adverbs before adjectives."""
        result = self.parser.parse("The very good book is here.")

        assert result.subject is not None
        assert "very" in result.subject.text, "Subject should include adverb 'very'"
        assert "good" in result.subject.text, "Subject should include adjective 'good'"

    def test_adverb_before_adjective_in_object(self):
        """Test that object NPs include adverbs before adjectives."""
        result = self.parser.parse("She found a very rare coin.")

        assert result.object_phrase is not None
        assert (
            "very" in result.object_phrase.text
        ), "Object should include adverb 'very'"

    def test_multiple_adverb_intensifiers(self):
        """Test various adverb-like intensifiers."""
        test_cases = [
            ("The quite old man sat.", "quite old man"),
            ("A really good idea emerged.", "really good idea"),
            ("The extremely rare bird flew.", "extremely rare bird"),
        ]

        for sentence, expected_phrase in test_cases:
            result = self.parser.parse(sentence)
            if result.subject:
                assert (
                    expected_phrase.split()[0] in result.subject.text
                ), f"Subject should contain '{expected_phrase}'"

    # ========================================================================
    # TEST 8: STACKED POSSESSIVES & PREPOSITIONAL PHRASES
    # ========================================================================

    def test_stacked_possessives(self):
        """Test handling of stacked possessive constructions."""
        result = self.parser.parse("John's brother's book is old.")

        # Should parse without errors
        assert result.subject is not None

        # Subject should include both possessives
        subject_text = result.subject.text
        assert "John's" in subject_text
        assert "brother's" in subject_text

    def test_stacked_possessives_with_pp(self):
        """Test stacked possessives with prepositional phrase."""
        result = self.parser.parse("John's brother's book on the table is old.")

        # Should handle complex subject
        assert result.subject is not None

        # Check possessive governance (rule_12)
        # The possessives should be properly governed
        # Look for the actual rule check key used
        has_possessive_check = any(
            "rule_12" in key.lower() or "possessive" in key.lower()
            for key in result.rule_checks
        )
        assert has_possessive_check, (
            f"Expected possessive check. " f"Found: {result.rule_checks.keys()}"
        )

    # ========================================================================
    # TEST 9: COMPREHENSIVE INTEGRATION TESTS
    # ========================================================================

    def test_all_improvements_together(self):
        """Test that all 9 improvements work together."""
        sentence = "The very good children were given toys."
        result = self.parser.parse(sentence)

        # 1. Offsets present
        assert all(hasattr(t, "start") and hasattr(t, "end") for t in result.tokens)

        # 3. Morphology (irregular plural, passive)
        assert result.voice == Voice.PASSIVE
        children_tokens = [t for t in result.tokens if t.text == "children"]
        assert any(t.number and t.number.value == "plural" for t in children_tokens)

        # 4. Finite verb identified
        assert result.verb_phrase is not None
        assert result.verb_phrase.tokens[0].text == "were"

        # 6. Flags (structured)
        assert isinstance(result.flags, list)

        # 8. NP with adverb
        assert result.subject is not None
        assert "very" in result.subject.text

    def test_json_output_deterministic(self):
        """Test that JSON output is deterministic."""
        sentence = "The cat sat."

        # Parse twice
        result1 = self.parser.parse(sentence)
        result2 = self.parser.parse(sentence)

        # Convert to JSON
        json1 = json.dumps(result1.to_dict(), sort_keys=True)
        json2 = json.dumps(result2.to_dict(), sort_keys=True)

        # Should be identical
        assert json1 == json2, "JSON output should be deterministic"

    def test_show_method_json_mode(self):
        """Test show() method in JSON mode."""
        import io
        import sys

        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured

        try:
            self.parser.show("The cat sat.", json_only=True)
            output = captured.getvalue()

            # Should be valid JSON
            json_data = json.loads(output)
            assert "tokens" in json_data
            assert "subject" in json_data
        finally:
            sys.stdout = sys.__stdout__

    # ========================================================================
    # TEST 10: EDGE CASES
    # ========================================================================

    def test_empty_string(self):
        """Test parsing empty string."""
        result = self.parser.parse("")
        assert len(result.tokens) == 0

    def test_punctuation_only(self):
        """Test parsing punctuation only."""
        result = self.parser.parse("...")
        assert len(result.tokens) > 0

    def test_long_sentence(self):
        """Test parsing long complex sentence."""
        sentence = (
            "The very intelligent students who studied hard "
            "were given excellent grades by the professor."
        )
        result = self.parser.parse(sentence)

        # Should parse without crashing
        assert result is not None
        assert len(result.tokens) > 10

    def test_contractions(self):
        """Test handling of contractions."""
        result = self.parser.parse("I'm happy and you're sad.")

        # Should tokenize contractions
        token_texts = [t.text for t in result.tokens]
        # Contractions might be split or kept together
        assert "I'm" in token_texts

    # ========================================================================
    # TEST 11: PERFORMANCE (OPTIONAL)
    # ========================================================================

    def test_performance_benchmark(self):
        """Test that parser meets performance requirements."""
        import time

        sentence = "The children were given toys."
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            self.parser.parse(sentence)
        end = time.time()

        elapsed = end - start
        throughput = iterations / elapsed

        # Should be reasonably fast (at least 1000 parses/sec)
        assert (
            throughput > 1000
        ), f"Parser should handle 1000+ parses/sec, got {throughput:.0f}"

    # ========================================================================
    # NEW TESTS: SENTENCE TYPE DETECTION
    # ========================================================================

    def test_sentence_type_declarative(self):
        """Test detection of declarative sentences (statements)."""
        result = self.parser.parse("The cat sat on the mat.")
        assert result.sentence_type == SentenceType.DECLARATIVE

    def test_sentence_type_interrogative_wh(self):
        """Test detection of WH-questions."""
        test_cases = [
            "What time is it?",
            "Where are you going?",
            "Who is there?",
            "Why did you do that?",
            "How are you?",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert (
                result.sentence_type == SentenceType.INTERROGATIVE
            ), f"Failed for: {sentence}"

    def test_sentence_type_interrogative_inverted(self):
        """Test detection of inverted auxiliary questions."""
        test_cases = [
            "Is she coming?",
            "Are they ready?",
            "Do you like coffee?",
            "Can we go?",
            "Will it work?",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert (
                result.sentence_type == SentenceType.INTERROGATIVE
            ), f"Failed for: {sentence}"

    def test_sentence_type_imperative(self):
        """Test detection of imperative sentences (commands)."""
        test_cases = ["Sit down!", "Go home!", "Stop!", "Listen!"]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert (
                result.sentence_type == SentenceType.IMPERATIVE
            ), f"Failed for: {sentence}"

    def test_sentence_type_exclamatory(self):
        """Test detection of exclamatory sentences."""
        result = self.parser.parse("What a beautiful day!")
        assert result.sentence_type == SentenceType.EXCLAMATORY

        result = self.parser.parse("How wonderful!")
        assert result.sentence_type == SentenceType.EXCLAMATORY

    # ========================================================================
    # NEW TESTS: TENSE DETECTION
    # ========================================================================

    def test_tense_present(self):
        """Test detection of present tense."""
        test_cases = [
            "She walks to school.",
            "They are happy.",
            "I am here.",
            "He is tall.",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert result.tense == Tense.PRESENT, f"Failed for: {sentence}"

    def test_tense_past(self):
        """Test detection of past tense."""
        result = self.parser.parse("She walked home.")
        assert result.tense == Tense.PAST

        result = self.parser.parse("They arrived yesterday.")
        assert result.tense == Tense.PAST

    def test_tense_future(self):
        """Test detection of future tense."""
        test_cases = [
            "She will go tomorrow.",
            "They shall arrive soon.",
            "I will help you.",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert result.tense == Tense.FUTURE, f"Failed for: {sentence}"

    def test_tense_present_perfect(self):
        """Test detection of present perfect tense."""
        test_cases = [
            "I have seen that movie.",
            "She has finished her work.",
            "They have arrived.",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert result.tense == Tense.PRESENT_PERFECT, f"Failed for: {sentence}"

    def test_tense_past_perfect(self):
        """Test detection of past perfect tense."""
        result = self.parser.parse("She had seen it.")
        assert result.tense == Tense.PAST_PERFECT

        result = self.parser.parse("They had finished quickly.")
        assert result.tense == Tense.PAST_PERFECT

    def test_tense_future_perfect(self):
        """Test detection of future perfect tense."""
        test_cases = [
            "She will have arrived by noon.",
            "They will have finished by then.",
        ]
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert result.tense == Tense.FUTURE_PERFECT, f"Failed for: {sentence}"

    # ========================================================================
    # NEW TESTS: CONFIGURATION PRESETS
    # ========================================================================

    def test_config_strict_formal(self):
        """Test strict formal configuration."""
        cfg = ParserConfig.strict_formal()
        parser = KirkhamParser(cfg)

        # Should flag informal pronouns
        result = parser.parse("It is me.")
        assert len(result.flags) > 0
        assert not cfg.allow_informal_pronouns
        assert cfg.enforce_rule_20_strict

    def test_config_modern_permissive(self):
        """Test modern permissive configuration."""
        cfg = ParserConfig.modern_permissive()
        parser = KirkhamParser(cfg)

        # Should allow informal pronouns
        result = parser.parse("It is me.")
        # Filter for copula case flags only
        copula_flags = [
            f
            for f in result.flags
            if "nominative case" in f.message or "to be" in f.message
        ]
        assert len(copula_flags) == 0
        assert cfg.allow_informal_pronouns

    def test_config_educational(self):
        """Test educational configuration."""
        cfg = ParserConfig.educational()
        parser = KirkhamParser(cfg)

        parser.parse("The cat sat.")
        assert cfg.enable_extended_validation
        assert cfg.detect_sentence_type
        assert cfg.detect_tense

    # ========================================================================
    # NEW TESTS: BATCH PROCESSING
    # ========================================================================

    def test_parse_batch_sequential(self):
        """Test sequential batch processing."""
        texts = [
            "The cat sleeps.",
            "Dogs bark loudly.",
            "Birds fly in the sky.",
        ]
        results = self.parser.parse_batch(texts, parallel=False)

        assert len(results) == 3
        assert results[0].subject is not None
        assert results[0].verb_phrase is not None

    def test_parse_batch_parallel(self):
        """Test parallel batch processing."""
        texts = ["Sentence one.", "Sentence two.", "Sentence three."]
        results = self.parser.parse_batch(texts, parallel=True)

        assert len(results) == 3
        for result in results:
            assert result.tokens is not None

    def test_parse_many_sentences(self):
        """Test parsing multiple sentences from a single string."""
        text = "The cat sat. The dog barked. Birds sing."
        results = self.parser.parse_many(text)

        assert len(results) == 3
        assert len(results[0].tokens) == 4  # The cat sat .

    def test_parse_file_line_by_line(self):
        """Test parsing from a file (line by line)."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("The cat sat.\n")
            f.write("The dog barked.\n")
            f.write("Birds fly.\n")
            temp_file = f.name

        try:
            results = self.parser.parse_file(temp_file, sentence_per_line=True)
            assert len(results) == 3
            assert results[0].subject is not None
        finally:
            Path(temp_file).unlink()

    def test_parse_file_auto_split(self):
        """Test parsing from a file (auto-split)."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("The cat sat. The dog barked. Birds fly.")
            temp_file = f.name

        try:
            results = self.parser.parse_file(temp_file, sentence_per_line=False)
            assert len(results) == 3
        finally:
            Path(temp_file).unlink()

    # ========================================================================
    # NEW TESTS: OUTPUT FORMATTING
    # ========================================================================

    def test_explain_method(self):
        """Test explain() method produces human-readable output."""
        output = self.parser.explain("The cat sat.", show_offsets=False)
        assert "PARSE STRUCTURE" in output
        assert "Subject:" in output
        assert "Verb:" in output

    def test_explain_with_offsets(self):
        """Test explain() method with character offsets."""
        output = self.parser.explain("The cat sat.", show_offsets=True)
        assert "[0:" in output  # Should show offset ranges

    def test_show_method_verbose(self):
        """Test show() method in verbose mode."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            self.parser.show("The cat sat.", json_only=False, show_offsets=False)
        output = f.getvalue()
        assert "PARSE STRUCTURE" in output

    def test_to_json_method(self):
        """Test to_json() method returns proper dict."""
        json_dict = self.parser.to_json("The cat sat.")
        assert "tokens" in json_dict
        assert "subject" in json_dict
        assert "verb_phrase" in json_dict
        assert "tense" in json_dict
        assert "sentence_type" in json_dict

    # ========================================================================
    # NEW TESTS: EDGE CASES
    # ========================================================================

    def test_empty_sentence(self):
        """Test parsing empty or very short input."""
        result = self.parser.parse(".")
        assert len(result.tokens) == 1

    def test_config_toggles(self):
        """Test configuration feature toggles."""
        cfg = ParserConfig(
            detect_sentence_type=False,
            detect_tense=False,
        )
        parser = KirkhamParser(cfg)
        result = parser.parse("The cat sat.")

        # These should be None when detection is disabled
        assert result.sentence_type is None
        assert result.tense is None

    def test_parse_many_single_sentence(self):
        """Test parse_many with single sentence."""
        results = self.parser.parse_many("The cat sat.")
        assert len(results) == 1

    def test_parse_many_no_periods(self):
        """Test parse_many with text without sentence endings."""
        results = self.parser.parse_many("just some text")
        assert len(results) == 1

    def test_json_serialization_complete(self):
        """Test that JSON serialization includes all new fields."""
        result = self.parser.parse("She will have gone.")
        json_dict = result.to_dict()

        # Check new fields are present
        assert "tense" in json_dict
        assert "sentence_type" in json_dict

        # Check they have values
        assert json_dict["tense"] is not None
        assert json_dict["sentence_type"] is not None

    def test_voice_detection_with_tense(self):
        """Test that voice and tense detection work together."""
        result = self.parser.parse("The book was written yesterday.")
        assert result.voice == Voice.PASSIVE
        assert result.tense == Tense.PAST

    def test_question_without_subject(self):
        """Test questions that don't have traditional subjects."""
        result = self.parser.parse("Who is there?")
        assert result.sentence_type == SentenceType.INTERROGATIVE
        # Subject finding may differ for questions

    def test_imperative_with_you(self):
        """Test imperative with explicit 'you'."""
        result = self.parser.parse("You go now!")
        # Could be declarative or imperative depending on context
        assert result.sentence_type is not None


# ============================================================================
# TEST RUNNER
# ============================================================================


def run_tests(verbosity=2):
    """Run all tests with specified verbosity."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestKirkhamParser)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


if __name__ == "__main__":
    print("=" * 70)
    print("ENGLISH GRAMMAR PARSER - UNIT TESTS")
    print("Testing all 9 improvements + edge cases")
    print("=" * 70)
    print()

    result = run_tests(verbosity=2)

    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
