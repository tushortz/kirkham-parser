# Changelog

All notable changes to the Kirkham Grammar Parser project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Performance profiling capabilities
- Error recovery mechanisms
- Additional output formats (CONLL, Penn Treebank, Graphviz)
- Batch processing with parallel support
- File processing capabilities
- Custom lexicon support

### Changed
- Improved Unicode handling for apostrophes, quotes, and dashes
- Enhanced tokenization with character offsets
- Better error reporting with precise locations

### Fixed
- Various edge cases in grammar rule validation
- Improved agreement checking for complex verb phrases
- Better handling of irregular plurals and possessives

## [0.0.2] - 2025-01-27

### Added
- **Orthography Rules (ORTHO I-X)** - Complete implementation of Kirkham's spelling rules
  - **ORTHO I**: Monosyllables ending in f, l, or s - double final consonant
  - **ORTHO II**: Polysyllables ending in f, l, or s - accent-based doubling
  - **ORTHO III**: Words ending in y after consonant - change y → i
  - **ORTHO IV**: Words ending in y after vowel - retain y
  - **ORTHO V**: Suffixes -able, -ous - drop final e except after c/g
  - **ORTHO VI**: Final silent e - drop before vowel-initial suffix
  - **ORTHO VII-IX**: Additional derivative/spelling cases
  - **ORTHO X**: Adding -ing or -ish - drop final e

- **Punctuation Rules** - Comprehensive punctuation validation
  - **COMMA Rules 1-10**: Complete comma usage validation
  - **SEMICOLON Rules 1-2**: Semicolon usage for compound members and examples
  - **COLON Rules 1-2**: Colon usage for supplemental remarks and pauses
  - **PERIOD Rule**: Complete independent sentences end with period
  - **DASH Rule**: Sudden breaks, significant pauses, unexpected turns
  - **INTERROGATION Rule**: Direct questions end with question mark
  - **EXCLAMATION Rule**: Strong emotion ends with exclamation mark
  - **APOSTROPHE Rule**: Correct apostrophe usage
  - **QUOTATION Rule**: Correct quotation mark usage

- **Enhanced Grammar Rules** - Additional Kirkham grammar rules
  - **RULE 1**: A/an agrees with its noun in the singular only
  - **RULE 2**: The belongs to nouns to limit/define their meaning
  - **RULE 8**: Compound subjects need plural verb/pronoun
  - **RULE 13**: Personal pronouns agree with their nouns in gender and number
  - **RULE 19**: Adjective pronouns belong to nouns
  - **RULE 21**: To be admits the same case after it as before it
  - **RULE 25**: Bare infinitive after certain verbs
  - **RULE 28**: Perfect participle belongs to noun/pronoun
  - **RULE 29**: Adverbs qualify verbs, participles, adjectives, and other adverbs
  - **RULE 30**: Prepositions are generally placed before the case they govern

- **Smart Proper Noun Detection** - Automatically skips proper nouns in spelling validation
- **Granular Rule Configuration** - Individual enable/disable for each rule category
- **OrthographyValidator Class** - Dedicated spelling validation component
- **PunctuationValidator Class** - Dedicated punctuation validation component

### Changed
- **Enhanced Pronoun Classification** - Better gender/number/person detection for pronouns
- **Improved Case Detection** - More accurate case assignment for pronouns
- **Better Rule Organization** - Separated orthography and punctuation into dedicated validators
- **Updated Configuration** - Added orthography and punctuation rule toggles

### Fixed
- **Proper Noun Handling** - Fixed orthography rules incorrectly flagging proper nouns like "Lagos"
- **Pronoun Gender Detection** - Fixed personal pronoun gender and number attributes
- **Rule 21 Robustness** - Added null checks for case comparison in copula validation
- **Possessive Pronoun Classification** - Fixed "her" being misclassified as personal instead of possessive

### Technical Improvements
- **Modular Validation** - Separated orthography and punctuation into dedicated classes
- **Type Safety** - Enhanced type hints for new validator classes
- **Error Handling** - Improved error recovery for edge cases in new rules
- **Performance** - Optimized rule checking with early returns and efficient lookups

### Summary
Version 0.1.0 represents a major expansion of the Kirkham Grammar Parser with comprehensive orthography and punctuation validation. This release adds 25+ new rules covering spelling validation (ORTHO I-X) and punctuation usage (COMMA, SEMICOLON, COLON, PERIOD, DASH, INTERROGATION, EXCLAMATION, APOSTROPHE, QUOTATION). The parser now provides complete coverage of Kirkham's grammar system with smart proper noun detection and granular configuration options.

### Breaking Changes
- None. All changes are backwards compatible.

### Migration Guide
- No migration required. All existing functionality remains unchanged.
- New orthography and punctuation validation is enabled by default but can be disabled via configuration.

## [0.0.1] - 2025-01-27

### Added
- **Initial Release** - Complete English grammar parser implementation
- **Core Parser Class** - `KirkhamParser` with clean API
- **Part-of-Speech Classification** - Identifies 9 parts of speech with grammatical features
- **Syntactic Parsing** - Extracts sentence structure (subject, verb phrase, object)
- **Grammar Rule Validation** - Implements Kirkham's traditional grammar rules
- **Voice Detection** - Identifies active, passive, or neuter voice
- **Tense Detection** - Determines verb tense (present, past, future, perfect)
- **Sentence Type Detection** - Classifies declarative, interrogative, imperative, exclamatory
- **Unicode Support** - Handles Unicode apostrophes, quotes, and dashes
- **Character Offsets** - Provides token positions for UI highlighting

### Features
- **Modular Architecture** - Clean separation of concerns with SOLID principles
- **Configurable Parsing** - Customizable rule enforcement and behavior
- **Pluggable Lexicons** - Extend word lists without modifying source code
- **Multiple Output Formats** - JSON, text, CONLL, Penn Treebank, Graphviz
- **Command-Line Interface** - Easy-to-use CLI with multiple options
- **Comprehensive Testing** - 62 unit tests with 91% coverage
- **Type Safety** - Complete type hints throughout the codebase
- **Documentation** - Extensive documentation and examples

### Grammar Rules Implemented
- **RULE 3**: The nominative case governs the verb
- **RULE 4**: The verb must agree with its nominative in number and person
- **RULE 12**: A noun or pronoun in the possessive case is governed by the noun which it possesses
- **RULE 18**: Adjectives belong to, and qualify, nouns expressed or understood
- **RULE 20**: Active-transitive verbs govern the objective case
- **RULE 31**: Prepositions govern the objective case

### Data Structures
- **Token** - Individual words with grammatical features and character offsets
- **Phrase** - Groups of related tokens (NP, VP, PP)
- **ParseResult** - Complete sentence analysis with all components
- **ParserConfig** - Configuration options for customizing behavior
- **Flag** - Grammar violations with precise locations and messages

### Core Components
- **PartOfSpeechClassifier** - Word classification using lexicons and heuristics
- **SyntacticParser** - Sentence structure analysis and phrase extraction
- **GrammarRuleValidator** - Grammar rule checking and error detection
- **OutputFormatter** - Multiple output format support
- **Lexicon** - Comprehensive word lists organized by part of speech
- **TextUtils** - Text processing utilities for tokenization and analysis

### CLI Features
- **Single Sentence Parsing** - `kirkham "sentence"`
- **JSON Output** - `kirkham "sentence" -j`
- **File Processing** - `kirkham -f file.txt`
- **Verbose Output** - `kirkham "sentence" -v`
- **Batch Processing** - Process multiple sentences efficiently

### Python API
- **Simple Parsing** - `parser.parse("sentence")`
- **JSON Output** - `parser.to_json("sentence")`
- **Human-Readable** - `parser.explain("sentence")`
- **Batch Processing** - `parser.parse_batch(sentences)`
- **File Processing** - `parser.parse_file("file.txt")`
- **Configuration** - `KirkhamParser(ParserConfig(...))`

### Development Tools
- **Poetry** - Modern Python dependency management
- **Black** - Code formatting (line length: 88)
- **Ruff** - Fast Python linter with comprehensive rules
- **MyPy** - Static type checking
- **Pytest** - Testing framework with coverage
- **Coverage** - Test coverage reporting

### Project Structure
```
kirkham/
├── __init__.py              # Package initialization and exports
├── types.py                 # Enumerations and constants
├── models.py                # Data structures
├── lexicon.py               # Word lists and dictionaries
├── utils.py                 # Text processing utilities
├── classifier.py            # Part-of-speech classification
├── syntactic.py             # Syntactic parsing
├── validator.py             # Grammar rule validation
├── orthography.py           # Orthography (spelling) validation
├── punctuation.py           # Punctuation validation
├── formatter.py             # Output formatting
├── cli.py                   # Command-line interface
├── examples/                # Usage examples
└── tests/                   # Test suite
```

### Installation
- **Poetry** - `poetry install` (recommended)
- **pip** - `pip install git+https://github.com/tushortz/kirkham-parser.git`
- **Development** - `poetry install --with dev,test,lint`

### Dependencies
- **Python** - 3.8+ (specified in pyproject.toml)
- **typing-extensions** - For Python < 3.10 compatibility
- **Development** - pytest, black, ruff, coverage, mypy

### Documentation
- **README.md** - Comprehensive project documentation
- **INDEX.md** - Detailed project structure and navigation
- **API Reference** - Complete docstrings throughout codebase
- **Examples** - Usage examples in examples/ directory
- **Tests** - Comprehensive test suite with examples

### Testing
- **Unit Tests** - Comprehensive test coverage
- **Coverage** - High test coverage across all modules
- **Edge Cases** - Unicode, contractions, complex sentences
- **Performance Tests** - Batch processing and memory usage
- **Integration Tests** - End-to-end parsing workflows

### Code Quality
- **Type Safety** - Complete type hints with MyPy validation
- **Code Style** - Black formatting with Ruff linting
- **Documentation** - Google-style docstrings throughout
- **Error Handling** - Graceful error recovery and reporting
- **SOLID Principles** - Clean, maintainable object-oriented design

### License
- **MIT License** - Open source with permissive licensing
- **Educational Use** - Suitable for academic and commercial use

### Repository
- **GitHub** - https://github.com/tushortz/kirkham-parser
- **Documentation** - https://kirkham.readthedocs.io
- **Issues** - https://github.com/tushortz/kirkham-parser/issues
- **Discussions** - https://github.com/tushortz/kirkham-parser/discussions

### Acknowledgments
- **Samuel Kirkham** (1829) - Original grammar rules and principles
- **Python Community** - Excellent tooling and libraries
- **Contributors** - Help improve the parser

---

## Development History

### Pre-Release Development

#### Initial Implementation
- Created comprehensive English grammar parser based on Kirkham's Grammar (1829)
- Implemented rule-based part-of-speech classification
- Built syntactic parsing for sentence structure extraction
- Added grammar rule validation with traditional rules

#### Architecture Refactoring
- Refactored monolithic parser into modular components
- Separated concerns into distinct classes and modules
- Implemented SOLID principles throughout codebase
- Added comprehensive type hints and documentation

#### Feature Enhancements
- Added Unicode support for international characters
- Implemented character offset tracking for UI integration
- Enhanced tokenization with robust regex patterns
- Improved morphology heuristics for irregular forms

#### Testing & Quality
- Built comprehensive test suite with 62 unit tests
- Achieved 91% test coverage across all modules
- Implemented code quality tools (Black, Ruff, MyPy)
- Added continuous integration and development workflows

#### Documentation & Packaging
- Created comprehensive documentation (README.md, INDEX.md)
- Set up Poetry for modern Python packaging
- Added command-line interface with multiple options
- Implemented multiple output formats for different use cases

#### Performance Optimization
- Optimized lexicon lookups with frozen sets
- Implemented batch processing with parallel support
- Added performance profiling capabilities
- Optimized memory usage and object overhead

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Current Version: 0.1.0

This version (0.1.0) represents a major feature addition with comprehensive orthography and punctuation validation. Future versions will increment based on the semantic versioning scheme.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
