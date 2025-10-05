#!/usr/bin/env python3
"""Command-Line Interface for English Grammar Parser.

Provides a convenient CLI for parsing English sentences and analyzing grammar.

Usage:
    python grammar_cli.py "The cat sat on the mat."
    python grammar_cli.py --file input.txt --json
    python grammar_cli.py "She walks" --config strict
    python grammar_cli.py --file sentences.txt --check-only

Author: Based on Kirkham's Grammar
Date: 2025
"""
from __future__ import annotations

import argparse
import json
import sys

from kirkham.parser import KirkhamParser, ParserConfig, ParseResult


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="English Grammar Parser - Analyze English sentences based on Kirkham's Grammar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single sentence
  %(prog)s "The cat sat on the mat."

  # Parse from a file
  %(prog)s --file document.txt

  # Output JSON format
  %(prog)s "She walks quickly." --json

  # Use strict formal configuration
  %(prog)s "It is I." --config strict

  # Check for errors only
  %(prog)s "The cats runs." --check-only

  # Parse multiple sentences (one per line)
  %(prog)s --file sentences.txt --line-by-line

  # Show detailed analysis with offsets
  %(prog)s "The dog barked." --verbose --offsets
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "text", nargs="?", help="Text to parse (use quotes for sentences with spaces)"
    )
    input_group.add_argument(
        "-f", "--file", type=str, help="Path to file containing text to parse"
    )

    # Configuration options
    parser.add_argument(
        "-c",
        "--config",
        choices=["default", "strict", "permissive", "educational"],
        default="default",
        help="Parser configuration preset (default: default)",
    )

    # Output options
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output results in JSON format (default: human-readable)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed parse information (not compatible with --json)",
    )
    parser.add_argument(
        "-o",
        "--offsets",
        action="store_true",
        help="Show character offsets for tokens (only with --verbose)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only show grammar errors and warnings (no full parse)",
    )

    # File processing options
    parser.add_argument(
        "-l",
        "--line-by-line",
        action="store_true",
        help="Process file line-by-line (one sentence per line)",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)",
    )

    # Statistics options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics summary (for batch processing)",
    )

    args = parser.parse_args()

    # Validate argument combinations
    if args.offsets and not args.verbose:
        parser.error("--offsets requires --verbose")
    if args.json and args.verbose:
        parser.error("--json and --verbose are mutually exclusive")
    if args.line_by_line and not args.file:
        parser.error("--line-by-line requires --file")

    # Load parser configuration
    if args.config == "strict":
        cfg = ParserConfig.strict_formal()
    elif args.config == "permissive":
        cfg = ParserConfig.modern_permissive()
    elif args.config == "educational":
        cfg = ParserConfig.educational()
    else:
        cfg = ParserConfig()

    grammar_parser = KirkhamParser(cfg)

    try:
        # Load text
        if args.file:
            results = grammar_parser.parse_file(
                args.file, sentence_per_line=args.line_by_line, encoding=args.encoding
            )
        else:
            text = args.text
            # Check if it's multiple sentences
            if "." in text or "?" in text or "!" in text:
                results = grammar_parser.parse_many(text)
            else:
                results = [grammar_parser.parse(text)]

        # Output results
        if args.check_only:
            output_errors_only(results)
        elif args.json:
            output_json(results)
        elif args.verbose:
            output_verbose(results, args.offsets)
        else:
            output_summary(results)

        # Statistics
        if args.stats and len(results) > 1:
            output_statistics(results)

    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(
            f"Error: Cannot decode file '{args.file}' with encoding '{args.encoding}'",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def output_summary(results: list[ParseResult]) -> None:
    """Output concise summary of parse results."""
    for i, result in enumerate(results, 1):
        if len(results) > 1:
            print(f"\n{'='*70}")
            print(f"Sentence {i}:")
            print(f"{'='*70}")

        # Show basic parse
        text = " ".join(t.text for t in result.tokens)
        print(f"Text: {text}")

        if result.sentence_type:
            print(f"Type: {result.sentence_type.value}")

        if result.subject:
            print(f"Subject: {result.subject.text}")
        if result.verb_phrase:
            print(f"Verb: {result.verb_phrase.text}")
        if result.object_phrase:
            print(f"Object: {result.object_phrase.text}")
        if result.voice:
            print(f"Voice: {result.voice.value}")
        if result.tense:
            print(f"Tense: {result.tense.value}")

        # Show errors/warnings
        if result.flags:
            print("\nIssues:")
            for flag in result.flags:
                print(f"  • [{flag.rule.value}] {flag.message}")


def output_verbose(results: list[ParseResult], show_offsets: bool = False) -> None:
    """Output detailed parse information."""
    from kirkham.parser import OutputFormatter

    formatter = OutputFormatter()
    for i, result in enumerate(results, 1):
        if len(results) > 1:
            print(f"\n\n{'='*70}")
            print(f"SENTENCE {i}")
            print(f"{'='*70}")
        print(formatter.format_parse_result(result, show_offsets=show_offsets))


def output_json(results: list[ParseResult]) -> None:
    """Output results in JSON format."""
    if len(results) == 1:
        # Single result: output as object
        print(json.dumps(results[0].to_dict(), indent=2, sort_keys=True))
    else:
        # Multiple results: output as array
        print(json.dumps([r.to_dict() for r in results], indent=2, sort_keys=True))


def output_errors_only(results: list[ParseResult]) -> None:
    """Output only grammar errors and warnings."""
    total_errors = 0

    for i, result in enumerate(results, 1):
        if not result.flags:
            continue

        if len(results) > 1:
            text = " ".join(t.text for t in result.tokens)
            print(f"\nSentence {i}: {text}")
            print("-" * 70)

        for flag in result.flags:
            total_errors += 1
            if flag.span:
                print(
                    f"  [{flag.rule.value}] {flag.message} (at {flag.span.start}:{flag.span.end})"
                )
            else:
                print(f"  [{flag.rule.value}] {flag.message}")

    if total_errors == 0:
        print("✓ No grammar issues found!")
    else:
        print(f"\nTotal issues: {total_errors}")


def output_statistics(results: list[ParseResult]) -> None:
    """Output statistical summary of results."""
    print(f"\n{'='*70}")
    print("STATISTICS")
    print(f"{'='*70}")

    total = len(results)
    print(f"Total sentences: {total}")

    # Count by sentence type
    if any(r.sentence_type for r in results):
        from collections import Counter

        types = Counter(r.sentence_type.value for r in results if r.sentence_type)
        print("\nSentence types:")
        for stype, count in types.most_common():
            print(f"  {stype}: {count} ({count/total*100:.1f}%)")

    # Count by tense
    if any(r.tense for r in results):
        from collections import Counter

        tenses = Counter(r.tense.value for r in results if r.tense)
        print("\nTenses:")
        for tense, count in tenses.most_common():
            print(f"  {tense}: {count} ({count/total*100:.1f}%)")

    # Count by voice
    if any(r.voice for r in results):
        from collections import Counter

        voices = Counter(r.voice.value for r in results if r.voice)
        print("\nVoices:")
        for voice, count in voices.most_common():
            print(f"  {voice}: {count} ({count/total*100:.1f}%)")

    # Error statistics
    total_flags = sum(len(r.flags) for r in results)
    sentences_with_errors = sum(1 for r in results if r.flags)

    print("\nGrammar issues:")
    print(f"  Total issues: {total_flags}")
    print(
        f"  Sentences with issues: {sentences_with_errors} ({sentences_with_errors/total*100:.1f}%)"
    )

    # Average sentence length
    avg_length = sum(len(r.tokens) for r in results) / total
    print(f"\nAverage sentence length: {avg_length:.1f} tokens")


if __name__ == "__main__":
    main()
