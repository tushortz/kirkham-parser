# Kirkham Grammar Parser

A comprehensive English language parser based on Samuel Kirkham's English Grammar (1829). This implementation provides detailed syntactic analysis, grammar rule validation, and linguistic feature detection for English sentences.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue.svg)](https://python-poetry.org)

## 🚀 Quick Start

### Installation

The Kirkham Grammar Parser is managed with Poetry and can be installed in several ways:

#### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/tushortz/kirkham-parser.git
cd kirkham-parser

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

#### Option 2: Install with pip

```bash
# Install directly from GitHub
pip install git+https://github.com/tushortz/kirkham-parser.git

# Or install in development mode
pip install -e .
```

#### Option 3: Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/tushortz/kirkham-parser.git
cd kirkham-parser

# Install development dependencies
poetry install --with dev,test,lint

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run black .
```

### Basic Usage

#### Command Line Interface

```bash
# Parse a single sentence
kirkham "The cat sat on the mat."

# Parse with JSON output
kirkham "The cat sat on the mat." -j

# Parse from a file
kirkham -f sentences.txt

# Parse with verbose output
kirkham "The cat sat on the mat." -v
```

#### Python API

```python
from kirkham import KirkhamParser

# Create parser instance
parser = KirkhamParser()

# Parse a sentence
result = parser.parse("The quick brown fox jumps over the lazy dog.")

# Access parse results
print(f"Subject: {result.subject.text if result.subject else 'None'}")
print(f"Verb: {result.verb_phrase.text if result.verb_phrase else 'None'}")
print(f"Object: {result.object_phrase.text if result.object_phrase else 'None'}")
print(f"Voice: {result.voice.value if result.voice else 'None'}")
print(f"Tense: {result.tense.value if result.tense else 'None'}")

# Check grammar rules
for rule, passed in result.rule_checks.items():
    print(f"{rule}: {'PASS' if passed else 'FAIL'}")

# Get JSON output
json_data = parser.to_json("The cat sat on the mat.")
print(json_data)

# Get human-readable explanation
explanation = parser.explain("The cat sat on the mat.")
print(explanation)
```

## 📋 Features

### Core Capabilities

- **Part-of-Speech Classification**: Identifies 9 parts of speech with grammatical features
- **Syntactic Parsing**: Extracts sentence structure (subject, verb, object)
- **Grammar Rule Validation**: Checks sentences against traditional grammar rules
- **Orthography Validation**: Validates spelling according to Kirkham's orthography rules
- **Punctuation Validation**: Checks punctuation usage (commas, semicolons, colons, etc.)
- **Voice Detection**: Identifies active, passive, or neuter voice
- **Tense Detection**: Determines verb tense (present, past, future, perfect)
- **Sentence Type Detection**: Classifies declarative, interrogative, imperative, exclamatory
- **Error Detection**: Identifies grammatical errors with precise locations
- **Unicode Support**: Handles Unicode apostrophes, quotes, and dashes
- **Character Offsets**: Provides token positions for UI highlighting

### Grammar Rules Implemented

The parser implements comprehensive checking for Kirkham's grammar rules:

#### Traditional Grammar Rules
- **RULE 1**: A/an agrees with its noun in the singular only
- **RULE 2**: The belongs to nouns to limit/define their meaning
- **RULE 3**: The nominative case governs the verb
- **RULE 4**: The verb must agree with its nominative in number and person
- **RULE 8**: Compound subjects need plural verb/pronoun
- **RULE 12**: A noun or pronoun in the possessive case is governed by the noun which it possesses
- **RULE 13**: Personal pronouns agree with their nouns in gender and number
- **RULE 18**: Adjectives belong to, and qualify, nouns expressed or understood
- **RULE 19**: Adjective pronouns belong to nouns
- **RULE 20**: Active-transitive verbs govern the objective case
- **RULE 21**: To be admits the same case after it as before it
- **RULE 25**: Bare infinitive after certain verbs
- **RULE 28**: Perfect participle belongs to noun/pronoun
- **RULE 29**: Adverbs qualify verbs, participles, adjectives, and other adverbs
- **RULE 30**: Prepositions are generally placed before the case they govern
- **RULE 31**: Prepositions govern the objective case

#### Orthography Rules (Spelling)
- **ORTHO I**: Monosyllables ending in f, l, or s - double final consonant
- **ORTHO II**: Polysyllables ending in f, l, or s - accent-based doubling
- **ORTHO III**: Words ending in y after consonant - change y → i
- **ORTHO IV**: Words ending in y after vowel - retain y
- **ORTHO V**: Suffixes -able, -ous - drop final e except after c/g
- **ORTHO VI**: Final silent e - drop before vowel-initial suffix
- **ORTHO VII-IX**: Additional derivative/spelling cases
- **ORTHO X**: Adding -ing or -ish - drop final e

#### Punctuation Rules
- **COMMA 1-10**: Comprehensive comma usage rules
- **SEMICOLON 1-2**: Semicolon usage for compound members and examples
- **COLON 1-2**: Colon usage for supplemental remarks and pauses
- **PERIOD**: Complete independent sentences end with period
- **DASH**: Sudden breaks, significant pauses, unexpected turns
- **INTERROGATION**: Direct questions end with question mark
- **EXCLAMATION**: Strong emotion ends with exclamation mark
- **APOSTROPHE**: Correct apostrophe usage
- **QUOTATION**: Correct quotation mark usage

### Advanced Features

- **Configurable Parsing**: Customize rule enforcement and behavior
- **Pluggable Lexicons**: Extend word lists without modifying source code
- **Batch Processing**: Parse multiple sentences efficiently
- **Multiple Output Formats**: JSON, CONLL, Penn Treebank, Graphviz
- **Performance Profiling**: Built-in performance monitoring
- **Error Recovery**: Graceful handling of parsing errors
- **Comprehensive Rule Coverage**: 35+ grammar rules, 10 orthography rules, 15+ punctuation rules
- **Smart Proper Noun Detection**: Automatically skips proper nouns in spelling validation
- **Unicode Support**: Handles modern Unicode characters and symbols

## 🏗️ Architecture

The parser follows SOLID principles with a modular, object-oriented design:

### Core Components

- **`KirkhamParser`**: Main API interface
- **`PartOfSpeechClassifier`**: Word classification using lexicons and heuristics
- **`SyntacticParser`**: Sentence structure analysis
- **`GrammarRuleValidator`**: Traditional grammar rule checking
- **`OrthographyValidator`**: Spelling validation according to Kirkham's orthography rules
- **`PunctuationValidator`**: Punctuation usage validation
- **`OutputFormatter`**: Multiple output format support
- **`Lexicon`**: Pluggable word lists and dictionaries

### Data Structures

- **`Token`**: Individual words with grammatical features
- **`Phrase`**: Groups of related tokens (NP, VP, PP)
- **`ParseResult`**: Complete sentence analysis
- **`ParserConfig`**: Configuration options
- **`Flag`**: Grammar violations with precise locations

## 📖 Usage Examples

### Basic Parsing

```python
from kirkham import KirkhamParser

parser = KirkhamParser()
result = parser.parse("The cat sat on the mat.")

# Access components
print(f"Subject: {result.subject.text}")  # "The cat"
print(f"Verb: {result.verb_phrase.text}")  # "sat"
print(f"Voice: {result.voice.value}")  # "neuter"
```

### Orthography and Punctuation Validation

```python
from kirkham import KirkhamParser

parser = KirkhamParser()

# Orthography validation (spelling)
result = parser.parse("I am happi.")
print("Spelling flags:", [f.message for f in result.flags if 'ORTHO' in f.rule.value])
# Output: ['Word ending in y after consonant should change y to i before termination']

# Punctuation validation
result = parser.parse("Hello world")  # Missing period
print("Punctuation flags:", [f.message for f in result.flags if 'PERIOD' in f.rule.value])
# Output: ['Sentence should end with period, exclamation, or question mark']

# Proper nouns are correctly ignored
result = parser.parse("Lagos is a city in Nigeria.")
print("Orthography flags:", [f.message for f in result.flags if 'ORTHO' in f.rule.value])
# Output: [] (no flags - proper nouns ignored)
```

### Configuration

```python
from kirkham import KirkhamParser, ParserConfig

# Custom configuration
config = ParserConfig(
    # Traditional grammar rules
    enforce_rule_20_strict=False,  # Allow transitive verbs without objects
    allow_informal_pronouns=True,  # Allow "It's me"
    enable_extended_validation=True,  # Enable additional checks

    # Orthography (spelling) rules
    enforce_ortho_rules=True,  # Enable orthography checking
    enforce_ortho_i=True,  # Monosyllables ending in f/l/s
    enforce_ortho_ii=True,  # Polysyllables ending in f/l/s
    enforce_ortho_iii=True,  # Words ending in y after consonant

    # Punctuation rules
    enforce_punctuation_rules=True,  # Enable punctuation checking
    enforce_comma_rules=True,  # Enable comma rules
    enforce_period_rules=True,  # Enable period rules
    enforce_semicolon_rules=True,  # Enable semicolon rules
)

parser = KirkhamParser(config)
```

### Batch Processing

```python
# Parse multiple sentences
sentences = [
    "The cat sat on the mat.",
    "She writes beautiful poems.",
    "The birds are singing."
]

results = parser.parse_batch(sentences)

# Process results
for i, result in enumerate(results):
    print(f"Sentence {i+1}: {result.subject.text if result.subject else 'No subject'}")
```

### File Processing

```python
# Parse from file
results = parser.parse_file("sentences.txt", sentence_per_line=True)

# Parse with auto-sentence splitting
results = parser.parse_file("document.txt", sentence_per_line=False)
```

### Custom Lexicons

```python
from kirkham import KirkhamParser, Lexicon

# Create custom lexicon
custom_lexicon = Lexicon(
    transitive_verbs={"customize", "extend", "modify"},
    common_nouns={"widget", "gadget", "device"}
)

parser = KirkhamParser(lexicon=custom_lexicon)
```

### Output Formats

```python
# JSON output
json_data = parser.to_json("The cat sat on the mat.")

# Human-readable explanation
explanation = parser.explain("The cat sat on the mat.")

# CONLL format
conll_output = parser._formatter.to_conll(result)

# Penn Treebank format
treebank_output = parser._formatter.to_penn_treebank(result)

# Graphviz visualization
graphviz_output = parser._formatter.to_graphviz(result)
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=kirkham

# Run specific test file
poetry run pytest kirkham/tests/test_parser.py

# Run with verbose output
poetry run pytest -v
```

### Test Coverage

```bash
# Generate coverage report
poetry run coverage run -m pytest
poetry run coverage report
poetry run coverage html  # Generates HTML report in htmlcov/
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/tushortz/kirkham-parser.git
cd kirkham-parser

# Install with all dependencies
poetry install --with dev,test,lint

# Activate virtual environment
poetry shell
```

### Code Quality

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy kirkham/
```

### Available Scripts

The project includes several convenient scripts defined in `pyproject.toml`:

```bash
# CLI commands
kirkham "sentence"           # Main CLI
grammar-parse "sentence"     # Alternative CLI name

# Development commands
poetry run pytest           # Run tests
poetry run black .          # Format code
poetry run ruff check .     # Lint code
poetry run mypy kirkham/    # Type checking
```

## 📊 Performance

The parser is designed for speed and efficiency:

- **Pure Python**: No external ML dependencies
- **Rule-based**: Fast deterministic parsing
- **Optimized Lexicons**: Frozen sets for O(1) lookups
- **Batch Processing**: Parallel processing support
- **Memory Efficient**: Minimal object overhead

### Benchmarks

Typical performance on modern hardware:
- **Simple sentences**: ~1ms per sentence
- **Complex sentences**: ~5ms per sentence
- **Batch processing**: ~1000 sentences/second
- **Memory usage**: ~50MB for typical workloads

## 🔍 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Make sure you're in the virtual environment
poetry shell

# Or run with poetry
poetry run kirkham "sentence"
```

#### CLI Not Found
```bash
# Reinstall the package
poetry install

# Check if scripts are installed
poetry run kirkham --help
```

#### Parsing Errors
```python
# Enable error recovery
config = ParserConfig(enable_error_recovery=True)
parser = KirkhamParser(config)
```

### Getting Help

1. **Check the documentation**: Start with this README
2. **Run examples**: Try the CLI with different sentences
3. **Review source code**: Well-commented implementation
4. **Check issues**: Look at GitHub issues for common problems

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/kirkham-parser.git
cd kirkham-parser

# Install development dependencies
poetry install --with dev,test,lint

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Add tests** for new functionality
2. **Update documentation** as needed
3. **Follow code style** (black + ruff)
4. **Run tests** before submitting

### Submitting Changes

```bash
# Run all checks
poetry run pytest
poetry run ruff check .
poetry run black .
poetry run mypy kirkham/

# Commit changes
git commit -m "Add feature: description"

# Push and create PR
git push origin feature/your-feature-name
```

## 📚 Documentation

- **API Reference**: See docstrings in source code
- **Examples**: Check `kirkham/examples/` directory
- **Grammar Rules**: Based on Kirkham's English Grammar (1829)
- **Architecture**: Modular design with clear separation of concerns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Samuel Kirkham** (1829) for the foundational grammar rules
- **Python Community** for excellent tooling and libraries
- **Contributors** who help improve the parser

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tushortz/kirkham-parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tushortz/kirkham-parser/discussions)
- **Documentation**: [Read the Docs](https://kirkham.readthedocs.io)

---

**Version**: 0.1.0
**Status**: ✅ Active Development
**Python**: 3.8+
**License**: MIT

### What's New in v0.1.0

- ✨ **Orthography Rules**: Complete implementation of Kirkham's spelling rules (ORTHO I-X)
- ✨ **Punctuation Rules**: Comprehensive punctuation validation (COMMA, SEMICOLON, COLON, etc.)
- ✨ **Proper Noun Handling**: Smart detection that skips proper nouns in spelling checks
- ✨ **Enhanced Grammar Rules**: Additional Kirkham grammar rules (RULE 1, 2, 8, 13, 19, 21, 25, 28, 29, 30)
- ✨ **Configurable Validation**: Granular control over which rules to enforce
- ✨ **Improved Accuracy**: Better pronoun classification and case detection