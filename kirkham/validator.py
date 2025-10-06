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

        # Verbs that take bare infinitives (Rule 25)
        self.bare_inf_verbs = frozenset(
            {
                "bid",
                "bids",
                "bade",
                "bidden",
                "dare",
                "dares",
                "dared",
                "need",
                "needs",
                "needed",
                "make",
                "makes",
                "made",
                "see",
                "sees",
                "saw",
                "seen",
                "hear",
                "hears",
                "heard",
                "feel",
                "feels",
                "felt",
                "help",
                "helps",
                "helped",
                "let",
                "lets",
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
        # RULE 1: A/an agrees with its noun in the singular only (if enabled)
        if self.config.enforce_rule_1_strict:
            self._check_rule_1(parse_result)

        # RULE 2: The belongs to nouns to limit/define their meaning (if enabled)
        if self.config.enforce_rule_2_strict:
            self._check_rule_2(parse_result)

        # RULE 3: The nominative case governs the verb (if enabled)
        if self.config.enforce_rule_3_strict:
            self._check_rule_3(parse_result)

        # RULE 4: The verb must agree with its nominative in number and person (if enabled)
        if self.config.enforce_rule_4_strict:
            self._check_rule_4(parse_result)

        # RULE 5: Nominative Independent (Address) (if enabled)
        if self.config.enforce_rule_5_strict:
            self._check_rule_5(parse_result)

        # RULE 6: Nominative Absolute (if enabled)
        if self.config.enforce_rule_6_strict:
            self._check_rule_6(parse_result)

        # RULE 7: Apposition (if enabled)
        if self.config.enforce_rule_7_strict:
            self._check_rule_7(parse_result)

        # RULE 8: Compound subjects need plural verb/pronoun (if enabled)
        if self.config.enforce_rule_8_strict:
            self._check_rule_8(parse_result)

        # RULE 9: Disjunctive conjunctions need singular verb/pronoun (if enabled)
        if self.config.enforce_rule_9_strict:
            self._check_rule_9(parse_result)

        # RULE 10: Collective nouns conveying unity need singular verb/pronoun (if enabled)
        if self.config.enforce_rule_10_strict:
            self._check_rule_10(parse_result)

        # RULE 11: Nouns of multitude conveying plurality need plural verb/pronoun (if enabled)
        if self.config.enforce_rule_11_strict:
            self._check_rule_11(parse_result)

        # RULE 12: Possessive case governed by noun it possesses (if enabled)
        if self.config.enforce_rule_12_strict:
            self._check_rule_12(parse_result)

        # RULE 13: Personal pronouns agree with their nouns in gender and number (if enabled)
        if self.config.enforce_rule_13_strict:
            self._check_rule_13(parse_result)

        # RULE 14: Relative pronouns agree with their antecedents (if enabled)
        if self.config.enforce_rule_14_strict:
            self._check_rule_14(parse_result)

        # RULE 15: Relative is nominative when no nominative between it and verb (if enabled)
        if self.config.enforce_rule_15_strict:
            self._check_rule_15(parse_result)

        # RULE 16: Relative governed by verb when nominative between them (if enabled)
        if self.config.enforce_rule_16_strict:
            self._check_rule_16(parse_result)

        # RULE 17: Interrogative pronouns agree with subsequent in case (if enabled)
        if self.config.enforce_rule_17_strict:
            self._check_rule_17(parse_result)

        # RULE 18: Adjectives belong to and qualify nouns (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_18(parse_result)

        # RULE 19: Adjective pronouns belong to nouns (if enabled)
        if self.config.enforce_rule_19_strict:
            self._check_rule_19(parse_result)

        # RULE 20: Active-transitive verbs govern the objective case (if enabled)
        if self.config.enforce_rule_20_strict:
            self._check_rule_20(parse_result)

        # RULE 21: To be admits the same case after it as before it (if enabled)
        if self.config.enforce_rule_21_strict:
            self._check_rule_21(parse_result)

        # RULE 22: Neuter verbs have same case before and after (if enabled)
        if self.config.enforce_rule_22_strict:
            self._check_rule_22(parse_result)

        # RULE 23: Infinitive governed by verb/noun/adjective/participle/pronoun (if enabled)
        if self.config.enforce_rule_23_strict:
            self._check_rule_23(parse_result)

        # RULE 24: Infinitive as nominative or object (if enabled)
        if self.config.enforce_rule_24_strict:
            self._check_rule_24(parse_result)

        # RULE 25: Bare infinitive after certain verbs (if enabled)
        if self.config.enforce_rule_25_strict:
            self._check_rule_25(parse_result)

        # RULE 28: Perfect participle belongs to noun/pronoun (if enabled)
        if self.config.enforce_rule_28_strict:
            self._check_rule_28(parse_result)

        # RULE 29: Adverbs qualify verbs, participles, adjectives, and other adverbs (if enabled)
        if self.config.enforce_rule_29_strict:
            self._check_rule_29(parse_result)

        # RULE 30: Prepositions are generally placed before the case they govern (if enabled)
        if self.config.enforce_rule_30_strict:
            self._check_rule_30(parse_result)

        # RULE 31: Prepositions govern the objective case (always checked if extended validation enabled)
        if self.config.enable_extended_validation:
            self._check_rule_31(parse_result)

        # RULE 32: Nouns signifying distance/time governed by understood preposition (if enabled)
        if self.config.enforce_rule_32_strict:
            self._check_rule_32(parse_result)

        # RULE 33: Conjunctions connect nouns/pronouns in same case (if enabled)
        if self.config.enforce_rule_33_strict:
            self._check_rule_33(parse_result)

        # RULE 34: Conjunctions connect verbs of like moods and tenses (if enabled)
        if self.config.enforce_rule_34_strict:
            self._check_rule_34(parse_result)

        # RULE 35: Noun/pronoun after than/as/but is nominative or governed (if enabled)
        if self.config.enforce_rule_35_strict:
            self._check_rule_35(parse_result)

        # Additional case checks (prep object, copula, governed infinitives)
        if self.config.enable_extended_validation:
            self._check_prep_object_case(parse_result)
            self._check_copula_predicative_case(parse_result)
            self._check_governed_infinitives(parse_result)

    def _check_rule_1(self, parse_result: ParseResult) -> None:
        """RULE 1: A/an agrees with its noun in the singular only.
        Articles 'a' and 'an' should only be used with singular nouns.
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.text.lower() in {"a", "an"} and token.pos == PartOfSpeech.ARTICLE:
                # Look for the following noun
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ADVERB,
                }:
                    j += 1

                if j < len(parse_result.tokens):
                    next_token = parse_result.tokens[j]
                    if next_token.pos == PartOfSpeech.NOUN:
                        # Check if noun is plural
                        if next_token.number == Number.PLURAL:
                            violations.append((token, next_token))

        parse_result.rule_checks[RuleID.RULE_1.value] = len(violations) == 0

        for article_token, noun_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_1,
                    message=f"Article '{article_token.text}' should only be used with singular nouns, not '{noun_token.text}'",
                    span=Span(article_token.start, noun_token.end),
                )
            )

    def _check_rule_2(self, parse_result: ParseResult) -> None:
        """RULE 2: The belongs to nouns to limit/define their meaning.
        The article 'the' should be followed by a noun (singular or plural).
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.text.lower() == "the" and token.pos == PartOfSpeech.ARTICLE:
                # Check if immediately followed by comparative adjective/adverb
                if i + 1 < len(parse_result.tokens):
                    next_token = parse_result.tokens[i + 1]
                    if next_token.pos in {
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.ADVERB,
                    } and next_token.lemma in {
                        "more",
                        "most",
                        "better",
                        "best",
                        "worse",
                        "worst",
                        "less",
                        "least",
                        "further",
                        "furthest",
                        "farther",
                        "farthest",
                    }:
                        continue  # Valid comparative construction

                # Look for the following noun
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ADVERB,
                }:
                    j += 1

                # Check if we have a valid construction
                is_valid = False
                if j < len(parse_result.tokens):
                    next_token = parse_result.tokens[j]
                    # Valid if followed by noun
                    if next_token.pos == PartOfSpeech.NOUN:
                        is_valid = True

                if not is_valid:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_2.value] = len(violations) == 0

        for article_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_2,
                    message="Article 'the' should be followed by a noun",
                    span=Span(article_token.start, article_token.end),
                )
            )

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

        # Check if subject is compound (contains "and")
        is_compound = self._is_compound_subject(parse_result.subject)

        # For compound subjects, use plural agreement
        if is_compound:
            # Create a virtual plural subject for agreement checking
            virtual_subject = Token(
                text="compound_subject",
                lemma="compound_subject",
                pos=PartOfSpeech.NOUN,
                start=parse_result.subject.tokens[0].start,
                end=parse_result.subject.tokens[-1].end,
                number=Number.PLURAL,
                person=Person.THIRD,
            )
            agrees = self._check_agreement(virtual_subject, verb_to_check)
        else:
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

        # For "have" auxiliary verbs
        if verb.lemma in Lexicon.AUXILIARY_HAVE:
            if verb.lemma in {"have", "has"}:
                # "has" for 3rd person singular, "have" for others
                if subj_person == Person.THIRD and subj_number == Number.SINGULAR:
                    return verb.lemma == "has"
                return verb.lemma == "have"
            # "had" works for all persons/numbers in past tense
            if verb.lemma == "had":
                return True

        # For "do" auxiliary verbs
        if verb.lemma in Lexicon.AUXILIARY_DO:
            if verb.lemma in {"do", "does"}:
                # "does" for 3rd person singular, "do" for others
                if subj_person == Person.THIRD and subj_number == Number.SINGULAR:
                    return verb.lemma == "does"
                return verb.lemma == "do"
            # "did" works for all persons/numbers in past tense
            if verb.lemma == "did":
                return True

        # For modal verbs (can, could, will, would, etc.)
        if verb.lemma in Lexicon.MODAL_VERBS:
            return True  # Modals don't change form for agreement

        # For past participles (worked, studied, etc.)
        if verb.features.get("participle") == "past":
            return True  # Past participles work with all subjects

        # For past tense verbs (gave, went, etc.) - they work with all subjects
        if verb.features.get("tense") == "past":
            return True

        # Check for common past tense irregular verbs
        past_tense_verbs = {
            "gave",
            "went",
            "came",
            "saw",
            "took",
            "made",
            "got",
            "had",
            "did",
            "said",
            "thought",
            "knew",
            "felt",
            "found",
            "left",
            "put",
            "brought",
            "bought",
            "caught",
            "taught",
            "fought",
            "sought",
            "wrote",
            "drove",
            "rode",
            "chose",
            "spoke",
            "broke",
            "stole",
            "froze",
            "threw",
            "drew",
            "grew",
            "flew",
            "blew",
        }
        if verb.lemma in past_tense_verbs:
            return True

        # For regular verbs: 3rd person singular should have -s
        if subj_person == Person.THIRD and subj_number == Number.SINGULAR:
            return verb.text.endswith("s") or verb.features.get("3sg", False)
        # Other persons: verb should not have -s ending (except irregular)
        # But allow past tense forms (ended in -ed) for all persons
        if verb.text.endswith("ed"):
            return True
        return not verb.text.endswith("s") or verb.lemma in Lexicon.AUXILIARY_BE

    def _is_compound_subject(self, subject_phrase) -> bool:
        """Check if subject phrase is compound (contains 'and')."""
        if not subject_phrase or not subject_phrase.tokens:
            return False

        # Check if any token in the subject phrase is "and"
        return any(token.text.lower() == "and" for token in subject_phrase.tokens)

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
                # Check if followed by noun (attributive use)
                has_noun_after = False
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.NOUN:
                        has_noun_after = True
                        break
                    if parse_result.tokens[j].pos not in {
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.ARTICLE,
                    }:
                        break

                # Check if preceded by linking verb (predicative use)
                is_predicative = False
                # Look backwards for linking verbs, skipping articles, adverbs, and adjectives
                for j in range(i - 1, -1, -1):
                    token_j = parse_result.tokens[j]
                    if token_j.pos == PartOfSpeech.VERB:
                        # Check for "to be" verbs or other linking verbs
                        if token_j.lemma in Lexicon.AUXILIARY_BE or token_j.lemma in {
                            "prove",
                            "proves",
                            "proved",
                            "become",
                            "becomes",
                            "became",
                            "seem",
                            "seems",
                            "seemed",
                            "appear",
                            "appears",
                            "appeared",
                            "look",
                            "looks",
                            "looked",
                            "feel",
                            "feels",
                            "felt",
                            "sound",
                            "sounds",
                            "sounded",
                            "taste",
                            "tastes",
                            "tasted",
                            "smell",
                            "smells",
                            "smelled",
                            "grow",
                            "grows",
                            "grew",
                            "turn",
                            "turns",
                            "turned",
                            "remain",
                            "remains",
                            "remained",
                            "stay",
                            "stays",
                            "stayed",
                            "keep",
                            "keeps",
                            "kept",
                            "get",
                            "gets",
                            "got",
                            "gotten",
                        }:
                            is_predicative = True
                            break
                        # If we find a non-linking verb, continue looking (don't break)
                        # This handles cases like "The more I study, the better I get"
                        # where "study" is not the linking verb, but "get" is
                    # Stop if we hit a non-auxiliary word that's not an article, adverb, adjective, punctuation, preposition, or pronoun
                    elif token_j.pos not in {
                        PartOfSpeech.ARTICLE,
                        PartOfSpeech.ADVERB,
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.PUNCTUATION,
                        PartOfSpeech.PREPOSITION,
                        PartOfSpeech.PRONOUN,
                    }:
                        break

                # Also look forward for linking verbs (handles cases like "The more I study, the better I get")
                if not is_predicative:
                    for j in range(i + 1, len(parse_result.tokens)):
                        token_j = parse_result.tokens[j]
                        if token_j.pos == PartOfSpeech.VERB:
                            # Check for "to be" verbs or other linking verbs
                            if (
                                token_j.lemma in Lexicon.AUXILIARY_BE
                                or token_j.lemma
                                in {
                                    "prove",
                                    "proves",
                                    "proved",
                                    "become",
                                    "becomes",
                                    "became",
                                    "seem",
                                    "seems",
                                    "seemed",
                                    "appear",
                                    "appears",
                                    "appeared",
                                    "look",
                                    "looks",
                                    "looked",
                                    "feel",
                                    "feels",
                                    "felt",
                                    "sound",
                                    "sounds",
                                    "sounded",
                                    "taste",
                                    "tastes",
                                    "tasted",
                                    "smell",
                                    "smells",
                                    "smelled",
                                    "grow",
                                    "grows",
                                    "grew",
                                    "turn",
                                    "turns",
                                    "turned",
                                    "remain",
                                    "remains",
                                    "remained",
                                    "stay",
                                    "stays",
                                    "stayed",
                                    "keep",
                                    "keeps",
                                    "kept",
                                    "get",
                                    "gets",
                                    "got",
                                    "gotten",
                                }
                            ):
                                is_predicative = True
                                break
                        # Stop if we hit a non-auxiliary word that's not an article, adverb, adjective, punctuation, preposition, or pronoun
                        elif token_j.pos not in {
                            PartOfSpeech.ARTICLE,
                            PartOfSpeech.ADVERB,
                            PartOfSpeech.ADJECTIVE,
                            PartOfSpeech.PUNCTUATION,
                            PartOfSpeech.PREPOSITION,
                            PartOfSpeech.PRONOUN,
                        }:
                            break

                # Also check for ellipsis cases (implied "to be" verbs)
                # Look for patterns like "X, and Y [adjective]" where Y is a noun
                if not is_predicative and i > 2:
                    # Look backwards for comma-conjunction-noun pattern
                    found_comma = False
                    found_conjunction = False
                    found_noun = False
                    for j in range(i - 1, -1, -1):
                        token_j = parse_result.tokens[j]
                        if not found_noun and token_j.pos == PartOfSpeech.NOUN:
                            found_noun = True
                        elif (
                            found_noun
                            and not found_conjunction
                            and token_j.pos == PartOfSpeech.CONJUNCTION
                            and token_j.lemma in {"and", "but", "or"}
                        ):
                            found_conjunction = True
                        elif (
                            found_conjunction
                            and not found_comma
                            and token_j.pos == PartOfSpeech.PUNCTUATION
                            and token_j.text == ","
                        ):
                            found_comma = True
                            break
                        elif token_j.pos not in {
                            PartOfSpeech.ARTICLE,
                            PartOfSpeech.ADVERB,
                            PartOfSpeech.ADJECTIVE,
                        }:
                            break

                    if found_comma and found_conjunction and found_noun:
                        is_predicative = True

                # Skip if adjective is predicative (after "to be") or has a following noun
                if is_predicative or has_noun_after:
                    continue

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

            # Check for relative pronouns that serve as objects
            has_relative_object = self._has_relative_object(parse_result)

            # Check for verbs that can be used intransitively
            verb_head = parse_result.verb_phrase.head_token
            can_be_intransitive = self._can_verb_be_intransitive(verb_head)

            # Only flag if verb truly needs an object
            needs_object = (
                not has_object and not has_relative_object and not can_be_intransitive
            )

            parse_result.rule_checks[RuleID.RULE_20.value] = not needs_object

            if needs_object:
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
                # Skip infinitive "to" constructions (to + verb)
                if token.text.lower() == "to" and i + 1 < len(parse_result.tokens):
                    next_token = parse_result.tokens[i + 1]
                    if next_token.pos == PartOfSpeech.VERB:
                        continue  # Valid infinitive construction

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

    def _check_rule_8(self, parse_result: ParseResult) -> None:
        """RULE 8: Two or more singular nouns joined by a copulative need a plural verb/pronoun.
        Compound subjects connected by "and" should take plural verbs.
        """
        if not parse_result.subject or not parse_result.verb_phrase:
            parse_result.rule_checks[RuleID.RULE_8.value] = True
            return

        # Check if subject contains multiple nouns connected by "and"
        subject_tokens = parse_result.subject.tokens
        has_and = any(token.text.lower() == "and" for token in subject_tokens)

        if has_and:
            # Count nouns in subject
            noun_count = sum(
                1 for token in subject_tokens if token.pos == PartOfSpeech.NOUN
            )

            if noun_count >= 2:
                # Check if verb is plural
                verb_token = self._finite_verb_of_vp(parse_result.verb_phrase)

                # For compound subjects, base form verbs (like "play", "run", "walk") are considered plural
                # Check if verb is explicitly plural OR is a base form that works with plural subjects
                # OR is a plural form of "be" (are, were)
                is_plural_verb = (
                    verb_token.number == Number.PLURAL
                    or self._is_base_form_verb_for_plural(verb_token)
                    or verb_token.lemma in {"are", "were"}
                )

                parse_result.rule_checks[RuleID.RULE_8.value] = is_plural_verb

                if not is_plural_verb:
                    parse_result.flags.append(
                        Flag(
                            rule=RuleID.RULE_8,
                            message=f"Compound subject requires plural verb, not '{verb_token.text}'",
                            span=Span(verb_token.start, verb_token.end),
                        )
                    )
            else:
                parse_result.rule_checks[RuleID.RULE_8.value] = True
        else:
            parse_result.rule_checks[RuleID.RULE_8.value] = True

    def _check_rule_13(self, parse_result: ParseResult) -> None:
        """RULE 13: Personal pronouns agree with their nouns in gender and number.
        Pronouns should match their antecedents in gender and number.
        """
        violations = []

        # Only check personal pronouns, not demonstrative/relative/interrogative pronouns
        for token in parse_result.tokens:
            if token.pos == PartOfSpeech.PRONOUN:
                # Check if it's a personal pronoun (has pronoun_type feature)
                if token.features.get("pronoun_type") == "personal":
                    # Check if pronoun has proper gender/number attributes
                    if not token.gender or not token.number:
                        violations.append(token)

        parse_result.rule_checks[RuleID.RULE_13.value] = len(violations) == 0

        for pronoun_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_13,
                    message=f"Personal pronoun '{pronoun_token.text}' should have clear gender and number",
                    span=Span(pronoun_token.start, pronoun_token.end),
                )
            )

    def _check_rule_19(self, parse_result: ParseResult) -> None:
        """RULE 19: Adjective pronouns belong to nouns (expressed or understood).
        Adjective pronouns (my, your, his, etc.) should modify nouns.
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PRONOUN and token.features.get("possessive"):
                # Look for following noun
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ADVERB,
                }:
                    j += 1

                if (
                    j >= len(parse_result.tokens)
                    or parse_result.tokens[j].pos != PartOfSpeech.NOUN
                ):
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_19.value] = len(violations) == 0

        for pronoun_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_19,
                    message=f"Possessive pronoun '{pronoun_token.text}' should be followed by a noun",
                    span=Span(pronoun_token.start, pronoun_token.end),
                )
            )

    def _check_rule_21(self, parse_result: ParseResult) -> None:
        """RULE 21: To be admits the same case after it as before it.
        Enhanced copula case agreement checking.
        """
        if not parse_result.verb_phrase:
            parse_result.rule_checks[RuleID.RULE_21.value] = True
            return

        # Check if verb phrase contains 'be' forms
        has_be = any(
            token.features.get("auxiliary") == "be"
            for token in parse_result.verb_phrase.tokens
        )

        if has_be and parse_result.subject:
            # Find the complement after the verb
            vp_end_idx = parse_result.tokens.index(parse_result.verb_phrase.tokens[-1])
            complement_start = vp_end_idx + 1

            if complement_start < len(parse_result.tokens):
                complement_token = parse_result.tokens[complement_start]

                if complement_token.pos == PartOfSpeech.PRONOUN:
                    subject_case = parse_result.subject.tokens[0].case
                    complement_case = complement_token.case

                    # In formal English, cases should match
                    if (
                        not self.config.allow_informal_pronouns
                        and subject_case is not None
                        and complement_case is not None
                        and subject_case != complement_case
                    ):
                        parse_result.flags.append(
                            Flag(
                                rule=RuleID.RULE_21,
                                message=f"After 'to be', use same case as subject; found '{complement_token.text}' (should be {subject_case.value})",
                                span=Span(complement_token.start, complement_token.end),
                            )
                        )
                        parse_result.rule_checks[RuleID.RULE_21.value] = False
                        return

        parse_result.rule_checks[RuleID.RULE_21.value] = True

    def _check_rule_25(self, parse_result: ParseResult) -> None:
        """RULE 25: After bid, dare, need, make, see, hear, feel, help, let, the following verb is infinitive without to.
        Certain verbs take bare infinitives (without 'to').
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.VERB and token.lemma in self.bare_inf_verbs:
                # Look for 'to' + verb pattern that should be bare infinitive
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADVERB,
                    PartOfSpeech.ARTICLE,
                    PartOfSpeech.PRONOUN,
                }:
                    j += 1

                if j < len(parse_result.tokens) and (
                    parse_result.tokens[j].text.lower() == "to"
                    and parse_result.tokens[j].pos == PartOfSpeech.PREPOSITION
                ):
                    k = j + 1
                    while k < len(parse_result.tokens) and parse_result.tokens[
                        k
                    ].pos in {PartOfSpeech.ADVERB, PartOfSpeech.ARTICLE}:
                        k += 1

                    if (
                        k < len(parse_result.tokens)
                        and parse_result.tokens[k].pos == PartOfSpeech.VERB
                    ):
                        violations.append(
                            (token, parse_result.tokens[j], parse_result.tokens[k])
                        )

        parse_result.rule_checks[RuleID.RULE_25.value] = len(violations) == 0

        for main_verb, to_token, infinitive_verb in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_25,
                    message=f"After '{main_verb.text}', use bare infinitive without 'to': '{infinitive_verb.text}'",
                    span=Span(to_token.start, infinitive_verb.end),
                )
            )

    def _check_rule_28(self, parse_result: ParseResult) -> None:
        """RULE 28: The perfect participle belongs, like an adjective, to some noun/pronoun.
        Perfect participles (having + past participle) should modify nouns/pronouns.
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.features.get("participle") == "perfect":
                # Look for following noun/pronoun
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ADVERB,
                }:
                    j += 1

                if j >= len(parse_result.tokens) or parse_result.tokens[j].pos not in {
                    PartOfSpeech.NOUN,
                    PartOfSpeech.PRONOUN,
                }:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_28.value] = len(violations) == 0

        for participle_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_28,
                    message=f"Perfect participle '{participle_token.text}' should modify a noun or pronoun",
                    span=Span(participle_token.start, participle_token.end),
                )
            )

    def _check_rule_29(self, parse_result: ParseResult) -> None:
        """RULE 29: Adverbs qualify verbs, participles, adjectives, and other adverbs.
        Adverbs should modify appropriate parts of speech.
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.ADVERB:
                # Skip temporal adverbs that can stand alone (later, then, now, etc.)
                temporal_adverbs = {
                    "later",
                    "then",
                    "now",
                    "today",
                    "yesterday",
                    "tomorrow",
                    "soon",
                    "recently",
                }
                if token.lemma in temporal_adverbs:
                    continue

                # Check if adverb has a valid target
                has_target = False

                # Look for targets before and after (extend window for better detection)
                for j in range(max(0, i - 5), min(len(parse_result.tokens), i + 6)):
                    if j != i:
                        target_token = parse_result.tokens[j]
                        if target_token.pos in {
                            PartOfSpeech.VERB,
                            PartOfSpeech.PARTICIPLE,
                            PartOfSpeech.ADJECTIVE,
                            PartOfSpeech.ADVERB,
                        }:
                            has_target = True
                            break

                if not has_target:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_29.value] = len(violations) == 0

        for adverb_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_29,
                    message=f"Adverb '{adverb_token.text}' should modify a verb, participle, adjective, or another adverb",
                    span=Span(adverb_token.start, adverb_token.end),
                )
            )

    def _check_rule_30(self, parse_result: ParseResult) -> None:
        """RULE 30: Prepositions are generally placed before the case they govern.
        Prepositions should come before their objects.
        """
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PREPOSITION:
                # Skip infinitive "to" constructions (to + verb)
                if token.text.lower() == "to" and i + 1 < len(parse_result.tokens):
                    next_token = parse_result.tokens[i + 1]
                    if next_token.pos == PartOfSpeech.VERB:
                        continue  # Valid infinitive construction

                # Check if preposition is followed by its object
                j = i + 1
                while j < len(parse_result.tokens) and parse_result.tokens[j].pos in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ADVERB,
                    PartOfSpeech.ARTICLE,
                }:
                    j += 1

                if j >= len(parse_result.tokens) or parse_result.tokens[j].pos not in {
                    PartOfSpeech.NOUN,
                    PartOfSpeech.PRONOUN,
                }:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_30.value] = len(violations) == 0

        for prep_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_30,
                    message=f"Preposition '{prep_token.text}' should be followed by its object",
                    span=Span(prep_token.start, prep_token.end),
                )
            )

    def _has_relative_object(self, parse_result: ParseResult) -> bool:
        """Check if there are relative pronouns that serve as objects."""
        if not parse_result.tokens:
            return False

        # Look for relative pronouns (who, whom, which, that) that could be objects
        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PRONOUN and token.lemma in {
                "who",
                "whom",
                "which",
                "that",
            }:
                # Check if this relative pronoun is followed by a subject and then our verb
                if i + 2 < len(parse_result.tokens):
                    next_token = parse_result.tokens[i + 1]
                    verb_token = parse_result.tokens[i + 2]
                    if (
                        next_token.pos in {PartOfSpeech.PRONOUN, PartOfSpeech.NOUN}
                        and verb_token.pos == PartOfSpeech.VERB
                        and verb_token.features.get("transitive", False)
                    ):
                        return True
        return False

    def _can_verb_be_intransitive(self, verb_token: Token) -> bool:
        """Check if a verb can be used intransitively."""
        # Verbs that are commonly used intransitively
        intransitive_verbs = {
            "play",
            "plays",
            "played",  # "The children play"
            "study",
            "studies",
            "studied",  # "I study every day"
            "work",
            "works",
            "worked",  # "He works hard"
            "run",
            "runs",
            "ran",  # "She runs fast"
            "walk",
            "walks",
            "walked",  # "They walk to school"
            "sleep",
            "sleeps",
            "slept",  # "I sleep well"
            "eat",
            "eats",
            "ate",  # "We eat together"
            "drink",
            "drinks",
            "drank",  # "They drink water"
            "read",
            "reads",
            "write",
            "writes",
            "wrote",  # "He writes stories"
            "see",
            "sees",
            "saw",  # "I can see" (ability)
            "hear",
            "hears",
            "heard",  # "I can hear"
            "smell",
            "smells",
            "smelled",  # "I can smell"
            "taste",
            "tastes",
            "tasted",  # "I can taste"
            "feel",
            "feels",
            "felt",  # "I can feel"
        }
        return verb_token.lemma in intransitive_verbs

    def _is_base_form_verb_for_plural(self, verb_token: Token) -> bool:
        """Check if a verb is a base form that works with plural subjects."""
        # Base form verbs that work with plural subjects (no -s ending)
        base_form_verbs = {
            "play",
            "run",
            "walk",
            "talk",
            "work",
            "study",
            "eat",
            "drink",
            "sleep",
            "read",
            "write",
            "see",
            "hear",
            "feel",
            "think",
            "know",
            "go",
            "come",
            "stay",
            "leave",
            "arrive",
            "depart",
            "begin",
            "start",
            "end",
            "finish",
            "continue",
            "stop",
            "help",
            "want",
            "need",
            "like",
            "love",
            "hate",
            "prefer",
            "choose",
            "decide",
            "plan",
            "hope",
            "expect",
            "believe",
            "understand",
            "remember",
            "forget",
            "learn",
            "teach",
            "show",
            "tell",
            "ask",
            "answer",
            "speak",
            "listen",
            "watch",
            "look",
            "find",
            "lose",
            "win",
            "fail",
            "succeed",
            "try",
            "attempt",
        }
        return verb_token.lemma in base_form_verbs

    def _check_rule_5(self, parse_result: ParseResult) -> None:
        """RULE 5: When an address is made, the noun or pronoun addressed, is put in the nominative case independent."""
        violations = []

        # Look for vocative expressions (direct address)
        # Pattern: "John, come here" or "Come here, John"
        for i, token in enumerate(parse_result.tokens):
            if token.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                # Check if this is a direct address
                is_vocative = False

                # Check if followed by comma and imperative/command
                if (
                    i + 1 < len(parse_result.tokens)
                    and parse_result.tokens[i + 1].text == ","
                    and i + 2 < len(parse_result.tokens)
                ):
                    next_token = parse_result.tokens[i + 2]
                    if next_token.pos == PartOfSpeech.VERB:
                        is_vocative = True

                # Check if preceded by comma and imperative/command
                elif (
                    i > 1
                    and parse_result.tokens[i - 1].text == ","
                    and parse_result.tokens[i - 2].pos == PartOfSpeech.VERB
                ):
                    is_vocative = True

                if is_vocative and token.case != Case.NOMINATIVE:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_5.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_5,
                    message=f"Addressed noun/pronoun {token.text} should be in nominative case independent",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_6(self, parse_result: ParseResult) -> None:
        """RULE 6: A noun or pronoun placed before a participle, and being independent of the rest of the sentence, is in the nominative case absolute."""
        violations = []

        # Look for absolute constructions: "The weather being fine, we went out"
        for i, token in enumerate(parse_result.tokens):
            if token.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                # Check if followed by participle and comma
                if (
                    i + 2 < len(parse_result.tokens)
                    and parse_result.tokens[i + 1].pos == PartOfSpeech.PARTICIPLE
                    and parse_result.tokens[i + 2].text == ","
                ):
                    # This is likely an absolute construction
                    if token.case != Case.NOMINATIVE:
                        violations.append(token)

        parse_result.rule_checks[RuleID.RULE_6.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_6,
                    message=f"Noun/pronoun {token.text} in absolute construction should be in nominative case",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_7(self, parse_result: ParseResult) -> None:
        """RULE 7: Two or more nouns, or nouns and pronouns, signifying the same thing, are put, by apposition, in the same case."""
        violations = []

        # Look for appositive constructions: "John, the teacher, is here"
        for i, token in enumerate(parse_result.tokens):
            if token.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                # Check if this is an appositive (noun/pronoun set off by commas)
                if (
                    i > 0
                    and i + 1 < len(parse_result.tokens)
                    and parse_result.tokens[i - 1].text == ","
                    and parse_result.tokens[i + 1].text == ","
                ):
                    # Find the main noun/pronoun this appositive refers to
                    main_token = None
                    # Look backwards for the main noun/pronoun
                    for j in range(i - 2, -1, -1):
                        if parse_result.tokens[j].pos in {
                            PartOfSpeech.NOUN,
                            PartOfSpeech.PRONOUN,
                        }:
                            main_token = parse_result.tokens[j]
                            break

                    # Look forwards for the main noun/pronoun
                    if main_token is None:
                        for j in range(i + 2, len(parse_result.tokens)):
                            if parse_result.tokens[j].pos in {
                                PartOfSpeech.NOUN,
                                PartOfSpeech.PRONOUN,
                            }:
                                main_token = parse_result.tokens[j]
                                break

                    if main_token and token.case != main_token.case:
                        violations.append(token)

        parse_result.rule_checks[RuleID.RULE_7.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_7,
                    message=f"Appositive {token.text} should be in the same case as the noun it refers to",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_9(self, parse_result: ParseResult) -> None:
        """RULE 9: Two or more nouns, or nouns and pronouns, in the singular number, connected by disjunctive conjunctions, must have verbs, nouns, and pronouns, agreeing with them in the singular."""
        if not parse_result.subject or not parse_result.verb_phrase:
            parse_result.rule_checks[RuleID.RULE_9.value] = True
            return

        # Check if subject contains disjunctive conjunctions (or, nor)
        subject_tokens = parse_result.subject.tokens
        has_disjunctive = any(
            token.text.lower() in {"or", "nor"} for token in subject_tokens
        )

        if has_disjunctive:
            # Count nouns in subject
            noun_count = sum(
                1 for token in subject_tokens if token.pos == PartOfSpeech.NOUN
            )

            if noun_count >= 2:
                # Check if verb is singular (for disjunctive subjects)
                verb_token = self._finite_verb_of_vp(parse_result.verb_phrase)
                is_singular_verb = (
                    verb_token.number == Number.SINGULAR
                    or verb_token.lemma in {"is", "was", "has", "does"}
                    or self._is_singular_form_verb(verb_token)
                )

                parse_result.rule_checks[RuleID.RULE_9.value] = is_singular_verb

                if not is_singular_verb:
                    parse_result.flags.append(
                        Flag(
                            rule=RuleID.RULE_9,
                            message=f"Disjunctive subject requires singular verb, not {verb_token.text}",
                            span=Span(verb_token.start, verb_token.end),
                        )
                    )
            else:
                parse_result.rule_checks[RuleID.RULE_9.value] = True
        else:
            parse_result.rule_checks[RuleID.RULE_9.value] = True

    def _check_rule_10(self, parse_result: ParseResult) -> None:
        """RULE 10: A collective noun or noun of multitude, conveying unity of idea, generally has a verb or pronoun agreeing with it in the singular."""
        violations = []

        # Collective nouns that convey unity of idea
        collective_nouns = {
            "team",
            "group",
            "class",
            "family",
            "committee",
            "jury",
            "audience",
            "crowd",
            "herd",
            "flock",
            "pack",
            "swarm",
            "school",
            "army",
            "navy",
            "government",
            "company",
            "corporation",
            "organization",
            "society",
        }

        for token in parse_result.tokens:
            if (
                token.pos == PartOfSpeech.NOUN
                and token.lemma in collective_nouns
                and token.number == Number.PLURAL
            ):
                violations.append(token)

        parse_result.rule_checks[RuleID.RULE_10.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_10,
                    message=f"Collective noun {token.text} conveying unity should be singular",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_11(self, parse_result: ParseResult) -> None:
        """RULE 11: A noun of multitude, conveying plurality of idea, must have a verb or pronoun agreeing with it in the plural."""
        violations = []

        # Nouns of multitude that convey plurality of idea
        multitude_nouns = {
            "people",
            "men",
            "women",
            "children",
            "police",
            "cattle",
            "poultry",
            "vermin",
            "clergy",
            "gentry",
            "nobility",
            "peasantry",
        }

        for token in parse_result.tokens:
            if (
                token.pos == PartOfSpeech.NOUN
                and token.lemma in multitude_nouns
                and token.number == Number.SINGULAR
            ):
                violations.append(token)

        parse_result.rule_checks[RuleID.RULE_11.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_11,
                    message=f"Noun of multitude {token.text} conveying plurality should be plural",
                    span=Span(token.start, token.end),
                )
            )

    def _is_singular_form_verb(self, verb_token: Token) -> bool:
        """Check if a verb is in singular form."""
        # Singular forms of common verbs
        singular_forms = {
            "is",
            "was",
            "has",
            "does",
            "goes",
            "comes",
            "runs",
            "walks",
            "talks",
            "works",
            "studies",
            "eats",
            "drinks",
            "sleeps",
            "reads",
            "writes",
            "sees",
            "hears",
            "feels",
            "thinks",
            "knows",
        }
        return verb_token.lemma in singular_forms

    def _check_rule_14(self, parse_result: ParseResult) -> None:
        """RULE 14: Relative pronouns agree with their antecedents, in gender, person, and number."""
        violations = []

        # Relative pronouns
        relative_pronouns = {"who", "whom", "which", "that", "whose"}

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PRONOUN and token.lemma in relative_pronouns:
                # Find the antecedent (noun/pronoun this relative refers to)
                antecedent = self._find_antecedent(parse_result.tokens, i)

                if antecedent:
                    # Check agreement in gender, person, and number
                    if (
                        token.gender != antecedent.gender
                        or token.person != antecedent.person
                        or token.number != antecedent.number
                    ):
                        violations.append((token, antecedent))

        parse_result.rule_checks[RuleID.RULE_14.value] = len(violations) == 0

        for relative_token, antecedent_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_14,
                    message=f"Relative pronoun {relative_token.text} should agree with antecedent {antecedent_token.text} in gender, person, and number",
                    span=Span(relative_token.start, relative_token.end),
                )
            )

    def _check_rule_15(self, parse_result: ParseResult) -> None:
        """RULE 15: The relative is the nominative case to the verb, when no nominative comes between it and the verb."""
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PRONOUN and token.lemma in {
                "who",
                "which",
                "that",
            }:
                # Look for verb after the relative pronoun
                verb_found = False
                nominative_between = False

                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                        verb_found = True
                        break
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        nominative_between = True

                if (
                    verb_found
                    and not nominative_between
                    and token.case != Case.NOMINATIVE
                ):
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_15.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_15,
                    message=f"Relative pronoun {token.text} should be in nominative case when no nominative comes between it and the verb",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_16(self, parse_result: ParseResult) -> None:
        """RULE 16: When a nominative comes between the relative and the verb, the relative is governed by the following verb, or by some other word in its own member of the sentence."""
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.PRONOUN and token.lemma in {
                "who",
                "whom",
                "which",
                "that",
            }:
                # Look for nominative between relative and verb
                nominative_between = False
                verb_after = None

                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        nominative_between = True
                    elif (
                        parse_result.tokens[j].pos == PartOfSpeech.VERB
                        and nominative_between
                    ):
                        verb_after = parse_result.tokens[j]
                        break

                if nominative_between and verb_after:
                    # Relative should be governed by the verb (objective case for transitive verbs)
                    if (
                        verb_after.features.get("transitive", False)
                        and token.case != Case.OBJECTIVE
                    ):
                        violations.append(token)

        parse_result.rule_checks[RuleID.RULE_16.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_16,
                    message=f"Relative pronoun {token.text} should be in objective case when nominative comes between it and transitive verb",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_17(self, parse_result: ParseResult) -> None:
        """RULE 17: When a relative pronoun is of the interrogative kind, it refers to the word or phrase containing the answer to the question for its subsequent, which subsequent must agree in case with the interrogative."""
        violations = []

        # Interrogative pronouns
        interrogative_pronouns = {"who", "whom", "which", "what", "whose"}

        for i, token in enumerate(parse_result.tokens):
            if (
                token.pos == PartOfSpeech.PRONOUN
                and token.lemma in interrogative_pronouns
            ):
                # Check if this is in a question context
                is_question = any(t.text == "?" for t in parse_result.tokens)

                if is_question:
                    # Find the subsequent (answer) in the sentence
                    subsequent = self._find_subsequent_in_question(
                        parse_result.tokens, i
                    )

                    if subsequent and token.case != subsequent.case:
                        violations.append((token, subsequent))

        parse_result.rule_checks[RuleID.RULE_17.value] = len(violations) == 0

        for interrogative_token, subsequent_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_17,
                    message=f"Interrogative pronoun {interrogative_token.text} should agree in case with subsequent {subsequent_token.text}",
                    span=Span(interrogative_token.start, interrogative_token.end),
                )
            )

    def _find_antecedent(
        self, tokens: list[Token], relative_index: int
    ) -> Token | None:
        """Find the antecedent noun/pronoun for a relative pronoun."""
        # Look backwards from the relative pronoun
        for i in range(relative_index - 1, -1, -1):
            token = tokens[i]
            if token.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                return token
        return None

    def _find_subsequent_in_question(
        self, tokens: list[Token], interrogative_index: int
    ) -> Token | None:
        """Find the subsequent (answer) noun/pronoun in a question."""
        # Look forwards from the interrogative pronoun
        for i in range(interrogative_index + 1, len(tokens)):
            token = tokens[i]
            if token.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                return token
        return None

    def _check_rule_22(self, parse_result: ParseResult) -> None:
        """RULE 22: Active-intransitive and passive verbs, the verb to become, and other neuter verbs, have the same case after them as before them, when both words refer to, and signify, the same thing."""
        violations = []

        # Neuter verbs (linking verbs that don't take objects)
        neuter_verbs = {
            "become",
            "becomes",
            "became",
            "seem",
            "seems",
            "seemed",
            "appear",
            "appears",
            "appeared",
            "look",
            "looks",
            "looked",
            "feel",
            "feels",
            "felt",
            "sound",
            "sounds",
            "sounded",
            "taste",
            "tastes",
            "tasted",
            "smell",
            "smells",
            "smelled",
            "grow",
            "grows",
            "grew",
            "turn",
            "turns",
            "turned",
            "remain",
            "remains",
            "remained",
            "stay",
            "stays",
            "stayed",
            "keep",
            "keeps",
            "kept",
            "get",
            "gets",
            "got",
            "gotten",
        }

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.VERB and token.lemma in neuter_verbs:
                # Find subject before verb
                subject_token = None
                for j in range(i - 1, -1, -1):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        subject_token = parse_result.tokens[j]
                        break

                # Find complement after verb
                complement_token = None
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        complement_token = parse_result.tokens[j]
                        break

                if subject_token and complement_token:
                    # Check if they refer to the same thing (same case)
                    if subject_token.case != complement_token.case:
                        violations.append((token, subject_token, complement_token))

        parse_result.rule_checks[RuleID.RULE_22.value] = len(violations) == 0

        for verb_token, subject_token, complement_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_22,
                    message=f"Neuter verb {verb_token.text} requires same case before and after when referring to same thing",
                    span=Span(subject_token.start, complement_token.end),
                )
            )

    def _check_rule_23(self, parse_result: ParseResult) -> None:
        """RULE 23: A verb in the infinitive mood may be governed by a verb, noun, adjective, participle, or pronoun."""
        violations = []

        # Look for infinitive verbs (preceded by "to")
        for i, token in enumerate(parse_result.tokens):
            if (
                token.pos == PartOfSpeech.VERB
                and token.features.get("mood") == "infinitive"
            ):
                # Check if preceded by governing word
                has_governor = False

                # Look backwards for governor
                for j in range(i - 1, -1, -1):
                    governor = parse_result.tokens[j]
                    if governor.pos in {
                        PartOfSpeech.VERB,
                        PartOfSpeech.NOUN,
                        PartOfSpeech.ADJECTIVE,
                        PartOfSpeech.PARTICIPLE,
                        PartOfSpeech.PRONOUN,
                    }:
                        has_governor = True
                        break
                    if governor.text.lower() == "to":
                        # "to" is the infinitive marker, continue looking
                        continue
                    break

                if not has_governor:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_23.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_23,
                    message=f"Infinitive verb {token.text} should be governed by a verb, noun, adjective, participle, or pronoun",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_24(self, parse_result: ParseResult) -> None:
        """RULE 24: The infinitive mood, or part of a sentence, is frequently put as the nominative case to a verb, or the object of an active-transitive verb."""
        violations = []

        # Look for infinitive verbs
        for i, token in enumerate(parse_result.tokens):
            if (
                token.pos == PartOfSpeech.VERB
                and token.features.get("mood") == "infinitive"
            ):
                # Check if used as nominative (subject) or object
                is_nominative = False
                is_object = False

                # Check if used as subject (before main verb)
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                        is_nominative = True
                        break

                # Check if used as object (after transitive verb)
                for j in range(i - 1, -1, -1):
                    if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                        if parse_result.tokens[j].features.get("transitive", False):
                            is_object = True
                        break

                if not is_nominative and not is_object:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_24.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_24,
                    message=f"Infinitive {token.text} should be used as nominative or object of transitive verb",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_26(self, parse_result: ParseResult) -> None:
        """RULE 26: Participles have the same government as the verbs have from which they are derived."""
        violations = []

        for token in parse_result.tokens:
            if token.pos == PartOfSpeech.PARTICIPLE:
                # Check if participle has proper government (object for transitive verbs)
                base_verb = token.lemma  # Get base form

                # Check if base verb is transitive
                if base_verb in Lexicon.COMMON_TRANSITIVE_VERBS:
                    # Look for object after participle
                    has_object = False
                    for i, t in enumerate(parse_result.tokens):
                        if t == token:
                            # Look for object after this participle
                            for j in range(i + 1, len(parse_result.tokens)):
                                if parse_result.tokens[j].pos in {
                                    PartOfSpeech.NOUN,
                                    PartOfSpeech.PRONOUN,
                                }:
                                    has_object = True
                                    break
                            break

                    if not has_object:
                        violations.append(token)

        parse_result.rule_checks[RuleID.RULE_26.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_26,
                    message=f"Participle {token.text} derived from transitive verb should have object",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_27(self, parse_result: ParseResult) -> None:
        """RULE 27: The present participle refers to some noun or pronoun denoting the subject or actor."""
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if (
                token.pos == PartOfSpeech.PARTICIPLE
                and token.features.get("participle") == "present"
            ):
                # Look for subject/actor noun/pronoun
                has_subject = False

                # Look backwards for subject
                for j in range(i - 1, -1, -1):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        has_subject = True
                        break

                # Look forwards for subject
                if not has_subject:
                    for j in range(i + 1, len(parse_result.tokens)):
                        if parse_result.tokens[j].pos in {
                            PartOfSpeech.NOUN,
                            PartOfSpeech.PRONOUN,
                        }:
                            has_subject = True
                            break

                if not has_subject:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_27.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_27,
                    message=f"Present participle {token.text} should refer to a subject or actor",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_32(self, parse_result: ParseResult) -> None:
        """RULE 32: Home, and nouns signifying distance, time when, how long, &c. are generally governed by a preposition understood."""
        violations = []

        # Nouns that typically need understood prepositions
        understood_prep_nouns = {
            "home",
            "distance",
            "time",
            "duration",
            "length",
            "width",
            "height",
            "depth",
            "breadth",
            "extent",
            "space",
            "place",
            "location",
        }

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.NOUN and token.lemma in understood_prep_nouns:
                # Check if preceded by preposition
                has_preposition = False
                if i > 0 and parse_result.tokens[i - 1].pos == PartOfSpeech.PREPOSITION:
                    has_preposition = True

                if not has_preposition:
                    violations.append(token)

        parse_result.rule_checks[RuleID.RULE_32.value] = len(violations) == 0

        for token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_32,
                    message=f"Noun {token.text} typically requires understood preposition",
                    span=Span(token.start, token.end),
                )
            )

    def _check_rule_33(self, parse_result: ParseResult) -> None:
        """RULE 33: Conjunctions connect nouns and pronouns in the same case."""
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.CONJUNCTION and token.text.lower() in {
                "and",
                "or",
                "nor",
                "but",
            }:
                # Find nouns/pronouns connected by this conjunction
                left_token = None
                right_token = None

                # Look backwards for first noun/pronoun
                for j in range(i - 1, -1, -1):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        left_token = parse_result.tokens[j]
                        break

                # Look forwards for second noun/pronoun
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        right_token = parse_result.tokens[j]
                        break

                if left_token and right_token and left_token.case != right_token.case:
                    violations.append((token, left_token, right_token))

        parse_result.rule_checks[RuleID.RULE_33.value] = len(violations) == 0

        for conj_token, left_token, right_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_33,
                    message=f"Conjunction {conj_token.text} connects nouns/pronouns that should be in same case",
                    span=Span(left_token.start, right_token.end),
                )
            )

    def _check_rule_34(self, parse_result: ParseResult) -> None:
        """RULE 34: Conjunctions generally connect verbs of like moods and tenses."""
        violations = []

        for i, token in enumerate(parse_result.tokens):
            if token.pos == PartOfSpeech.CONJUNCTION and token.text.lower() in {
                "and",
                "or",
                "nor",
                "but",
            }:
                # Find verbs connected by this conjunction
                left_verb = None
                right_verb = None

                # Look backwards for first verb
                for j in range(i - 1, -1, -1):
                    if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                        left_verb = parse_result.tokens[j]
                        break

                # Look forwards for second verb
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                        right_verb = parse_result.tokens[j]
                        break

                if left_verb and right_verb:
                    # Check if verbs have compatible moods and tenses
                    left_mood = left_verb.features.get("mood", "indicative")
                    right_mood = right_verb.features.get("mood", "indicative")
                    left_tense = left_verb.features.get("tense", "present")
                    right_tense = right_verb.features.get("tense", "present")

                    if left_mood != right_mood or left_tense != right_tense:
                        violations.append((token, left_verb, right_verb))

        parse_result.rule_checks[RuleID.RULE_34.value] = len(violations) == 0

        for conj_token, left_verb, right_verb in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_34,
                    message=f"Conjunction {conj_token.text} connects verbs that should have like moods and tenses",
                    span=Span(left_verb.start, right_verb.end),
                )
            )

    def _check_rule_35(self, parse_result: ParseResult) -> None:
        """RULE 35: A noun or pronoun following the conjunction than, as, or but, is nominative to a verb, or governed by a verb or preposition, expressed or understood."""
        violations = []

        comparison_conjunctions = {"than", "as", "but"}

        for i, token in enumerate(parse_result.tokens):
            if (
                token.pos == PartOfSpeech.CONJUNCTION
                and token.text.lower() in comparison_conjunctions
            ):
                # Find noun/pronoun after conjunction
                following_token = None
                for j in range(i + 1, len(parse_result.tokens)):
                    if parse_result.tokens[j].pos in {
                        PartOfSpeech.NOUN,
                        PartOfSpeech.PRONOUN,
                    }:
                        following_token = parse_result.tokens[j]
                        break

                if following_token:
                    # Check if it's nominative to a verb or governed by verb/preposition
                    is_nominative = False
                    is_governed = False

                    # Look for verb after the noun/pronoun
                    for j in range(i + 2, len(parse_result.tokens)):
                        if parse_result.tokens[j].pos == PartOfSpeech.VERB:
                            is_nominative = True
                            break

                    # Look for governing verb or preposition before
                    for j in range(i - 1, -1, -1):
                        if parse_result.tokens[j].pos in {
                            PartOfSpeech.VERB,
                            PartOfSpeech.PREPOSITION,
                        }:
                            is_governed = True
                            break

                    if not is_nominative and not is_governed:
                        violations.append((token, following_token))

        parse_result.rule_checks[RuleID.RULE_35.value] = len(violations) == 0

        for conj_token, noun_token in violations:
            parse_result.flags.append(
                Flag(
                    rule=RuleID.RULE_35,
                    message=f"Noun/pronoun {noun_token.text} after {conj_token.text} should be nominative to verb or governed by verb/preposition",
                    span=Span(conj_token.start, noun_token.end),
                )
            )
