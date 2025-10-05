"""Example usage of the English Grammar Parser.
Demonstrates various features and use cases.
"""

from kirkham.parser import KirkhamParser, PartOfSpeech


def example_basic_parsing():
    """Demonstrate basic parsing functionality."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Parsing")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        "The dog barks loudly.",
        "Children play in the park.",
        "She reads a book every day.",
    ]

    for sentence in sentences:
        print(f"\nSentence: {sentence}")
        result = parser.parse(sentence)

        if result.subject:
            print(f"  Subject: {result.subject.text}")
        if result.verb_phrase:
            print(f"  Verb: {result.verb_phrase.text}")
        if result.object_phrase:
            print(f"  Object: {result.object_phrase.text}")
        if result.voice:
            print(f"  Voice: {result.voice.value}")


def example_grammar_checking():
    """Demonstrate grammar rule validation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Grammar Rule Checking")
    print("=" * 70)

    parser = KirkhamParser()

    # Correct sentence
    print("\n1. Grammatically correct sentence:")
    result = parser.parse("The teacher explains the lesson clearly.")
    print("   Sentence: The teacher explains the lesson clearly.")
    print(f"   All rules passed: {all(result.rule_checks.values())}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")

    # Sentence with potential issues
    print("\n2. Sentence with warnings:")
    result = parser.parse("Running quickly.")
    print("   Sentence: Running quickly.")
    print(f"   Errors: {result.errors}")
    print(f"   Warnings: {result.warnings}")


def example_part_of_speech_analysis():
    """Demonstrate detailed part-of-speech analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Part-of-Speech Analysis")
    print("=" * 70)

    parser = KirkhamParser()

    sentence = "The beautiful red flower blooms gracefully in springtime."
    print(f"\nSentence: {sentence}\n")

    result = parser.parse(sentence)

    # Group tokens by part of speech
    pos_groups = {}
    for token in result.tokens:
        if token.pos != PartOfSpeech.PUNCTUATION:
            pos_name = token.pos.value
            if pos_name not in pos_groups:
                pos_groups[pos_name] = []
            pos_groups[pos_name].append(token.text)

    print("Words grouped by part of speech:")
    for pos, words in sorted(pos_groups.items()):
        print(f"  {pos.capitalize()}: {', '.join(words)}")


def example_possessive_analysis():
    """Demonstrate possessive construction analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Possessive Construction Analysis")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        "Mary's cat is sleeping.",
        "The student's homework was excellent.",
        "My brother's friend visits often.",
    ]

    for sentence in sentences:
        print(f"\nSentence: {sentence}")
        result = parser.parse(sentence)

        # Find possessive tokens
        possessives = [
            t for t in result.tokens if t.case and t.case.value == "possessive"
        ]

        if possessives:
            for poss in possessives:
                print(f"  Possessive: '{poss.text}' ({poss.pos.value})")

        # Check if RULE 12 passed
        if "rule_12_possessive_governed" in result.rule_checks:
            print("  RULE 12 (possessive governance): PASS")


def example_voice_detection():
    """Demonstrate active/passive voice detection."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Voice Detection")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        ("The cat chased the mouse.", "Active"),
        ("The mouse was chased by the cat.", "Passive"),
        ("The sun shines brightly.", "Neuter"),
        ("He writes novels.", "Active"),
        ("The letter was written yesterday.", "Passive"),
    ]

    print("\nVoice detection results:")
    for sentence, expected_voice in sentences:
        result = parser.parse(sentence)
        detected = result.voice.value if result.voice else "unknown"
        status = "✓" if detected.lower() in expected_voice.lower() else "?"
        print(f"{status} {sentence}")
        print(f"    Expected: {expected_voice}, Detected: {detected.capitalize()}")


def example_error_detection():
    """Demonstrate error and warning detection."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Error and Warning Detection")
    print("=" * 70)

    parser = KirkhamParser()

    # Various test cases
    test_cases = [
        "The birds sings.",  # Agreement error (should be caught)
        "She writes.",  # Transitive verb without object (warning)
        "To the store.",  # No subject or verb
        "Beautiful day!",  # No verb
    ]

    for sentence in test_cases:
        print(f"\nSentence: {sentence}")
        result = parser.parse(sentence)

        if result.errors:
            print("  Errors:")
            for error in result.errors:
                print(f"    - {error}")

        if result.warnings:
            print("  Warnings:")
            for warning in result.warnings:
                print(f"    - {warning}")

        if not result.errors and not result.warnings:
            print("  No errors or warnings detected")


def example_complex_sentences():
    """Demonstrate parsing of more complex sentences."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Complex Sentences")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        "The old man walks slowly through the beautiful garden.",
        "My sister's intelligent friend studies computer science diligently.",
        "The magnificent ancient temple stands majestically on the hill.",
    ]

    for sentence in sentences:
        print(f"\n{sentence}")
        print(parser.parse_and_display(sentence))


def example_pronoun_analysis():
    """Demonstrate pronoun handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Pronoun Analysis")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        "I am happy.",
        "You are kind.",
        "He writes well.",
        "She sings beautifully.",
        "We work together.",
        "They play outside.",
    ]

    print("\nPronoun-verb agreement:")
    for sentence in sentences:
        result = parser.parse(sentence)
        if result.subject:
            subject_token = result.subject.head_token
            if subject_token.person:
                print(f"  {sentence}")
                print(f"    Pronoun: {subject_token.text}")
                print(f"    Person: {subject_token.person.value}")
                print(f"    Number: {subject_token.number.value}")
                agreement = result.rule_checks.get("rule_4_verb_agreement", False)
                print(f"    Agreement: {'✓ PASS' if agreement else '✗ FAIL'}")


def example_custom_analysis():
    """Demonstrate custom analysis of parse results."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Custom Analysis")
    print("=" * 70)

    parser = KirkhamParser()

    sentence = "The wise old professor teaches brilliant young students passionately."
    print(f"\nSentence: {sentence}\n")

    result = parser.parse(sentence)

    # Count different types of words
    adjective_count = sum(1 for t in result.tokens if t.pos == PartOfSpeech.ADJECTIVE)
    noun_count = sum(1 for t in result.tokens if t.pos == PartOfSpeech.NOUN)
    verb_count = sum(1 for t in result.tokens if t.pos == PartOfSpeech.VERB)
    adverb_count = sum(1 for t in result.tokens if t.pos == PartOfSpeech.ADVERB)

    print("Word count analysis:")
    print(f"  Adjectives: {adjective_count}")
    print(f"  Nouns: {noun_count}")
    print(f"  Verbs: {verb_count}")
    print(f"  Adverbs: {adverb_count}")

    # Find all modifiers
    print("\nAdjectives modifying nouns:")
    for i, token in enumerate(result.tokens):
        if token.pos == PartOfSpeech.ADJECTIVE:
            # Look for following noun
            for j in range(i + 1, len(result.tokens)):
                if result.tokens[j].pos == PartOfSpeech.NOUN:
                    print(f"  '{token.text}' modifies '{result.tokens[j].text}'")
                    break
                if result.tokens[j].pos not in {
                    PartOfSpeech.ADJECTIVE,
                    PartOfSpeech.ARTICLE,
                }:
                    break


def example_sentence_comparison():
    """Compare parsing of similar sentences."""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Sentence Comparison")
    print("=" * 70)

    parser = KirkhamParser()

    pairs = [
        ("The dog bites.", "The dog is bitten."),
        ("She writes a letter.", "A letter is written by her."),
    ]

    for sentence1, sentence2 in pairs:
        print("\nComparing sentences:")
        print(f"  1: {sentence1}")
        print(f"  2: {sentence2}")

        result1 = parser.parse(sentence1)
        result2 = parser.parse(sentence2)

        voice1 = result1.voice.value if result1.voice else "unknown"
        voice2 = result2.voice.value if result2.voice else "unknown"

        print(f"\n  Sentence 1 - Voice: {voice1}")
        if result1.subject:
            print(f"             Subject: {result1.subject.text}")
        if result1.verb_phrase:
            print(f"             Verb: {result1.verb_phrase.text}")
        if result1.object_phrase:
            print(f"             Object: {result1.object_phrase.text}")

        print(f"\n  Sentence 2 - Voice: {voice2}")
        if result2.subject:
            print(f"             Subject: {result2.subject.text}")
        if result2.verb_phrase:
            print(f"             Verb: {result2.verb_phrase.text}")
        if result2.object_phrase:
            print(f"             Object: {result2.object_phrase.text}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print(" ENGLISH GRAMMAR PARSER - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    examples = [
        ("Basic Parsing", example_basic_parsing),
        ("Grammar Checking", example_grammar_checking),
        ("Part-of-Speech Analysis", example_part_of_speech_analysis),
        ("Possessive Analysis", example_possessive_analysis),
        ("Voice Detection", example_voice_detection),
        ("Error Detection", example_error_detection),
        ("Pronoun Analysis", example_pronoun_analysis),
        ("Custom Analysis", example_custom_analysis),
        ("Sentence Comparison", example_sentence_comparison),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")

    print("\n" + "=" * 70)
    print(" ALL EXAMPLES COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
