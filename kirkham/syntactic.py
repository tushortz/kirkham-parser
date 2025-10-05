"""Syntactic parser for the Kirkham Grammar Parser.

This module performs syntactic analysis of sentences, implementing parsing
based on Kirkham's grammatical rules.
"""

from __future__ import annotations

from .classifier import PartOfSpeechClassifier
from .lexicon import DEFAULT_LEXICON, Lexicon
from .models import DEFAULT_CONFIG, ParserConfig, ParseResult, Phrase, Token
from .types import Case, PartOfSpeech, SentenceType, Tense, Voice
from .utils import TextUtils


class SyntacticParser:
    """Performs syntactic analysis of sentences.
    Implements parsing based on Kirkham's grammatical rules.
    """

    # Adverb-like words that commonly intensify adjectives
    ADVERB_LIKE = frozenset(
        {
            "very",
            "quite",
            "rather",
            "too",
            "so",
            "more",
            "most",
            "less",
            "least",
            "really",
            "extremely",
            "fairly",
            "pretty",
            "highly",
            "incredibly",
            "particularly",
        }
    )

    def __init__(
        self, config: ParserConfig | None = None, lexicon: Lexicon | None = None
    ) -> None:
        """Initialize the parser with optional configuration and lexicon.

        Args:
            config: Parser configuration. If None, uses DEFAULT_CONFIG.
            lexicon: Custom lexicon. If None, uses DEFAULT_LEXICON.

        """
        self.config = config or DEFAULT_CONFIG
        self.lex = lexicon or DEFAULT_LEXICON
        self.classifier = PartOfSpeechClassifier(self.lex)
        # Import validator here to avoid circular imports
        from .validator import GrammarRuleValidator

        self.validator = GrammarRuleValidator(self.config)

    def _looks_adverb(self, token: Token) -> bool:
        """Check if token looks like an adverb (intensifier or modifier).

        Handles common adverbial intensifiers that precede adjectives
        like "very good", "quite nice", "rather old".

        Args:
            token: Token to check

        Returns:
            True if token appears to be an adverb

        """
        # Check if it's in the adverb-like set
        if token.lemma in self.ADVERB_LIKE:
            return True

        # Check if explicitly classified as adverb
        if token.pos == PartOfSpeech.ADVERB:
            return True

        # Check for -ly ending (common adverb suffix)
        return bool(token.lemma.endswith("ly"))

    def _detect_sentence_type(self, tokens: list[Token]) -> SentenceType:
        """Detect the type of sentence based on structure and punctuation.

        Handles:
        - Questions (interrogatives): WH-words, question marks, inverted subjects
        - Commands (imperatives): Start with base verb, often no subject
        - Exclamations: Exclamation marks, intensifiers
        - Statements (declaratives): Default

        Args:
            tokens: List of tokens in the sentence

        Returns:
            SentenceType enum value

        Examples:
            "What time is it?" → INTERROGATIVE
            "Sit down!" → IMPERATIVE
            "What a beautiful day!" → EXCLAMATORY
            "The cat sat." → DECLARATIVE

        """
        if not tokens:
            return SentenceType.DECLARATIVE

        # Check punctuation marks
        last_token = tokens[-1]
        if last_token.text == "?":
            return SentenceType.INTERROGATIVE
        if last_token.text == "!":
            # Could be imperative or exclamatory
            # Check for exclamatory patterns: "What a...", "How..."
            if tokens[0].lemma in {"what", "how"} and len(tokens) > 2:
                if tokens[1].pos in {PartOfSpeech.ARTICLE, PartOfSpeech.ADJECTIVE}:
                    return SentenceType.EXCLAMATORY
            return SentenceType.IMPERATIVE

        # Check for WH-words at the start (questions)
        if tokens[0].lemma in {
            "who",
            "what",
            "where",
            "when",
            "why",
            "how",
            "which",
            "whom",
            "whose",
        }:
            return SentenceType.INTERROGATIVE

        # Check for inverted auxiliary (questions): "Do you...", "Is he...", "Can they..."
        if len(tokens) >= 2:
            first = tokens[0]
            second = tokens[1]
            if (
                first.pos == PartOfSpeech.VERB
                and first.lemma
                in Lexicon.AUXILIARY_BE
                | Lexicon.AUXILIARY_HAVE
                | Lexicon.AUXILIARY_DO
                | Lexicon.MODAL_VERBS
            ) and second.pos == PartOfSpeech.PRONOUN:
                return SentenceType.INTERROGATIVE

        # Check for imperatives: start with base verb, no subject before it
        if tokens[0].pos == PartOfSpeech.VERB:
            if self._is_base_verb_shape(tokens[0].lemma):
                # Check if there's a subject pronoun before verb (if not, likely imperative)
                # "You go" (declarative) vs "Go!" (imperative)
                return SentenceType.IMPERATIVE

        # Default to declarative
        return SentenceType.DECLARATIVE

    def _determine_tense(self, verb_phrase: Phrase) -> Tense:
        """Determine the tense of a verb phrase.

        Analyzes auxiliary verbs and main verb forms to determine tense.

        Args:
            verb_phrase: The verb phrase to analyze

        Returns:
            Tense enum value

        Examples:
            "will go" → FUTURE
            "has gone" → PRESENT_PERFECT
            "had gone" → PAST_PERFECT
            "will have gone" → FUTURE_PERFECT
            "goes" → PRESENT
            "went" → PAST

        """
        if not verb_phrase or not verb_phrase.tokens:
            return Tense.PRESENT

        lemmas = [t.lemma for t in verb_phrase.tokens]
        tokens = verb_phrase.tokens

        # Future: will/shall + base
        if any(m in lemmas for m in {"will", "shall"}):
            # Check for perfect: will have + past participle
            if "have" in lemmas or "has" in lemmas:
                return Tense.FUTURE_PERFECT
            return Tense.FUTURE

        # Perfect aspects (have/has/had + past participle)
        if any(aux in lemmas for aux in {"have", "has", "had"}):
            # Check if followed by past participle
            has_participle = any(t.features.get("participle") == "past" for t in tokens)
            if has_participle:
                if "had" in lemmas:
                    return Tense.PAST_PERFECT
                return Tense.PRESENT_PERFECT

        # Simple tenses: check main verb form
        main_verb = tokens[-1]  # Last verb is typically the main verb

        # Check for past tense markers
        if main_verb.lemma.endswith("ed") or TextUtils.is_past_participle(
            main_verb.lemma
        ):
            # Could be past or past participle (but not in perfect context)
            # Check for irregular past forms
            irregular_past = {
                "went",
                "came",
                "saw",
                "made",
                "took",
                "got",
                "gave",
                "found",
                "knew",
                "thought",
                "told",
                "became",
                "left",
                "felt",
                "brought",
                "began",
                "ran",
                "held",
                "heard",
                "kept",
                "meant",
                "met",
                "paid",
                "read",
                "said",
                "sat",
                "sent",
                "stood",
                "understood",
                "wrote",
            }
            if main_verb.lemma in irregular_past:
                return Tense.PAST

            # Check for "was/were" (past BE)
            if main_verb.lemma in {"was", "were"}:
                return Tense.PAST

            return Tense.PAST

        # Present tense (3rd person singular -s or base form with present context)
        if main_verb.features.get("3sg") or main_verb.text.endswith("s"):
            return Tense.PRESENT

        # Check for present BE forms
        if main_verb.lemma in {"am", "is", "are"}:
            return Tense.PRESENT

        # Default to present for base forms
        return Tense.PRESENT

    def parse(self, sentence: str) -> ParseResult:
        """Parse a sentence and return complete analysis.

        Args:
            sentence: Input sentence string

        Returns:
            ParseResult object with complete analysis

        """
        # Tokenize and classify (with character offsets)
        word_tokens = TextUtils.tokenize(sentence)
        tokens = [
            self.classifier.classify(word, start, end)
            for word, start, end in word_tokens
        ]

        # Store original sentence in result
        result = ParseResult(tokens=tokens)
        result.notes.append(
            f"Sentence length: {len(sentence)} chars, {len(tokens)} tokens"
        )

        # Detect sentence type (if enabled)
        if self.config.detect_sentence_type:
            result.sentence_type = self._detect_sentence_type(tokens)

        # Find verb phrase
        verb_phrase = self._find_verb_phrase(tokens)
        result.verb_phrase = verb_phrase

        if not verb_phrase:
            result.warnings.append("No finite verb found in sentence")
            return result

        # Find subject
        subject = self._find_subject(tokens, verb_phrase)
        result.subject = subject

        # Find object
        object_phrase = self._find_object(tokens, verb_phrase)
        result.object_phrase = object_phrase

        # Determine voice (pass tokens for look-ahead)
        result.voice = self._determine_voice(tokens, verb_phrase, object_phrase)

        # Determine tense (if enabled)
        if self.config.detect_tense and verb_phrase:
            result.tense = self._determine_tense(verb_phrase)

        # Validate grammar rules
        self.validator.validate(result)

        return result

    def _find_verb_phrase(self, tokens: list[Token]) -> Phrase | None:
        """Find the main verb phrase in the sentence.
        Implements identification of verb groups including auxiliaries.
        """
        for i, token in enumerate(tokens):
            if token.pos == PartOfSpeech.VERB:
                # Extend through auxiliary chain
                j = i
                while j + 1 < len(tokens) and tokens[j + 1].pos == PartOfSpeech.VERB:
                    j += 1

                # Create verb phrase
                verb_tokens = tokens[i : j + 1]
                return Phrase(
                    tokens=verb_tokens,
                    phrase_type="VP",
                    head_index=j - i,  # Last verb is head
                )

        return None

    def _find_subject(self, tokens: list[Token], verb_phrase: Phrase) -> Phrase | None:
        """Find the subject noun phrase before the verb.
        Implements RULE 3: The nominative case governs the verb.
        """
        verb_start_idx = tokens.index(verb_phrase.tokens[0])

        # Look backwards from verb for noun/pronoun
        for i in range(verb_start_idx - 1, -1, -1):
            if tokens[i].pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                # Found potential subject, extend to include determiners/adjectives/adverbs
                start_idx = i

                # Include preceding articles, adjectives, possessives, and adverbs
                # Handles: "the very good book", "a rather old man", "John's brother's book"
                # Stop at prepositions to avoid crossing PP boundaries
                j = i - 1
                while j >= 0:
                    token = tokens[j]

                    # Stop at prepositions (don't cross PP boundary)
                    if token.pos == PartOfSpeech.PREPOSITION:
                        break

                    # Include possessives, articles, adjectives, adverbs
                    if (
                        token.case == Case.POSSESSIVE
                        or token.pos in {PartOfSpeech.ARTICLE, PartOfSpeech.ADJECTIVE}
                        or self._looks_adverb(token)
                    ):
                        start_idx = j
                        j -= 1
                    # Stop at anything else
                    else:
                        break

                subject_tokens = tokens[start_idx : i + 1]
                return Phrase(
                    tokens=subject_tokens, phrase_type="NP", head_index=i - start_idx
                )

        return None

    def _find_object(self, tokens: list[Token], verb_phrase: Phrase) -> Phrase | None:
        """Find the object noun phrase after the verb.
        Implements RULE 20: Active-transitive verbs govern the objective case.
        """
        verb_end_idx = tokens.index(verb_phrase.tokens[-1])

        # Look forward from verb for noun/pronoun
        start_idx = None
        end_idx = None

        i = verb_end_idx + 1
        while i < len(tokens):
            token = tokens[i]

            # Stop at punctuation or conjunction
            if token.pos in {PartOfSpeech.PUNCTUATION, PartOfSpeech.CONJUNCTION}:
                break

            # Stop at preposition if we haven't started collecting object
            if token.pos == PartOfSpeech.PREPOSITION and start_idx is None:
                break

            # Collect articles, adjectives, adverbs, nouns, pronouns
            # Handles: "a very good book", "the quite old man"
            if token.pos in {
                PartOfSpeech.ARTICLE,
                PartOfSpeech.ADJECTIVE,
                PartOfSpeech.NOUN,
                PartOfSpeech.PRONOUN,
            } or self._looks_adverb(token):
                if start_idx is None:
                    start_idx = i
                end_idx = i
            elif start_idx is not None:
                # Found end of object phrase
                break

            i += 1

        if start_idx is not None and end_idx is not None:
            object_tokens = tokens[start_idx : end_idx + 1]
            # Find head (last noun/pronoun)
            head_idx = 0
            for j, tok in enumerate(object_tokens):
                if tok.pos in {PartOfSpeech.NOUN, PartOfSpeech.PRONOUN}:
                    head_idx = j

            return Phrase(tokens=object_tokens, phrase_type="NP", head_index=head_idx)

        return None

    def _determine_voice(
        self, tokens: list[Token], verb_phrase: Phrase, object_phrase: Phrase | None
    ) -> Voice:
        """Determine if the verb phrase is active, passive, or neuter voice.

        Handles:
        - Standard be-passive: "was written"
        - Get-passive: "got caught", "gets broken" (if enabled in config)
        - Been + VBN: "has been written"
        - Look-ahead for past participles just outside VP

        Args:
            tokens: All tokens in the sentence
            verb_phrase: The identified verb phrase
            object_phrase: The identified object phrase (if any)

        Returns:
            Voice.PASSIVE, Voice.ACTIVE, or Voice.NEUTER

        """
        if not verb_phrase:
            return Voice.NEUTER

        # Helper: check if token is past participle
        def is_vbn(tok: Token) -> bool:
            return tok.features.get("participle") == "past"

        # Determine which auxiliaries indicate passive
        aux_set = {"be"}
        if self.config.detect_get_passive:
            aux_set.add("get")

        # Check for passive auxiliary in VP
        has_aux = any(
            t.features.get("auxiliary") in aux_set for t in verb_phrase.tokens
        )

        # Check for past participle in VP
        has_vbn_in_vp = any(is_vbn(t) for t in verb_phrase.tokens)

        # Lookahead 2 tokens in case VBN is just outside VP
        vp_last_idx = tokens.index(verb_phrase.tokens[-1]) if verb_phrase.tokens else -1
        if vp_last_idx >= 0:
            lookahead = tokens[vp_last_idx + 1 : vp_last_idx + 3]
            vbn_lookahead = any(is_vbn(t) for t in lookahead)
        else:
            vbn_lookahead = False

        # Passive: has auxiliary (be/get) + past participle
        if has_aux and (has_vbn_in_vp or vbn_lookahead):
            return Voice.PASSIVE

        # Active: has object or explicitly transitive verb
        if object_phrase or any(
            t.features.get("transitive") for t in verb_phrase.tokens
        ):
            return Voice.ACTIVE

        return Voice.NEUTER

    def _is_base_verb_shape(self, lemma: str) -> bool:
        """Check if a lemma has a base verb shape (infinitive form).

        A base verb should:
        - Not be an auxiliary (BE, HAVE, DO, GET, modals)
        - Not end in -s (3rd person singular)
        - Not end in -ed (past tense)
        - Not end in -ing (present participle)
        - Not be irregular past tense (went, saw, etc.)

        Returns:
            True if lemma appears to be a base/infinitive lexical verb

        """
        # Reject auxiliaries - they don't function as infinitive heads
        # "to be", "to have", "to do", etc. are special cases
        if (
            lemma in Lexicon.AUXILIARY_BE
            or lemma in Lexicon.AUXILIARY_HAVE
            or lemma in Lexicon.AUXILIARY_DO
            or lemma in Lexicon.AUXILIARY_GET
            or lemma in Lexicon.MODAL_VERBS
        ):
            return False

        # Common irregular past tense forms (NOT base forms)
        irregular_past_tense = {
            "went",
            "came",
            "saw",
            "made",
            "took",
            "got",
            "gave",
            "found",
            "knew",
            "thought",
            "told",
            "became",
            "left",
            "felt",
            "brought",
            "began",
            "ran",
            "held",
            "heard",
            "kept",
            "meant",
            "met",
            "paid",
            "read",
            "said",
            "sat",
            "sent",
            "stood",
            "understood",
            "wrote",
            "ate",
            "fell",
            "grew",
            "threw",
            "wore",
            "won",
            "spoke",
            "broke",
            "chose",
            "drove",
            "rode",
            "sold",
            "taught",
            "caught",
            "fought",
            "bought",
            "sought",
        }

        # Reject irregular past tense forms
        if lemma in irregular_past_tense:
            return False

        # Reject -ing forms (present participle/gerund)
        if lemma.endswith("ing"):
            return False

        # Reject -ed forms (past tense/participle)
        if lemma.endswith("ed"):
            # Exception: short words like "red", "bed" are not verbs
            if len(lemma) <= 3:
                return False
            return False

        # Reject -s forms (3rd person singular)
        # But allow exceptions like "pass", "class", "bus"
        if lemma.endswith("s") and not lemma.endswith(("ss", "us", "as", "is", "ness")):
            # Check if removing 's' or 'es' gives us a known base verb
            base = lemma[:-1]
            if (
                base in Lexicon.COMMON_TRANSITIVE_VERBS
                or base in Lexicon.COMMON_INTRANSITIVE_VERBS
            ):
                # This is likely a conjugated form (e.g., "walks" -> "walk")
                return False
            # Try removing 'es' for verbs like "goes" -> "go"
            if lemma.endswith("es"):
                base = lemma[:-2]
                if (
                    base in Lexicon.COMMON_TRANSITIVE_VERBS
                    or base in Lexicon.COMMON_INTRANSITIVE_VERBS
                ):
                    return False

        # Known base form lexical verbs (auxiliaries already rejected above)
        if (
            lemma in Lexicon.COMMON_TRANSITIVE_VERBS
            or lemma in Lexicon.COMMON_INTRANSITIVE_VERBS
        ):
            return True

        # For unknown words, assume they might be base form if they pass checks
        return True

    def _find_infinitives(self, tokens: list[Token]) -> list[tuple[int, int]]:
        """Find infinitive phrases (to + verb) in the token sequence.

        Uses safer detection to avoid treating "to" as infinitive marker
        when it's actually a preposition (e.g., "to school", "to him").

        Requirements for infinitive:
        1. "to" followed by a token
        2. Next token must be classified as VERB
        3. Next token must have base verb shape (not tensed)
        4. Not followed by noun/pronoun/adjective (those indicate prepositional use)

        Returns:
            List of (start_idx, end_idx) tuples for infinitive spans

        """
        spans = []

        for i, token in enumerate(tokens):
            # Check for "to"
            if token.lemma == "to" and token.pos == PartOfSpeech.PREPOSITION:
                j = i + 1

                # Check if there's a next token
                if j < len(tokens):
                    next_token = tokens[j]

                    # MUST be classified as VERB
                    if next_token.pos == PartOfSpeech.VERB:
                        # MUST have base verb shape (infinitive form)
                        if self._is_base_verb_shape(next_token.lemma):
                            # This is a valid infinitive: to + base verb
                            spans.append((i, j))

        return spans
