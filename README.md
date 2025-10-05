# English Grammar Classifier and Parser

A comprehensive English language classifier and parser based on Samuel Kirkham's English Grammar (1829). This implementation follows traditional grammar rules and provides detailed syntactic analysis of English sentences.

## Overview

This parser implements a rule-based approach to English grammar analysis, incorporating the classical grammatical principles outlined in Kirkham's seminal work on English grammar. It performs:

- **Part-of-Speech Classification**: Identifies words as nouns, verbs, adjectives, adverbs, pronouns, prepositions, conjunctions, articles, and interjections
- **Syntactic Parsing**: Extracts sentence structure including subject, verb phrase, and object
- **Grammar Rule Validation**: Checks sentences against traditional grammar rules
- **Voice Detection**: Identifies active, passive, or neuter voice
- **Error Detection**: Identifies grammatical errors and provides warnings

## Features

### 1. Part-of-Speech Classification

The classifier uses a sophisticated rule-based system that considers:
- Lexical lookup from comprehensive word lists
- Morphological analysis (word endings and affixes)
- Contextual information
- Proper noun detection via capitalization

Supported parts of speech:
- **Nouns**: Common and proper nouns, with number (singular/plural) and case (nominative/possessive/objective)
- **Pronouns**: Personal, possessive, demonstrative, relative, and interrogative
- **Verbs**: Main verbs, auxiliaries (be, have, do), and modal verbs
- **Adjectives**: Descriptive words qualifying nouns
- **Adverbs**: Words modifying verbs, adjectives, or other adverbs
- **Prepositions**: Words showing relationships between nouns
- **Conjunctions**: Coordinating and subordinating conjunctions
- **Articles**: Definite (the) and indefinite (a, an)
- **Interjections**: Exclamations and expressions

### 2. Syntactic Analysis

The parser identifies:
- **Subject**: Nominative noun phrase governing the verb
- **Verb Phrase**: Main verb including auxiliaries
- **Object**: Objective noun phrase (for transitive verbs)
- **Voice**: Active, passive, or neuter

### 3. Grammar Rule Validation

Implements checking for the following Kirkham grammar rules:

#### RULE 3: The nominative case governs the verb
Every sentence should have a subject (nominative case) for its verb.

#### RULE 4: The verb must agree with its nominative in number and person
Ensures subject-verb agreement:
- Third person singular subjects require singular verbs (he writes)
- Plural subjects require plural verbs (they write)
- Special handling for "be" verb forms (am, is, are, was, were)

#### RULE 12: A noun or pronoun in the possessive case is governed by the noun which it possesses
Validates that possessive forms (John's, my, his) are followed by a noun.

#### RULE 18: Adjectives belong to, and qualify, nouns expressed or understood
Checks that adjectives properly modify nouns.

#### RULE 20: Active-transitive verbs govern the objective case
Transitive verbs in active voice should have an object.

#### RULE 31: Prepositions govern the objective case
Prepositions should be followed by a noun or pronoun (object of preposition).

## Installation

### Requirements
- Python 3.7+
- No external dependencies (uses only Python standard library)

### Setup

```bash
# Clone or download the file
cd /path/to/llm

# The parser is ready to use
python english_grammar_parser.py
```

## Usage

### Basic Usage

```python
from english_grammar_parser import EnglishGrammarParser

# Create parser instance
parser = EnglishGrammarParser()

# Parse a sentence
sentence = "The quick brown fox jumps over the lazy dog."
result = parser.parse(sentence)

# Access parse results
print(f"Subject: {result.subject.text if result.subject else 'None'}")
print(f"Verb: {result.verb_phrase.text if result.verb_phrase else 'None'}")
print(f"Object: {result.object_phrase.text if result.object_phrase else 'None'}")
print(f"Voice: {result.voice.value if result.voice else 'None'}")

# Check grammar rules
for rule, passed in result.rule_checks.items():
    print(f"{rule}: {'PASS' if passed else 'FAIL'}")
```

### Formatted Output

```python
# Get formatted output
output = parser.parse_and_display(sentence)
print(output)
```

### Example Output

```
======================================================================
ENGLISH GRAMMAR PARSE RESULT
======================================================================

TOKENS:
----------------------------------------------------------------------
  0. The [article]
  1. quick [adjective]
  2. brown [adjective]
  3. fox [noun] case=nominative number=singular person=third
  4. jumps [verb] number=singular person=third
  5. over [preposition]
  6. the [article]
  7. lazy [adjective]
  8. dog [noun] case=nominative number=singular person=third
  9. . [punctuation]

PARSE STRUCTURE:
----------------------------------------------------------------------
Subject:  The quick brown fox
Verb:     jumps
Object:   [NONE]
Voice:    neuter

GRAMMAR RULE CHECKS:
----------------------------------------------------------------------
✓ PASS  rule_3_nominative_governs_verb
✓ PASS  rule_4_verb_agreement
======================================================================
```

## Architecture

The parser follows SOLID principles with a clean, object-oriented design:

### Core Components

#### 1. Lexicon
Manages comprehensive word lists organized by part of speech. Includes:
- Articles, pronouns, conjunctions, prepositions
- Auxiliary verbs and modal verbs
- Common transitive and intransitive verbs
- Common nouns, adjectives, and adverbs

#### 2. TextUtils
Utility functions for text processing:
- Tokenization
- Possessive stripping
- Word form analysis (plurals, participles)
- Capitalization checking

#### 3. PartOfSpeechClassifier
Classifies words into their grammatical categories using:
- Dictionary lookup
- Morphological analysis
- Pattern matching
- Default heuristics

#### 4. SyntacticParser
Performs syntactic analysis:
- Verb phrase identification
- Subject extraction
- Object detection
- Voice determination

#### 5. GrammarRuleValidator
Validates sentences against Kirkham's grammar rules:
- Subject-verb agreement
- Case governance
- Transitive verb objects
- Prepositional objects

#### 6. OutputFormatter
Formats parse results for human-readable display.

### Data Structures

#### Token
Represents a single word or punctuation mark with:
- Original text
- Lemma (base form)
- Part of speech
- Grammatical features (case, gender, number, person)

#### Phrase
Represents a group of related tokens:
- Token list
- Phrase type (NP, VP, PP)
- Head word index

#### ParseResult
Complete analysis of a sentence:
- All tokens
- Identified phrases (subject, verb, object)
- Voice
- Grammar rule check results
- Errors and warnings

## Examples

### Example 1: Simple Sentence
```python
parser.parse_and_display("The cat sits on the mat.")
```
- **Subject**: The cat
- **Verb**: sits
- **Voice**: neuter (intransitive)
- **Rules**: All pass

### Example 2: Possessive Construction
```python
parser.parse_and_display("John's book is very interesting.")
```
- **Subject**: book (with possessive modifier "John's")
- **Verb**: is
- **Notes**: Possessive relationship detected (RULE 12)

### Example 3: Transitive Verb
```python
parser.parse_and_display("She writes beautiful poems.")
```
- **Subject**: She
- **Verb**: writes
- **Object**: beautiful poems
- **Voice**: active
- **Rules**: Transitive verb has object (RULE 20)

### Example 4: Complex Noun Phrase
```python
parser.parse_and_display("The quick brown fox jumps over the lazy dog.")
```
- **Subject**: The quick brown fox (multi-word noun phrase with adjectives)
- **Verb**: jumps
- **Rules**: Adjectives properly qualify nouns (RULE 18)

## Limitations

As a rule-based system, this parser has certain limitations:

1. **Lexicon Coverage**: Unknown words may be misclassified
2. **Ambiguity**: Cannot always resolve part-of-speech ambiguity without semantic context
3. **Complex Syntax**: Handles basic sentence structures; complex constructions may not parse correctly
4. **Idioms**: Does not recognize idiomatic expressions
5. **Context**: Cannot use discourse context to resolve references

## Extending the Parser

### Adding New Words

Add words to the appropriate lexicon set in the `Lexicon` class:

```python
class Lexicon:
    COMMON_TRANSITIVE_VERBS: Set[str] = {
        # Add your verbs here
        "create", "destroy", "modify"
    }
```

### Adding New Grammar Rules

Implement new validation methods in `GrammarRuleValidator`:

```python
def _check_rule_X(self, parse_result: ParseResult) -> None:
    """RULE X: Description of the rule."""
    # Implementation
    pass
```

### Improving Classification

Extend `PartOfSpeechClassifier` methods to handle special cases:

```python
def _classify_special_case(self, word: str) -> Token:
    # Custom logic
    pass
```

## Technical Details

### Tokenization
Uses regex-based tokenization preserving:
- Contractions (don't, won't)
- Possessives (John's)
- Punctuation as separate tokens

### Agreement Checking
Implements traditional subject-verb agreement rules:
- First person singular: I am, I write
- Second person: you are, you write
- Third person singular: he is, he writes
- Third person plural: they are, they write

### Voice Detection
Identifies voice through:
- Passive: auxiliary "be" + past participle
- Active: transitive verb with object
- Neuter: intransitive verb or linking verb

## References

1. **Kirkham, Samuel**. *English Grammar in Familiar Lectures*. 1829.
   - Classic grammar text providing the foundational rules
   - Available from Project Gutenberg

2. **Traditional Grammar Principles**
   - Eight parts of speech
   - Three grammatical cases (nominative, possessive, objective)
   - Subject-verb agreement
   - Voice (active/passive)

## License

This implementation is provided for educational purposes. The original grammar rules are in the public domain (Kirkham, 1829).

## Author

Generated based on Samuel Kirkham's English Grammar
Date: October 2025

## Contributing

To improve the parser:

1. Expand lexicons with more words
2. Add additional grammar rule checks
3. Improve classification heuristics
4. Enhance phrase structure identification
5. Add support for more complex sentence structures

## Testing

Run the built-in examples:

```bash
python english_grammar_parser.py
```

The script includes comprehensive test sentences demonstrating various grammatical constructions.

---

For questions or issues, refer to the source code comments which provide detailed documentation of each component.
