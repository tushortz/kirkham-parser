"""Grammar rule validator for the Kirkham Grammar Parser.

This module validates sentences against Kirkham's grammar rules,
implementing checking for the 35 rules of syntax from Kirkham's Grammar.
"""

from __future__ import annotations

from .lexicon import Lexicon
from .models import (
    DEFAULT_CONFIG,
    Flag,
    ParserConfig,
    ParseResult,
    Span,
    Token,
)
from .types import Case, Number, PartOfSpeech, Person, RuleID, Voice


class GrammarRuleValidator:
    """Validates sentences against Kirkham's grammar rules.
    Implements checking for the 35 rules of syntax from Kirkham's Grammar.
    """

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize validator with optional configuration.

        Args:
            config: Parser configuration. If None, uses DEFAULT_CONFIG.

        """
        self.config = config or DEFAULT_CONFIG

        # Verbs that govern infinitives with objective case subject
        self.gov_inf_verbs = frozenset(
            {
                "want",
                "wants",
                "wanted",
                "wish",
                "wishes",
                "wished",
                "expect",
                "expects",
                "expected",
                "ask",
                "asks",
                "asked",
                "tell",
                "tells",
                "told",
                "permit",
                "permits",
                "permitted",
                "allow",
                "allows",
                "allowed",
                "cause",
                "causes",
                "caused",
                "compel",
                "compels",
                "compelled",
                "advise",
                "advises",
                "advised",
                "encourage",
                "encourages",
                "encouraged",
            }
        )

    def _finite_verb_of_vp(self, vp) -> Token:
        """Find the finite verb anchor in a verb phrase.

        Prefers modals, then tensed BE/DO/HAVE auxiliaries, then lexical verbs
        with -s/-ed endings. This helps correctly identify the verb for agreement
        checking in complex auxiliary chains.

        Args:
            vp: Verb phrase to analyze

        Returns:
            The finite verb token (modal, tensed auxiliary, or main verb)

        Example:
            "will have been going" → returns "will" (modal)
            "has been chosen" → returns "has" (tensed auxiliary)
            "walks" → returns "walks" (3sg lexical verb)

        """
        # Prefer modal first
        for t in vp.tokens:
            if t.features.get("modal"):
                return t

        # Then tensed BE/DO/HAVE (not participles)
        for t in vp.tokens:
            if t.features.get("auxiliary") in {
                "be",
                "do",
                "have",
            } and not t.features.get("participle"):
                return t

        # Then any -s/-ed lexical verb
        for t in vp.tokens:
            if t.pos == PartOfSpeech.VERB and (
                t.text.endswith("s") or t.text.endswith("ed")
            ):
                return t

        # Fallback: last verb in chain
        return vp.tokens[-1] if vp.tokens else vp.tokens[0]

    def _pron_case(self, tok: Token) -> Case | None:
        """Get the grammatical case of a pronoun token."""
        return tok.case

    def validate(self, parse_result: ParseResult) -> None:
        """Validate parse result against grammar rules.
        Modifies parse_result in place by adding rule checks and errors.
        Respects parser configuration for rule enforcement.

        Args:
            parse_result: ParseResult object to validate

        """
        # RULE 3: The nominative case governs the verb (if enabled)
        if self.config.enforce_rule_3_strict:
            self._check_rule_3(parse_result)

        # RULE 4: The verb must agree with its nominative in number and person (if enabled)
        if self.config.enforce_rule_4_strict:
            self._check_rule_4(parse_result)

        # RULE 12: Possessive case governed by noun it possesses (if enabled)
        if self.config.enforce_rule_12_strict:
            self._check_rule_12(parse_result)

        # RULE 18: Adjectives belong to and qualify nouns (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_18(parse_result)

        # RULE 20: Active-transitive verbs govern the objective case (if enabled)
        if self.config.enforce_rule_20_strict:
            self._check_rule_20(parse_result)

        # RULE 31: Prepositions govern the objective case (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_31(parse_result)

        # Additional case checks (prep object, copula, governed infinitives)
        if self.config.enable_extended_validation:
            self._check_prep_object_case(parse_result)
            self._check_copula_predicative_case(parse_result)
            self._check_governed_infinitives(parse_result)

    def _check_rule_3(self, parse_result: ParseResult) -> None:
        """RULE 3: The nominative case governs the verb.
        A sentence should have a subject (nominative) for its verb.
        """
        has_subject = parse_result.subject is not None
        parse_result.rule_checks[RuleID.RULE_3.value] = has_subject

        if not has_subject and parse_result.verb_phrase:
            # Create Flag with span for verb phrase
            vp_start = parse_result.verb_phrase.tokens[0].start
            vp_end = parse_result.verb_phrase.tokens[-1].end

            flag = Flag(
                rule=RuleID.RULE_3,
                message="Verb phrase found without subject (nominative)",
                span=Span(start=vp_start, end=vp_end),
            )
            parse_result.flags.append(flag)
            # Backwards compatibility
            parse_result.errors.append(
                "RULE 3 violation: Verb phrase found without subject (nominative)"
            )

    def _check_rule_4(self, parse_result: ParseResult) -> None:
        """RULE 4: The verb must agree with its nominative in number and person."""
        if not parse_result.subject or not parse_result.verb_phrase:
            return

        subject_head = parse_result.subject.head_token

        # For agreement, check the finite verb anchor (modal, tensed auxiliary, or main verb)
        # This handles complex chains like "will have been going" correctly
        verb_to_check = self._finite_verb_of_vp(parse_result.verb_phrase)

        # Check agreement
        agrees = self._check_agreement(subject_head, verb_to_check)
        parse_result.rule_checks[RuleID.RULE_4.value] = agrees

        if not agrees:
            # Create Flag with span covering subject and verb
            span_start = min(subject_head.start, verb_to_check.start)
            span_end = max(subject_head.end, verb_to_check.end)

            flag = Flag(
                rule=RuleID.RULE_4,
                message=f"Verb '{verb_to_check.text}' does not agree with "
                f"subject '{subject_head.text}' in number/person",
                span=Span(start=span_start, end=span_end),
            )
            parse_result.flags.append(flag)
            # Backwards compatibility
            parse_result.errors.append(
                f"RULE 4 violation: Verb '{verb_to_check.text}' does not agree with "
                f"subject '{subject_head.text}' in number/person"
            )

    def _check_agreement(self, subject: Token, verb: Token) -> bool:
        """Check if verb agrees with subject in number and person."""
        subj_number = subject.number or Number.SINGULAR
        subj_person = subject.person or Person.THIRD

        # For "be" verb
        if verb.lemma in Lexicon.AUXILIARY_BE:
            if verb.lemma == "am":
                return subj_person == Person.FIRST and subj_number == Number.SINGULAR
            if verb.lemma == "is":
                return subj_person == Person.THIRD and subj_number == Number.SINGULAR
            if verb.lemma == "are":
                # "are" works with plural OR second person (you are)
                return subj_number == Number.PLURAL or subj_person == Person.SECOND
            if verb.lemma == "was":
                # "was" for 1st/3rd singular (I was, he was) but NOT "you was"
                return subj_number == Number.SINGULAR and subj_person != Person.SECOND
            if verb.lemma == "were":
                # "were" for plural OR second person (you were)
                return subj_number == Number.PLURAL or subj_person == Person.SECOND

        # For regular verbs: 3rd person singular should have -s
        if subj_person == Person.THIRD and subj_number == Number.SINGULAR:
            return verb.text.endswith("s") or verb.features.get("3sg", False)
        # Other persons: verb should not have -s ending (except irregular)
        return not verb.text.endswith("s") or verb.lemma in Lexicon.AUXILIARY_BE

    def _check_rule_12(self, parse_result: ParseResult) -> None:
        """RULE 12: A noun or pronoun in the possessive case is governed by
        the noun which it possesses.
        """
        possessive_pairs = []

        for i, token in enumerate(parse_result.tokens):
            if token.case == Case.POSSESSIVE:
                # Look for following noun
                j = i + 1
                # Skip articles and adjectives
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ARTICLE,
                    PartOfSpeech.ADJECTIVE,
                }:
                    j += 1

                # Check if noun follows
                if (
                    j < len(parse_result.tokens)
                    and parse_result.tokens[j].pos == PartOfSpeech.NOUN
                ):
                    possessive_pairs.append((i, j))
                else:
                    flag = Flag(
                        rule=RuleID.RULE_12,
                        message=f"Possessive '{token.text}' not followed by noun",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 12: Possessive '{token.text}' not followed by noun"
                    )

        if possessive_pairs:
            parse_result.rule_checks["rule_12_possessive_governed"] = True
            parse_result.notes.append(
                f"Found {len(possessive_pairs)} possessive relationship(s)"
            )

    def _check_rule_18(self, parse_result: ParseResult) -> None:
        """RULE 18: Adjectives belong to, and qualify, nouns expressed or understood."""
        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.ADJECTIVE:
                # Check if followed by noun
                has_noun = False
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.NOUN:
                        has_noun = True
                        break
                    if parse_result.tokens[j].pos not in {
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.ARTICLE,
                    }:
                        break

                if not has_noun:
                    flag = Flag(
                        rule=RuleID.RULE_18,  # Adjectives qualify nouns
                        message=f"Adjective '{token.text}' may lack noun to qualify",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 18: Adjective '{token.text}' may lack noun to qualify"
                    )

    def _check_rule_20(self, parse_result: ParseResult) -> None:
        """RULE 20: Active-transitive verbs govern the objective case.
        A transitive verb should have an object.
        """
        if not parse_result.verb_phrase:
            return

        # Check if verb is transitive
        is_transitive = any(
            token.features.get("transitive", False)
            for token in parse_result.verb_phrase.tokens
        )

        if is_transitive and parse_result.voice == Voice.ACTIVE:
            has_object = parse_result.object_phrase is not None
            parse_result.rule_checks[RuleID.RULE_20.value] = has_object

            if not has_object:
                # Create Flag with span for verb phrase
                vp_start = parse_result.verb_phrase.tokens[0].start
                vp_end = parse_result.verb_phrase.tokens[-1].end

                flag = Flag(
                    rule=RuleID.RULE_20,
                    message="Transitive verb may require object (objective case)",
                    span=Span(start=vp_start, end=vp_end),
                )
                parse_result.flags.append(flag)
                # Backwards compatibility
                parse_result.warnings.append(
                    "RULE 20: Transitive verb may require object (objective case)"
                )

    def _check_rule_31(self, parse_result: ParseResult) -> None:
        """RULE 31: Prepositions govern the objective case.
        A preposition should be followed by a noun/pronoun in objective case.
        """
        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PREPOSITION:
                # Look for following noun/pronoun
                found_object = False
                for j in range(i + 1, min(i + 4, len(parse_result.tokens))):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        found_object = True
                        break
                    if parse_result.tokens[j].pos == PartOfSpeech.PUNCTUATION:
                        break

                if not found_object:
                    flag = Flag(
                        rule=RuleID.RULE_31,  # Prepositions govern the objective case
                        message=f"Preposition '{token.text}' lacks object",
                        span=Span(start=token.start, end=token.end),
                    )
                    parse_result.flags.append(flag)
                    # Backwards compatibility
                    parse_result.warnings.append(
                        f"RULE 31: Preposition '{token.text}' lacks object"
                    )

    def _check_prep_object_case(self, pr: ParseResult) -> None:
        """Check that prepositions govern objective case pronouns.

        Flags nominative pronouns following prepositions (e.g., "between you and I").
        """
        for i, t in enumerate(pr.tokens):
            if t.pos == PartOfSpeech.PREPOSITION:
                k = i + 1
                # Scan short window for object, skipping articles/adjectives
                while k < len(pr.tokens) and pr.tokens[k].pos in {
                    PartOfSpeech.ARTICLE,
                    PartOfSpeech.ADJECTIVE,
                }:
                    k += 1

                if k < len(pr.tokens) and pr.tokens[k].pos == PartOfSpeech.PRONOUN:
                    if self._pron_case(pr.tokens[k]) == Case.NOMINATIVE:
                        pr.flags.append(
                            Flag(
                                RuleID.RULE_31,
                                f"Preposition '{t.text}' should govern objective case; "
                                f"found nominative '{pr.tokens[k].text}'",
                                Span(pr.tokens[k].start, pr.tokens[k].end),
                            )
                        )

    def _check_copula_predicative_case(self, pr: ParseResult) -> None:
        """Check predicative nominative after copula (be).

        In strict mode, flags objective pronouns after "to be" (e.g., "It is me").
        Respects allow_informal_pronouns config.
        """
        if not pr.verb_phrase:
            return

        # Check if verb phrase contains "be"
        if not any(
            tok.features.get("auxiliary") == "be" for tok in pr.verb_phrase.tokens
        ):
            return

        # Find next NP/pronoun after VP
        last = pr.verb_phrase.tokens[-1]
        start = pr.tokens.index(last) + 1

        if start < len(pr.tokens) and pr.tokens[start].pos == PartOfSpeech.PRONOUN:
            if self._pron_case(pr.tokens[start]) == Case.OBJECTIVE:
                if not self.config.allow_informal_pronouns:
                    pr.flags.append(
                        Flag(
                            RuleID.RULE_4,  # Using RULE_4 for agreement
                            f"After a form of 'to be', use nominative case; "
                            f"found '{pr.tokens[start].text}'",
                            Span(pr.tokens[start].start, pr.tokens[start].end),
                        )
                    )

    def _check_governed_infinitives(self, pr: ParseResult) -> None:
        """Check case of pronoun subject of governed infinitives.

        Verbs like "want", "expect", "tell" govern infinitives whose subject
        should be in objective case (e.g., "I want him to go", not "I want he to go").
        """
        # Find "to + V" sequences
        idxs = [i for i, t in enumerate(pr.tokens) if t.text.lower() == "to"]

        for i in idxs:
            j = i - 1  # Token before "to"
            if j <= 0:
                continue

            k = j - 1  # Token before that (potential governing verb)
            subj = pr.tokens[j]
            gov = pr.tokens[k]

            # Check: pronoun + to, with governing verb before
            if (
                subj.pos == PartOfSpeech.PRONOUN
                and gov.pos == PartOfSpeech.VERB
                and gov.lemma in self.gov_inf_verbs
            ) and self._pron_case(subj) == Case.NOMINATIVE:
                pr.flags.append(
                    Flag(
                        RuleID.RULE_20,  # Using RULE_20 for objective governance
                        f"Subject of governed infinitive after '{gov.text}' "
                        f"should be objective; found '{subj.text}'",
                        Span(subj.start, subj.end),
                    )
                )
