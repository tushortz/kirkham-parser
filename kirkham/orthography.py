"""Orthography (Spelling) Rules for the Kirkham Grammar Parser.

This module implements Kirkham's orthography rules I-X for spelling validation.
"""

from __future__ import annotations

from .models import Flag, ParseResult, Span
from .types import RuleID


class OrthographyValidator:
    """Validates spelling according to Kirkham's orthography rules."""

    def __init__(self, config):
        """Initialize the orthography validator."""
        self.config = config

    def validate(self, parse_result: ParseResult) -> None:
        """Validate spelling rules for all tokens."""
        if not self.config.enforce_ortho_rules:
            return

        # Apply orthography rules
        if self.config.enforce_ortho_i:
            self._check_ortho_i(parse_result)
        if self.config.enforce_ortho_ii:
            self._check_ortho_ii(parse_result)
        if self.config.enforce_ortho_iii:
            self._check_ortho_iii(parse_result)
        if self.config.enforce_ortho_iv:
            self._check_ortho_iv(parse_result)
        if self.config.enforce_ortho_v:
            self._check_ortho_v(parse_result)
        if self.config.enforce_ortho_vi:
            self._check_ortho_vi(parse_result)
        if self.config.enforce_ortho_vii:
            self._check_ortho_vii(parse_result)
        if self.config.enforce_ortho_viii:
            self._check_ortho_viii(parse_result)
        if self.config.enforce_ortho_ix:
            self._check_ortho_ix(parse_result)
        if self.config.enforce_ortho_x:
            self._check_ortho_x(parse_result)

    def _check_ortho_i(self, parse_result: ParseResult) -> None:
        """ORTHO I: Monosyllables ending in f, l, or s (single vowel before): double the final consonant.

        Examples: staff, ball, pass (correct)
        Exceptions: if, of, is, as, has, was, this, thus, us, yes, gas, bus
        """
        violations = []

        # Exception words that don't follow the rule
        exceptions = {
            "if",
            "of",
            "is",
            "as",
            "has",
            "was",
            "this",
            "thus",
            "us",
            "yes",
            "gas",
            "bus",
            "plus",
            "minus",
            "focus",
            "campus",
            "status",
        }

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Skip exceptions
                if word in exceptions:
                    continue

                # Check if monosyllable ending in f, l, or s with single vowel before
                if self._is_monosyllable(word) and word.endswith(("f", "l", "s")):
                    # Check if single vowel before final consonant
                    if len(word) >= 3:
                        vowel_before = word[-2]
                        if vowel_before in "aeiou":
                            # Check if final consonant is not doubled
                            if word[-1] != word[-2]:
                                violations.append(token)

        parse_result.rule_checks[RuleID.ORTHO_I.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_I,
                    message=f"Monosyllable '{token.text}' ending in f/l/s should double the final consonant",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_ii(self, parse_result: ParseResult) -> None:
        """ORTHO II: Polysyllables ending in f, l, or s with accent on last syllable: usually double final consonant.

        Examples: control → controlled, refer → referred
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Skip common words that don't follow doubling rules
                common_exceptions = {
                    "years",
                    "students",
                    "studious",
                    "serious",
                    "obvious",
                    "previous",
                    "various",
                    "curious",
                    "glorious",
                    "victorious",
                    "mysterious",
                    "generous",
                    "numerous",
                    "dangerous",
                    "courageous",
                    "outrageous",
                    "advantageous",
                    "disadvantageous",
                    "courteous",
                    "righteous",
                    "spontaneous",
                    "simultaneous",
                    "instantaneous",
                    "contemporaneous",
                    "erroneous",
                    "homogeneous",
                    "heterogeneous",
                    "extraneous",
                    "subterraneous",
                    "superfluous",
                    "tempestuous",
                    "voluptuous",
                    "presumptuous",
                    "sumptuous",
                    "tumultuous",
                    "unctuous",
                    "virtuous",
                    "sensuous",
                    "conspicuous",
                    "perspicuous",
                    "ambiguous",
                    "contiguous",
                    "exiguous",
                    "irreligious",
                    "religious",
                    "sacrilegious",
                    "prodigious",
                    "litigious",
                    "prestigious",
                    "tedious",
                    "odious",
                    "melodious",
                    "commodious",
                    "incommodious",
                    "furious",
                }

                if word in common_exceptions:
                    continue

                # Check if polysyllable ending in f, l, or s
                if not self._is_monosyllable(word) and word.endswith(("f", "l", "s")):
                    # Only flag if it's a verb that might need doubling for past tense/participle
                    if (
                        token.pos.value == "verb"
                        and len(word) >= 4
                        and word[-1] in "fls"
                    ):
                        # Check if final consonant is not doubled
                        if word[-1] != word[-2]:
                            violations.append(token)

        parse_result.rule_checks[RuleID.ORTHO_II.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_II,
                    message=f"Polysyllable '{token.text}' ending in f/l/s may need doubled final consonant",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_iii(self, parse_result: ParseResult) -> None:
        """ORTHO III: Words ending in y after consonant: change y → i before terminations except before -ing.

        Examples: happy → happiness, try → tried, but trying (not triing)
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Check if word ends in y after consonant
                if len(word) >= 3 and word.endswith("y"):
                    consonant_before_y = word[-2]
                    if consonant_before_y not in "aeiou":
                        # Check if word has a termination that should trigger y→i change
                        # This is a simplified check - in practice, we'd need a comprehensive list
                        common_endings = [
                            "ed",
                            "er",
                            "est",
                            "ly",
                            "ness",
                            "ment",
                            "ful",
                        ]
                        for ending in common_endings:
                            if word.endswith(ending) and not word.endswith("ing"):
                                # Check if y was changed to i
                                base_word = word[: -len(ending)]
                                if base_word.endswith("y"):
                                    violations.append(token)
                                break

        parse_result.rule_checks[RuleID.ORTHO_III.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_III,
                    message=f"Word '{token.text}' ending in y after consonant should change y to i before termination",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_iv(self, parse_result: ParseResult) -> None:
        """ORTHO IV: Words ending in y after vowel: retain y.

        Examples: monkey → monkeys, play → played
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Check if word ends in y after vowel
                if len(word) >= 3 and word.endswith("y"):
                    vowel_before_y = word[-2]
                    if vowel_before_y in "aeiou":
                        # Check if y was incorrectly changed to i
                        if word.endswith(("ies", "ied")):
                            violations.append(token)

        parse_result.rule_checks[RuleID.ORTHO_IV.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_IV,
                    message=f"Word '{token.text}' ending in y after vowel should retain y",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_v(self, parse_result: ParseResult) -> None:
        """ORTHO V: With certain suffixes (-able, -ous), final e is often dropped, but retained after c or g.

        Examples: changeable, courageous (e retained), lovable (e dropped)
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Check suffixes that typically drop final e
                dropping_suffixes = ["able", "ous", "ive", "ful", "less"]
                for suffix in dropping_suffixes:
                    if word.endswith(suffix):
                        base_word = word[: -len(suffix)]
                        if len(base_word) >= 2:
                            # Check if final e should be retained after c or g, or dropped otherwise
                            if (
                                base_word.endswith(("c", "g"))
                                and not base_word.endswith("e")
                            ) or (
                                base_word.endswith("e")
                                and not base_word.endswith(("c", "g"))
                            ):
                                violations.append(token)
                        break

        parse_result.rule_checks[RuleID.ORTHO_V.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_V,
                    message=f"Word '{token.text}' with suffix may need final e adjustment",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_vi(self, parse_result: ParseResult) -> None:
        """ORTHO VI: Final silent e is generally dropped before vowel-initial suffix.

        Examples: love → loving, hope → hoping
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Check vowel-initial suffixes
                vowel_suffixes = ["ing", "ed", "er", "est", "able", "ous", "ive"]
                for suffix in vowel_suffixes:
                    if word.endswith(suffix):
                        base_word = word[: -len(suffix)]
                        if len(base_word) >= 2 and base_word.endswith("e"):
                            # Check if silent e was not dropped
                            if base_word.endswith("e"):
                                violations.append(token)
                        break

        parse_result.rule_checks[RuleID.ORTHO_VI.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_VI,
                    message=f"Word '{token.text}' should drop final silent e before vowel-initial suffix",
                    span=Span(token.start, token.end),
                )
            )

    def _check_ortho_vii(self, parse_result: ParseResult) -> None:
        """ORTHO VII: Additional derivative/spelling cases."""
        # This would contain specific spelling rules for derivatives
        # For now, we'll implement a basic check for common patterns
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Check for common spelling patterns
                if word.endswith("ie") and not word.endswith("cie"):
                    # Words ending in -ie often follow specific patterns
                    pass  # Could add specific checks here

        parse_result.rule_checks[RuleID.ORTHO_VII.value] = len(violations) == 0

    def _check_ortho_viii(self, parse_result: ParseResult) -> None:
        """ORTHO VIII: Additional derivative/spelling cases."""
        # Additional spelling rules would go here
        parse_result.rule_checks[RuleID.ORTHO_VIII.value] = True

    def _check_ortho_ix(self, parse_result: ParseResult) -> None:
        """ORTHO IX: Additional derivative/spelling cases."""
        # Additional spelling rules would go here
        parse_result.rule_checks[RuleID.ORTHO_IX.value] = True

    def _check_ortho_x(self, parse_result: ParseResult) -> None:
        """ORTHO X: When adding -ing or -ish to words ending in e, the e is generally dropped.

        Examples: write → writing, shine → shining
        """
        violations = []

        for token in parse_result.tokens:
            if token.pos.value in {"noun", "verb", "adjective"}:
                word = token.text.lower()

                # Skip proper nouns (capitalized words) - they follow different rules
                if token.text[0].isupper() and token.pos.value == "noun":
                    continue

                # Check -ing and -ish suffixes
                if word.endswith(("ing", "ish")):
                    base_word = word[:-3] if word.endswith("ing") else word[:-4]
                    if len(base_word) >= 2 and base_word.endswith("e"):
                        violations.append(token)

        parse_result.rule_checks[RuleID.ORTHO_X.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.ORTHO_X,
                    message=f"Word '{token.text}' should drop final e before -ing or -ish",
                    span=Span(token.start, token.end),
                )
            )

    def _is_monosyllable(self, word: str) -> bool:
        """Check if a word is a monosyllable."""
        # Simple vowel count - more sophisticated syllable counting would be needed
        # for accurate results
        vowels = "aeiou"
        vowel_count = sum(1 for char in word if char in vowels)
        return vowel_count == 1

    def _has_accent_on_last_syllable(self, word: str) -> bool:
        """Check if word has accent on last syllable.

        This is a simplified implementation. In practice, accent detection
        requires sophisticated linguistic analysis.
        """
        # For now, we'll use a simple heuristic
        # Words ending in certain patterns often have accent on last syllable
        accented_endings = ["er", "or", "ar", "ur", "ir"]
        return any(word.endswith(ending) for ending in accented_endings)
