"""Main parser class for the Kirkham Grammar Parser.

This module provides the main KirkhamParser class that orchestrates
the parsing process using the various specialized components.
"""

from __future__ import annotations

import re

from .formatter import OutputFormatter
from .lexicon import Lexicon
from .models import DEFAULT_CONFIG, ParserConfig, ParseResult
from .syntactic import SyntacticParser

# Sentence splitting regex (basic sentence boundary detection)
# Splits on sentence-ending punctuation followed by whitespace and a capital
# letter or quote
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\u201C])')


class KirkhamParser:
    """Main parser class for English grammar analysis.

    Provides a clean, reusable API for parsing and analyzing English
    sentences based on Kirkham's Grammar rules.

    This class maintains state (config, lexicons) and exposes a simple
    interface: parse(), explain(), to_json().
    """

    def __init__(
        self, cfg: ParserConfig = DEFAULT_CONFIG, lexicon: Lexicon | None = None
    ) -> None:
        """Initialize the parser with configuration and optional lexicon.

        Args:
            cfg: Parser configuration. Defaults to DEFAULT_CONFIG.
            lexicon: Custom lexicon for word lists. Defaults to DEFAULT_LEXICON.
                     Users can extend lexicons without editing code.

        Examples:
            # Default configuration
            parser = KirkhamParser()

            # Custom configuration
            cfg = ParserConfig(
                enforce_rule_20_strict=False,
                allow_informal_pronouns=True
            )
            parser = KirkhamParser(cfg)

            # Custom lexicon
            custom_lex = Lexicon(
                transitive_verbs=Lexicon.COMMON_TRANSITIVE_VERBS
                | {"customize", "extend"}
            )
            parser = KirkhamParser(lexicon=custom_lex)

        """
        self.cfg = cfg
        self.lex = lexicon or Lexicon()
        self._syntactic_parser = SyntacticParser(self.cfg, self.lex)
        self._formatter = OutputFormatter()

    def parse(self, text: str) -> ParseResult:
        """Parse an English sentence.

        Args:
            text: The sentence to parse

        Returns:
            ParseResult object with complete analysis

        Example:
            >>> parser = KirkhamParser()
            >>> result = parser.parse("The cat sat.")
            >>> result.subject.text
            'The cat'

        """
        return self._syntactic_parser.parse(text)

    def explain(self, text: str, show_offsets: bool = False) -> str:
        """Parse and return human-readable explanation.

        Args:
            text: The sentence to parse
            show_offsets: Whether to show character offsets

        Returns:
            Formatted explanation string

        Example:
            >>> parser = KirkhamParser()
            >>> print(parser.explain("The cat sat."))

        """
        result = self.parse(text)
        return self._formatter.format_text(result, show_offsets=show_offsets)

    def to_json(self, text: str) -> dict:
        """Parse and return JSON-serializable dictionary.

        Useful for APIs and UIs that need structured data with
        token offsets for highlighting.

        Args:
            text: The sentence to parse

        Returns:
            Dictionary with complete parse information

        Example:
            >>> parser = KirkhamParser()
            >>> data = parser.to_json("The cat sat.")
            >>> data['tokens'][0]['text']
            'The'

        """
        result = self.parse(text)
        return result.to_dict()

    def parse_many(self, text: str) -> list[ParseResult]:
        """Parse multiple sentences from a text.

        Performs basic sentence splitting and parses each sentence independently.
        Useful for processing paragraphs or multi-sentence input.

        Args:
            text: Text containing one or more sentences

        Returns:
            List of ParseResult objects, one per sentence

        Example:
            >>> parser = KirkhamParser()
            >>> results = parser.parse_many("The cat sat. The dog barked.")
            >>> len(results)
            2
            >>> results[0].subject.text
            'The cat'

        """
        # Split on sentence boundaries
        parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]

        # If no splits found, treat as single sentence
        if not parts:
            parts = [text.strip()]

        # Parse each sentence
        return [self._syntactic_parser.parse(p) for p in parts]

    def show(
        self, text: str, json_only: bool = True, show_offsets: bool = False
    ) -> None:
        """Parse and display with deterministic output control.

        Args:
            text: The sentence to parse
            json_only: If True, output JSON. If False, formatted text.
            show_offsets: If json_only=False, show character offsets.

        Examples:
            >>> parser.show("The cat sat.")  # JSON (default)
            >>> parser.show("The cat sat.", json_only=False)

        """
        import json

        if json_only:
            # Deterministic JSON output
            json_data = self.to_json(text)
            print(json.dumps(json_data, indent=2, sort_keys=True))
        else:
            # Formatted text output (verbose mode)
            print(self.explain(text, show_offsets=show_offsets))

    def parse_batch(
        self, texts: list[str], parallel: bool = False
    ) -> list[ParseResult]:
        """Parse multiple texts efficiently.

        Args:
            texts: List of sentences/paragraphs to parse
            parallel: If True, use multiprocessing for parallel processing
                     (recommended for large batches, >1000 texts)

        Returns:
            List of ParseResult objects, one per text

        Example:
            >>> parser = KirkhamParser()
            >>> texts = ["The cat sat.", "The dog barked.", "Birds fly."]
            >>> results = parser.parse_batch(texts)
            >>> len(results)
            3
            >>> results[0].subject.text
            'The cat'

        Note:
            Parallel processing has overhead. For small batches (<100 texts),
            sequential processing may be faster. Test with your workload.

        """
        if parallel:
            try:
                from multiprocessing import Pool, cpu_count

                # Use number of CPUs - 1 to leave one core for OS
                num_processes = max(1, cpu_count() - 1)

                with Pool(processes=num_processes) as pool:
                    return pool.map(self.parse, texts)
            except ImportError:
                # Fallback to sequential if multiprocessing not available
                return [self.parse(text) for text in texts]
        else:
            return [self.parse(text) for text in texts]

    def parse_file(
        self, filepath: str, sentence_per_line: bool = False, encoding: str = "utf-8"
    ) -> list[ParseResult]:
        """Parse text from a file.

        Args:
            filepath: Path to text file to parse
            sentence_per_line: If True, treat each line as a separate sentence.
                              If False, auto-split sentences using parse_many().
            encoding: File encoding (default: utf-8)

        Returns:
            List of ParseResult objects

        Example:
            >>> parser = KirkhamParser()
            >>> # File with one sentence per line
            >>> results = parser.parse_file("sentences.txt", sentence_per_line=True)
            >>> # File with paragraphs (auto-split)
            >>> results = parser.parse_file("document.txt", sentence_per_line=False)

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is incorrect

        """
        with open(filepath, encoding=encoding) as f:
            if sentence_per_line:
                lines = [line.strip() for line in f if line.strip()]
                return self.parse_batch(lines)
            text = f.read()
            return self.parse_many(text)
