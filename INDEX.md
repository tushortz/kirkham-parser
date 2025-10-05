# Kirkham Grammar Parser - Project Index

## 📚 Project Overview

The Kirkham Grammar Parser is a comprehensive English language parser based on Samuel Kirkham's English Grammar (1829). It provides detailed syntactic analysis, grammar rule validation, and linguistic feature detection for English sentences.

**Status**: ✅ Active Development
**Version**: 0.0.1
**Python**: 3.8+
**License**: MIT

---

## 🏗️ Project Structure

### 📦 Package Structure

```
kirkham/
├── __init__.py              # Package initialization and exports
├── parser.py                # Main KirkhamParser class
├── types.py                 # Enumerations and constants
├── models.py                # Data structures (Token, Phrase, ParseResult)
├── lexicon.py               # Word lists and dictionaries
├── utils.py                 # Text processing utilities
├── classifier.py            # Part-of-speech classification
├── syntactic.py             # Syntactic parsing
├── validator.py             # Grammar rule validation
├── formatter.py             # Output formatting
├── cli.py                   # Command-line interface
├── examples/                # Usage examples
│   └── another_example.py   # Example scripts
└── tests/                   # Test suite
    └── test_parser.py       # Unit tests
```

### 📋 Configuration Files

```
pyproject.toml               # Poetry configuration and project metadata
README.md                    # Main documentation
INDEX.md                     # This file - project index
```

---

## 🚀 Quick Start Guide

### Installation

#### Option 1: Poetry (Recommended)
```bash
# Clone repository
git clone https://github.com/tushortz/kirkham-parser.git
cd kirkham-parser

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell
```

#### Option 2: pip
```bash
# Install from GitHub
pip install git+https://github.com/tushortz/kirkham-parser.git
```

### Basic Usage

#### Command Line
```bash
# Parse a sentence
kirkham "The cat sat on the mat."

# JSON output
kirkham "The cat sat on the mat." -j

# Parse from file
kirkham -f sentences.txt
```

#### Python API
```python
from kirkham import KirkhamParser

parser = KirkhamParser()
result = parser.parse("The quick brown fox jumps over the lazy dog.")

print(f"Subject: {result.subject.text}")
print(f"Verb: {result.verb_phrase.text}")
print(f"Voice: {result.voice.value}")
```

---

## 📖 Core Components

### 🔧 Main Classes

#### `KirkhamParser` ⭐
**Main API interface**
- Clean, reusable API for parsing English sentences
- Configurable behavior and rule enforcement
- Multiple output formats (JSON, text, CONLL, etc.)
- Batch processing capabilities

**Key Methods:**
- `parse(text)` - Parse a single sentence
- `parse_many(text)` - Parse multiple sentences
- `parse_batch(texts)` - Efficient batch processing
- `to_json(text)` - Get JSON output
- `explain(text)` - Get human-readable explanation

#### `PartOfSpeechClassifier`
**Word classification engine**
- Identifies 9 parts of speech
- Uses lexicons + morphological analysis
- Handles irregular forms and special cases
- Supports Unicode characters

#### `SyntacticParser`
**Sentence structure analysis**
- Extracts subject, verb phrase, object
- Determines voice (active/passive/neuter)
- Identifies tense and sentence type
- Handles complex noun phrases

#### `GrammarRuleValidator`
**Grammar rule checking**
- Implements Kirkham's 35 grammar rules
- Subject-verb agreement checking
- Case governance validation
- Error detection with precise locations

#### `OutputFormatter`
**Multiple output formats**
- JSON with character offsets
- Human-readable text
- CONLL format
- Penn Treebank format
- Graphviz visualization

### 📊 Data Structures

#### `Token`
Individual words with grammatical features:
- `text` - Original word
- `lemma` - Base form
- `pos` - Part of speech
- `case` - Grammatical case
- `number` - Singular/plural
- `person` - First/second/third
- `start/end` - Character offsets

#### `Phrase`
Groups of related tokens:
- `tokens` - List of tokens
- `phrase_type` - NP, VP, PP
- `head_index` - Index of head word
- `text` - Concatenated text

#### `ParseResult`
Complete sentence analysis:
- `tokens` - All tokens
- `subject` - Subject phrase
- `verb_phrase` - Verb phrase
- `object_phrase` - Object phrase
- `voice` - Voice classification
- `tense` - Tense classification
- `sentence_type` - Sentence type
- `rule_checks` - Grammar rule results
- `flags` - Errors and warnings

---

## 🎯 Key Features

### ✅ Classification
- **9 Parts of Speech**: Nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions, articles, interjections
- **Grammatical Features**: Case, gender, number, person
- **Morphological Analysis**: Plurals, possessives, participles
- **Unicode Support**: Handles Unicode apostrophes, quotes, dashes

### ✅ Parsing
- **Sentence Structure**: Subject, verb phrase, object extraction
- **Voice Detection**: Active, passive, neuter
- **Tense Detection**: Present, past, future, perfect tenses
- **Sentence Types**: Declarative, interrogative, imperative, exclamatory

### ✅ Validation
- **Grammar Rules**: Implements Kirkham's traditional grammar rules
- **Error Detection**: Precise error locations with character offsets
- **Agreement Checking**: Subject-verb agreement validation
- **Case Governance**: Proper case usage validation

### ✅ Output Formats
- **JSON**: Structured data with offsets for UI highlighting
- **Text**: Human-readable explanations
- **CONLL**: Standard NLP format
- **Penn Treebank**: Tree structure format
- **Graphviz**: Visual dependency graphs

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/tushortz/kirkham-parser.git
cd kirkham-parser

# Install development dependencies
poetry install --with dev,test,lint

# Activate virtual environment
poetry shell
```

### Available Commands

```bash
# CLI commands
kirkham "sentence"           # Main CLI
grammar-parse "sentence"     # Alternative CLI name

# Development commands
poetry run pytest           # Run tests
poetry run black .          # Format code
poetry run ruff check .     # Lint code
poetry run mypy kirkham/    # Type checking
poetry run coverage run -m pytest  # Run with coverage
```

### Code Quality Tools

- **Black**: Code formatting (line length: 88)
- **Ruff**: Fast Python linter with many rules
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

---

## 📚 Usage Examples

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

### Configuration

```python
from kirkham import KirkhamParser, ParserConfig

# Custom configuration
config = ParserConfig(
    enforce_rule_20_strict=False,  # Allow transitive verbs without objects
    allow_informal_pronouns=True,  # Allow "It's me"
    enable_extended_validation=True  # Enable additional checks
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

results = parser.parse_batch(sentences, parallel=True)
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

---

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

### Test Structure

- **Unit Tests**: `kirkham/tests/test_parser.py`
- **Coverage**: Currently ~91% coverage
- **Test Types**: Classification, parsing, validation, formatting
- **Edge Cases**: Unicode, contractions, complex sentences

---

## 📊 Performance

### Benchmarks

Typical performance on modern hardware:
- **Simple sentences**: ~1ms per sentence
- **Complex sentences**: ~5ms per sentence
- **Batch processing**: ~1000 sentences/second
- **Memory usage**: ~50MB for typical workloads

### Optimization Features

- **Frozen Sets**: O(1) lexicon lookups
- **Batch Processing**: Parallel processing support
- **Memory Efficient**: Minimal object overhead
- **Pure Python**: No external ML dependencies

---

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

1. **Check the documentation**: Start with README.md
2. **Run examples**: Try the CLI with different sentences
3. **Review source code**: Well-commented implementation
4. **Check issues**: Look at GitHub issues for common problems

---

## 🤝 Contributing

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

---

## 📞 Support & Resources

### Documentation
- **README.md**: Main documentation
- **API Reference**: See docstrings in source code
- **Examples**: Check `kirkham/examples/` directory

### Community
- **Issues**: [GitHub Issues](https://github.com/tushortz/kirkham-parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tushortz/kirkham-parser/discussions)
- **Documentation**: [Read the Docs](https://kirkham.readthedocs.io)

### References
- **Kirkham, Samuel** (1829): *English Grammar in Familiar Lectures*
- **Traditional Grammar**: Eight parts of speech, three cases
- **Modern NLP**: Integration with contemporary tools

---

## ✨ Highlights

### Academic Quality
- Based on authoritative 1829 grammar text
- Implements traditional linguistic theory
- Suitable for educational purposes

### Software Quality
- SOLID principles throughout
- Comprehensive type hints
- Extensive documentation
- Clean, maintainable code

### Practical Utility
- Real-world applications
- Fast performance
- Easy to integrate
- Extensible architecture

---

## 📁 File Locations

All files are in: `/Users/taiwo/Documents/learn/llm/`

```
kirkham/                     # Main package
├── __init__.py              # Package exports
├── parser.py                # Main KirkhamParser class
├── types.py                 # Enumerations
├── models.py                # Data structures
├── lexicon.py               # Word lists
├── utils.py                 # Text utilities
├── classifier.py            # POS classification
├── syntactic.py             # Syntactic parsing
├── validator.py             # Grammar validation
├── formatter.py             # Output formatting
├── cli.py                   # Command-line interface
├── examples/                # Usage examples
└── tests/                   # Test suite

pyproject.toml               # Poetry configuration
README.md                    # Main documentation
INDEX.md                     # This file
```

---

## 🎓 Recommended Reading Order

### For Users:
1. **README.md** - Overview and quick start
2. **INDEX.md** (this file) - Detailed project structure
3. **CLI Examples** - Try `kirkham "sentence" -j`
4. **Python API** - See usage examples above

### For Developers:
1. **README.md** - Project overview
2. **pyproject.toml** - Configuration and dependencies
3. **kirkham/parser.py** - Main API
4. **kirkham/tests/test_parser.py** - Test examples

### For Students:
1. **Kirkham's Grammar** - Learn the foundational rules
2. **README.md** - Basic usage
3. **Source Code** - Implementation details
4. **Examples** - Practice with different sentences

---

**Version**: 0.0.1
**Status**: ✅ Active Development
**Python**: 3.8+
**License**: MIT

---

**Start here**: README.md
**Questions?**: Check GitHub Issues
**Examples**: Try `kirkham "sentence" -j`