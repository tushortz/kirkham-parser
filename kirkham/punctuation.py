"""Punctuation Rules for the Kirkham Grammar Parser."""

from __future__ import annotations

from .models import Flag, ParseResult, Span
from .types import RuleID


class PunctuationValidator:
    def __init__(self, config):
        self.config = config

    def validate(self, parse_result: ParseResult) -> None:
        if not self.config.enforce_punctuation_rules:
            return

        # Basic period check
        if self.config.enforce_period_rules:
            self._check_period_rules(parse_result)

    def _check_period_rules(self, parse_result: ParseResult) -> None:
        violations = []

        # Look for sentences that should end with periods
        if not parse_result.tokens[-1].text.endswith((".", "!", "?")):
            violations.append(
                (
                    RuleID.PERIOD_RULE,
                    "Sentence should end with period, exclamation, or question mark",
                    Span(parse_result.tokens[-1].end, parse_result.tokens[-1].end),
                )
            )

        parse_result.rule_checks[RuleID.PERIOD_RULE.value] = len(violations) == 0

        for rule_id, message, span in violations:
            parse_result.flags.append(Flag(rule=rule_id, message=message, span=span))
