"""Output formatter for the Kirkham Grammar Parser.

This module provides various output formats for parse results,
including JSON, CONLL, Penn Treebank, and Graphviz visualization.
"""

from __future__ import annotations

import json

from .models import ParseResult


class OutputFormatter:
    """Formats parse results into various output formats."""

    @staticmethod
    def to_json(parse_result: ParseResult) -> str:
        """Convert ParseResult to JSON string.

        Args:
            parse_result: ParseResult to convert

        Returns:
            JSON string representation

        """
        return json.dumps(parse_result.to_dict(), indent=2)

    @staticmethod
    def to_conll(parse_result: ParseResult) -> str:
        """Convert ParseResult to CONLL format.

        Args:
            parse_result: ParseResult to convert

        Returns:
            CONLL format string

        """
        lines = []
        for i, token in enumerate(parse_result.tokens):
            # CONLL format: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
            line = f"{i+1}\t{token.text}\t{token.lemma}\t{token.pos.value}\t_\t"

            # Features
            feats = []
            if token.case:
                feats.append(f"Case={token.case.value}")
            if token.number:
                feats.append(f"Number={token.number.value}")
            if token.person:
                feats.append(f"Person={token.person.value}")
            if token.gender:
                feats.append(f"Gender={token.gender.value}")

            line += "|".join(feats) if feats else "_"
            line += "\t_\t_\t_\t_"
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def to_penn_treebank(parse_result: ParseResult) -> str:
        """Convert ParseResult to Penn Treebank format.

        Args:
            parse_result: ParseResult to convert

        Returns:
            Penn Treebank format string

        """

        def phrase_to_tree(phrase) -> str:
            if not phrase:
                return "()"

            phrase_type = phrase.phrase_type or "PHRASE"
            tokens_str = " ".join(token.text for token in phrase.tokens)
            return f"({phrase_type} {tokens_str})"

        tree_parts = []

        if parse_result.subject:
            tree_parts.append(f"(NP {phrase_to_tree(parse_result.subject)})")

        if parse_result.verb_phrase:
            tree_parts.append(f"(VP {phrase_to_tree(parse_result.verb_phrase)})")

        if parse_result.object_phrase:
            tree_parts.append(f"(NP {phrase_to_tree(parse_result.object_phrase)})")

        return f"(S {' '.join(tree_parts)})"

    @staticmethod
    def to_graphviz(parse_result: ParseResult) -> str:
        """Convert ParseResult to Graphviz DOT format.

        Args:
            parse_result: ParseResult to convert

        Returns:
            Graphviz DOT format string

        """
        lines = ["digraph ParseTree {"]
        lines.append("  rankdir=TB;")
        lines.append("  node [shape=box];")

        # Add nodes for phrases
        node_id = 0
        phrase_nodes = {}

        if parse_result.subject:
            phrase_nodes["subject"] = node_id
            lines.append(
                f'  {node_id} [label="NP: {parse_result.subject.head_token.text}"];'
            )
            node_id += 1

        if parse_result.verb_phrase:
            phrase_nodes["verb"] = node_id
            lines.append(
                f'  {node_id} [label="VP: {parse_result.verb_phrase.head_token.text}"];'
            )
            node_id += 1

        if parse_result.object_phrase:
            phrase_nodes["object"] = node_id
            lines.append(
                f'  {node_id} [label="NP: '
                f'{parse_result.object_phrase.head_token.text}"];'
            )
            node_id += 1

        # Add edges
        if "subject" in phrase_nodes and "verb" in phrase_nodes:
            lines.append(
                f'  {phrase_nodes["subject"]} -> {phrase_nodes["verb"]} [label="subj"];'
            )

        if "verb" in phrase_nodes and "object" in phrase_nodes:
            lines.append(
                f'  {phrase_nodes["verb"]} -> {phrase_nodes["object"]} [label="obj"];'
            )

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def show(parse_result: ParseResult, json_only: bool = True) -> None:
        """Display parse result in a readable format.

        Args:
            parse_result: ParseResult to display
            json_only: If True, only show JSON output. If False, show detailed
                breakdown.

        """
        if json_only:
            print(OutputFormatter.to_json(parse_result))
        else:
            # Detailed breakdown
            print("PARSE STRUCTURE")
            # Reconstruct sentence from tokens
            sentence = "".join(
                token.text + " " for token in parse_result.tokens
            ).strip()
            print(f"Sentence: {sentence}")
            print(
                f"Voice: {parse_result.voice.value if parse_result.voice else 'Unknown'}"
            )
            print(
                f"Tense: {parse_result.tense.value if parse_result.tense else 'Unknown'}"
            )
            print(
                f"Sentence Type: {parse_result.sentence_type.value if parse_result.sentence_type else 'Unknown'}"
            )

            if parse_result.subject:
                print(f"Subject: {parse_result.subject.head_token.text}")

            if parse_result.verb_phrase:
                print(f"Verb: {parse_result.verb_phrase.head_token.text}")

            if parse_result.object_phrase:
                print(f"Object: {parse_result.object_phrase.head_token.text}")

            if parse_result.flags:
                print("\nFlags:")
                for flag in parse_result.flags:
                    print(f"  {flag.rule.value}: {flag.message}")

            if parse_result.errors:
                print("\nErrors:")
                for error in parse_result.errors:
                    print(f"  {error}")

            if parse_result.warnings:
                print("\nWarnings:")
                for warning in parse_result.warnings:
                    print(f"  {warning}")

    @staticmethod
    def format_text(parse_result: ParseResult, show_offsets: bool = False) -> str:
        """Format parse result as readable text string.

        Args:
            parse_result: ParseResult to format
            show_offsets: Whether to show character offsets

        Returns:
            Formatted text string

        """
        lines = []
        lines.append("PARSE STRUCTURE")
        # Reconstruct sentence from tokens with proper spacing
        sentence = _reconstruct_text_from_tokens(parse_result.tokens)
        lines.append(f"Sentence: {sentence}")
        lines.append(
            f"Voice: {parse_result.voice.value if parse_result.voice else 'Unknown'}"
        )
        lines.append(
            f"Tense: {parse_result.tense.value if parse_result.tense else 'Unknown'}"
        )
        lines.append(
            f"Sentence Type: {parse_result.sentence_type.value if parse_result.sentence_type else 'Unknown'}"
        )

        if parse_result.subject:
            if show_offsets:
                lines.append(
                    f"Subject: {parse_result.subject.text} [{parse_result.subject.tokens[0].start}:{parse_result.subject.tokens[-1].end}]"
                )
            else:
                lines.append(f"Subject: {parse_result.subject.text}")

        if parse_result.verb_phrase:
            if show_offsets:
                lines.append(
                    f"Verb: {parse_result.verb_phrase.text} [{parse_result.verb_phrase.tokens[0].start}:{parse_result.verb_phrase.tokens[-1].end}]"
                )
            else:
                lines.append(f"Verb: {parse_result.verb_phrase.text}")

        if parse_result.object_phrase:
            if show_offsets:
                lines.append(
                    f"Object: {parse_result.object_phrase.text} [{parse_result.object_phrase.tokens[0].start}:{parse_result.object_phrase.tokens[-1].end}]"
                )
            else:
                lines.append(f"Object: {parse_result.object_phrase.text}")

        if parse_result.flags:
            lines.append("\nFlags:")
            for flag in parse_result.flags:
                if show_offsets and flag.span:
                    lines.append(
                        f"  {flag.rule.value}: {flag.message} [{flag.span.start}:{flag.span.end}]"
                    )
                else:
                    lines.append(f"  {flag.rule.value}: {flag.message}")

        if parse_result.errors:
            lines.append("\nErrors:")
            for error in parse_result.errors:
                lines.append(f"  {error}")

        if parse_result.warnings:
            lines.append("\nWarnings:")
            for warning in parse_result.warnings:
                lines.append(f"  {warning}")

        return "\n".join(lines)


def _reconstruct_text_from_tokens(tokens: list) -> str:
    """Reconstruct text from tokens, preserving original spacing.

    Args:
        tokens: List of tokens with start/end positions

    Returns:
        Properly spaced text string
    """
    if not tokens:
        return ""

    # Sort tokens by start position to ensure correct order
    sorted_tokens = sorted(tokens, key=lambda t: t.start)

    # Reconstruct text by joining tokens with appropriate spacing
    result = []
    for i, token in enumerate(sorted_tokens):
        if i == 0:
            result.append(token.text)
        else:
            prev_token = sorted_tokens[i - 1]
            # Check if there should be a space between tokens
            # No space before punctuation, space before other tokens
            if token.text in {
                ",",
                ".",
                ";",
                ":",
                "!",
                "?",
                ")",
                "]",
                "}",
            } or prev_token.text in {"(", "[", "{"}:
                result.append(token.text)
            else:
                result.append(" " + token.text)

    return "".join(result)
