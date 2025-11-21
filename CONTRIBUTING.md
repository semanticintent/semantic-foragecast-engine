# Contributing to Semantic Foragecast Engine

Thank you for your interest in contributing to the Semantic Foragecast Engine! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@semanticintent.com](mailto:conduct@semanticintent.com).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [issue tracker](https://github.com/semanticintent/semantic-foragecast-engine/issues) to avoid duplicates.

When creating a bug report, include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. actual behavior
- **Environment details** (OS, Python version, Blender version)
- **Configuration file** you used
- **Error messages** and stack traces
- **Sample files** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:
- **Clear title and description**
- **Use case** - why is this needed?
- **Expected behavior** - what should happen?
- **Alternative solutions** you've considered
- **Related work** - links to similar features

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:
- `good first issue` - Easy issues for newcomers
- `help wanted` - Issues where we need community help
- `documentation` - Improvements to docs

### Pull Requests

We welcome pull requests! Here's the process:

1. **Fork the repository**
2. **Create a feature branch** from `develop`
3. **Make your changes** with tests
4. **Run the test suite** to ensure nothing breaks
5. **Update documentation** as needed
6. **Submit a pull request** to `develop` branch

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Blender 4.0 or higher
- FFmpeg 4.4 or higher
- Git

### Installation

```bash
# 1. Clone your fork
git clone https://github.com/YOUR-USERNAME/semantic-foragecast-engine.git
cd semantic-foragecast-engine

# 2. Add upstream remote
git remote add upstream https://github.com/semanticintent/semantic-foragecast-engine.git

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Install pre-commit hooks (optional but recommended)
pre-commit install

# 6. Verify setup
python tests/test_prep_audio.py
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python tests/test_prep_audio.py
python tests/test_export_video.py
python tests/test_e2e_pipeline.py

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run quick integration test
python quick_test.py
```

### Running Linters

```bash
# Check code style
black --check .
flake8 .
isort --check-only .

# Auto-format code
black .
isort .

# Type checking
mypy *.py
```

## Project Structure

```
semantic-foragecast-engine/
├── main.py                 # Pipeline orchestrator
├── prep_audio.py           # Phase 1: Audio analysis
├── blender_script.py       # Phase 2: Blender automation
├── grease_pencil.py        # 2D animation mode
├── export_video.py         # Phase 3: Video export
├── config.yaml             # Configuration files
├── tests/                  # Test suite
│   ├── test_prep_audio.py
│   ├── test_export_video.py
│   └── test_e2e_pipeline.py
├── docs/                   # Documentation
└── .github/                # GitHub configuration
    ├── workflows/          # CI/CD pipelines
    └── ISSUE_TEMPLATE/     # Issue templates
```

## Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with these modifications:
- **Line length**: 100 characters (not 79)
- **String quotes**: Double quotes preferred
- **Imports**: Sorted with `isort` (black profile)

### Code Quality

- **Type hints**: Use type hints for function signatures
- **Docstrings**: All public functions must have docstrings (Google style)
- **Comments**: Explain *why*, not *what*
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Example

```python
def process_audio(
    audio_path: str,
    lyrics_path: Optional[str] = None,
    output_json: str = "prep_data.json"
) -> Dict[str, Any]:
    """
    Process audio file and extract beats, phonemes, and lyrics.

    Args:
        audio_path: Path to audio file (WAV or MP3)
        lyrics_path: Optional path to lyrics file
        output_json: Output path for prep data

    Returns:
        Dictionary containing audio analysis results

    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If audio format is unsupported
    """
    # Implementation here
    pass
```

## Testing Guidelines

### Test Requirements

- **Unit tests** for all new functions
- **Integration tests** for new features
- **E2E tests** for new modes/workflows
- **Minimum 80% code coverage** for new code

### Test Structure

```python
class TestNewFeature(unittest.TestCase):
    """Test suite for new feature."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        pass

    def setUp(self):
        """Set up before each test."""
        pass

    def test_basic_functionality(self):
        """Test basic feature behavior."""
        # Arrange
        input_data = "test"

        # Act
        result = new_feature(input_data)

        # Assert
        self.assertEqual(result, expected_value)

    def tearDown(self):
        """Clean up after each test."""
        pass
```

### Running Specific Tests

```bash
# Run single test file
python tests/test_prep_audio.py

# Run single test class
python -m unittest tests.test_prep_audio.TestAudioPreprocessor

# Run single test method
python -m unittest tests.test_prep_audio.TestAudioPreprocessor.test_load_audio
```

## Pull Request Process

### Before Submitting

1. **Update documentation** if you changed APIs
2. **Add tests** for new functionality
3. **Run full test suite** locally
4. **Update CHANGELOG.md** with your changes
5. **Ensure CI passes** on your fork

### PR Description Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** must pass (CI, linting, tests)
2. **Code review** by at least one maintainer
3. **Documentation review** if docs changed
4. **Final approval** and merge by maintainer

### After Merge

- Your PR will be included in the next release
- You'll be added to CONTRIBUTORS.md (if not already)
- Thank you for contributing!

## Adding New Features

### New Animation Modes

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed tutorials on:
- Adding new animation modes
- Creating custom effects
- Extending audio analysis
- Building plugins

### File Organization

When adding new files:
- **Core modules** → Root directory
- **Tests** → `tests/` directory
- **Documentation** → Root `.md` files or `docs/` for detailed guides
- **Examples** → `examples/` directory (create if needed)
- **Utilities** → Root directory with clear naming

## Documentation

### README Updates

Update README.md if you:
- Add new features
- Change configuration options
- Modify installation process
- Add dependencies

### Code Documentation

- **Docstrings**: All public APIs
- **Comments**: Complex algorithms
- **Type hints**: Function signatures
- **Examples**: In docstrings for non-obvious usage

### Creating New Guides

For major features, create a new guide in root:
- Follow existing guide structure
- Include Quick Start section
- Add examples and troubleshooting
- Link from README.md

## Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: [support@semanticintent.com](mailto:support@semanticintent.com)

### Communication Channels

- **GitHub Issues**: Technical discussions
- **GitHub Discussions**: General community chat
- **Pull Requests**: Code reviews and feedback

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes
- Project README (for major contributions)

## Attribution

This contribution guide is adapted from open source contribution guides from:
- [Atom](https://github.com/atom/atom/blob/master/CONTRIBUTING.md)
- [Rails](https://github.com/rails/rails/blob/main/CONTRIBUTING.md)
- [Open Source Guides](https://opensource.guide/)

---

Thank you for contributing to Semantic Foragecast Engine! 🎉
