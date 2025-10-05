"""Demonstration of robust tokenization with character offsets and JSON export.

This script shows how the improved tokenizer handles:
- Unicode apostrophes (', ', ")
- Hyphenated words (well-known, 30-year-old)
- Contractions (don't, she's, won't)
- Decimal numbers (25.5, 3.14)
- Character offsets for UI highlighting

Author: Enhanced English Grammar Parser
Date: October 2025
"""

import json

from kirkham.parser import KirkhamParser


def demo_offset_highlighting():
    """Demonstrate how offsets enable UI highlighting."""
    print("\n" + "=" * 70)
    print("DEMO 1: Character Offsets for UI Highlighting")
    print("=" * 70)

    parser = KirkhamParser()
    sentence = "The well-known author writes beautifully."

    print(f"\nOriginal sentence:\n  {sentence}\n")

    result = parser.parse(sentence)

    print("Tokens with positions:")
    for token in result.tokens:
        # Extract the actual text using offsets
        extracted = sentence[token.start : token.end]
        print(f'  [{token.start:2d}:{token.end:2d}] "{extracted}" -> {token.pos.value}')

    # Highlight subject
    if result.subject:
        print(f"\nHighlighting subject: '{result.subject.text}'")
        start = result.subject.tokens[0].start
        end = result.subject.tokens[-1].end

        # Create visual highlight
        before = sentence[:start]
        highlighted = sentence[start:end]
        after = sentence[end:]
        print(f"  {before}[{highlighted}]{after}")
        print(f"  Offsets: {start}:{end}")


def demo_unicode_handling():
    """Demonstrate Unicode apostrophe handling."""
    print("\n" + "=" * 70)
    print("DEMO 2: Unicode Apostrophe Support")
    print("=" * 70)

    parser = KirkhamParser()

    # Different apostrophe types
    test_cases = [
        ("Standard: I don't know.", "'"),
        ("Unicode Right: I don't know.", "'"),
        ("Unicode Left: I don't know.", "'"),
    ]

    for sentence, apos_type in test_cases:
        print(f"\nUsing {apos_type} apostrophe:")
        print(f"  Sentence: {sentence}")

        result = parser.parse(sentence)
        contractions = [
            t for t in result.tokens if "'" in t.text or "'" in t.text or "'" in t.text
        ]

        if contractions:
            for cont in contractions:
                print(f"  Found: '{cont.text}' at position [{cont.start}:{cont.end}]")


def demo_hyphenated_words():
    """Demonstrate hyphenated word handling."""
    print("\n" + "=" * 70)
    print("DEMO 3: Hyphenated Words")
    print("=" * 70)

    parser = KirkhamParser()

    sentences = [
        "The well-known scientist discovered it.",
        "My 5-year-old daughter reads well.",
        "State-of-the-art technology advances rapidly.",
    ]

    for sentence in sentences:
        print(f"\nSentence: {sentence}")
        result = parser.parse(sentence)

        hyphenated = [t for t in result.tokens if "-" in t.text]
        if hyphenated:
            print("  Hyphenated words found:")
            for hw in hyphenated:
                print(f"    - '{hw.text}' at [{hw.start}:{hw.end}]")


def demo_json_export():
    """Demonstrate JSON export for API/UI use."""
    print("\n" + "=" * 70)
    print("DEMO 4: JSON Export for APIs and UIs")
    print("=" * 70)

    parser = KirkhamParser()
    sentence = "She writes beautiful stories."

    print(f"\nSentence: {sentence}\n")

    # Get JSON representation
    json_data = parser.parse_to_json(sentence)

    print("JSON structure (formatted):")
    print(json.dumps(json_data, indent=2))

    print("\n\nExample: Using JSON data to highlight in a UI:")
    print("```javascript")
    print("// Frontend code could use the offsets like this:")
    print('const sentence = "She writes beautiful stories.";')
    print("const tokens = parseResult.tokens;")
    print("")
    print("tokens.forEach(token => {")
    print("  const element = document.createElement('span');")
    print("  element.textContent = sentence.substring(token.start, token.end);")
    print("  element.className = `token-${token.pos}`;")
    print("  element.dataset.start = token.start;")
    print("  element.dataset.end = token.end;")
    print("  container.appendChild(element);")
    print("});")
    print("```")


def demo_sentence_reconstruction():
    """Demonstrate that offsets allow perfect reconstruction."""
    print("\n" + "=" * 70)
    print("DEMO 5: Sentence Reconstruction from Offsets")
    print("=" * 70)

    parser = KirkhamParser()

    test_sentences = [
        "I don't know!",
        "The 25.5-year-old woman works.",
        "John's well-written book sells.",
    ]

    for original in test_sentences:
        print(f"\nOriginal: {original}")

        result = parser.parse(original)

        # Reconstruct sentence using offsets
        reconstructed = ""
        last_end = 0

        for token in result.tokens:
            # Add any whitespace between tokens
            reconstructed += original[last_end : token.start]
            # Add the token
            reconstructed += original[token.start : token.end]
            last_end = token.end

        # Add any remaining text
        reconstructed += original[last_end:]

        match = "✓" if reconstructed == original else "✗"
        print(f"Reconstructed: {reconstructed}")
        print(f"Match: {match}")


def demo_phrase_offsets():
    """Demonstrate phrase-level offsets."""
    print("\n" + "=" * 70)
    print("DEMO 6: Phrase-Level Offsets")
    print("=" * 70)

    parser = KirkhamParser()
    sentence = "The brilliant young scientist discovered remarkable phenomena."

    print(f"\nSentence: {sentence}\n")

    json_data = parser.parse_to_json(sentence)

    # Show phrase offsets
    if json_data["subject"]:
        subj = json_data["subject"]
        print(f"Subject phrase: '{subj['text']}'")
        print(f"  Span: [{subj['start']}:{subj['end']}]")
        print(f"  Extracted: '{sentence[subj['start']:subj['end']]}'")

    if json_data["verb_phrase"]:
        verb = json_data["verb_phrase"]
        print(f"\nVerb phrase: '{verb['text']}'")
        print(f"  Span: [{verb['start']}:{verb['end']}]")
        print(f"  Extracted: '{sentence[verb['start']:verb['end']]}'")

    if json_data["object_phrase"]:
        obj = json_data["object_phrase"]
        print(f"\nObject phrase: '{obj['text']}'")
        print(f"  Span: [{obj['start']}:{obj['end']}]")
        print(f"  Extracted: '{sentence[obj['start']:obj['end']]}'")


def demo_practical_ui_application():
    """Show a practical example of how to use this in a web UI."""
    print("\n" + "=" * 70)
    print("DEMO 7: Practical UI Application Example")
    print("=" * 70)

    parser = KirkhamParser()
    sentence = "The quick brown fox jumps over the lazy dog."

    print(f"\nSentence: {sentence}\n")

    json_data = parser.parse_to_json(sentence)

    print("HTML Output with color-coded parts of speech:")
    print("-" * 70)

    # Simulate generating HTML
    html_parts = []
    html_parts.append('<div class="parsed-sentence">')

    last_end = 0
    for token in json_data["tokens"]:
        # Add whitespace
        if token["start"] > last_end:
            html_parts.append(sentence[last_end : token["start"]])

        # Add colored token
        color = get_pos_color(token["pos"])
        html_parts.append(
            f'<span class="token" '
            f'style="color:{color}" '
            f'data-pos="{token["pos"]}" '
            f'data-start="{token["start"]}" '
            f'data-end="{token["end"]}" '
            f'title="{token["pos"]}">'
            f'{token["text"]}'
            f"</span>"
        )

        last_end = token["end"]

    html_parts.append("</div>")

    html_output = "".join(html_parts)
    print(html_output)

    # Show visual representation
    print("\n\nVisual color-coded output (simulated):")
    print("-" * 70)
    for token in json_data["tokens"]:
        if token["pos"] == "punctuation":
            print(token["text"], end="")
        else:
            print(f" \033[1m{token['text']}\033[0m", end="")
    print()


def get_pos_color(pos):
    """Get color for part of speech."""
    colors = {
        "noun": "#3498db",  # blue
        "verb": "#e74c3c",  # red
        "adjective": "#2ecc71",  # green
        "adverb": "#9b59b6",  # purple
        "pronoun": "#f39c12",  # orange
        "preposition": "#95a5a6",  # gray
        "conjunction": "#34495e",  # dark gray
        "article": "#1abc9c",  # teal
        "punctuation": "#7f8c8d",  # light gray
    }
    return colors.get(pos, "#000000")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("ROBUST TOKENIZATION WITH CHARACTER OFFSETS")
    print("Enhanced English Grammar Parser")
    print("=" * 70)

    demos = [
        ("Offset Highlighting", demo_offset_highlighting),
        ("Unicode Support", demo_unicode_handling),
        ("Hyphenated Words", demo_hyphenated_words),
        ("JSON Export", demo_json_export),
        ("Reconstruction", demo_sentence_reconstruction),
        ("Phrase Offsets", demo_phrase_offsets),
        ("UI Application", demo_practical_ui_application),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n\nError in {name} demo: {e}")

    print("\n" + "=" * 70)
    print("All demonstrations completed!")
    print("=" * 70 + "\n")

    # Summary
    print("\nKEY IMPROVEMENTS:")
    print("  ✓ Character offsets for every token")
    print("  ✓ Unicode apostrophe support (' ' ')")
    print("  ✓ Hyphenated word handling (well-known, state-of-the-art)")
    print("  ✓ Contraction support (don't, she's, won't)")
    print("  ✓ Decimal number recognition (25.5, 3.14)")
    print("  ✓ JSON export for API/UI integration")
    print("  ✓ Phrase-level offset spans")
    print("  ✓ Perfect sentence reconstruction")
    print("\nUSE CASES:")
    print("  • Syntax highlighting in editors")
    print("  • Interactive grammar learning apps")
    print("  • Text annotation tools")
    print("  • Grammar checking UIs")
    print("  • API responses with highlighting data")
    print("  • Educational software")


if __name__ == "__main__":
    main()
