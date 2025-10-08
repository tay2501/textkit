# Pull Request

## 📝 Summary

<!--
Provide a clear and concise summary of your changes.
Include the motivation and context behind these changes.
Reference any related issues using keywords like "Fixes #123", "Closes #456", "Relates to #789".
-->

Brief description of the changes made in this PR.

**Related Issues:**
- Fixes #<!-- issue number -->
- Relates to #<!-- issue number -->

## 🔧 Type of Change

<!--
Select the type of change by marking the appropriate checkbox(es).
-->

- [ ] 🐛 **Bug fix** - non-breaking change that fixes an issue
- [ ] ✨ **New feature** - non-breaking change that adds functionality
- [ ] 💥 **Breaking change** - fix or feature that causes existing functionality to not work as expected
- [ ] 📚 **Documentation** - changes to documentation only
- [ ] 🔄 **Refactoring** - code changes that neither fix a bug nor add a feature
- [ ] ⚡ **Performance** - changes that improve performance
- [ ] 🧪 **Tests** - adding missing tests or correcting existing tests
- [ ] 🔧 **Build/CI** - changes to build process or CI configuration
- [ ] 🏗️ **Infrastructure** - changes to infrastructure, deployment, or tooling

## 🚀 Changes Made

<!--
Provide a more detailed description of the changes.
Use bullet points to list specific changes.
-->

### Components Modified
- [ ] `text_core` - Core text processing functionality (components/)
- [ ] `crypto_engine` - Encryption/decryption functionality (components/)
- [ ] `io_handler` - File input/output operations (components/)
- [ ] `config_manager` - Configuration management (components/)
- [ ] `async_core` - Asynchronous operations (components/)
- [ ] `cli_interface` - Command-line interface (bases/)
- [ ] `interactive_session` - Interactive mode functionality (bases/)
- [ ] CLI commands - Hierarchical structure (`text`, `crypto`, `rules`, `clipboard`)
- [ ] Legacy commands - Deprecated flat commands (`transform`, `iconv`, `encrypt`, `decrypt`)
- [ ] Other: _______________

### Specific Changes
- <!-- List your changes here -->

## 🧪 Testing

<!--
Describe how you tested your changes.
Include details about test cases, scenarios, and verification methods.
-->

### Test Coverage
- [ ] **Unit tests** - all new/modified code has unit tests
- [ ] **Integration tests** - tested integration between components
- [ ] **End-to-end tests** - tested complete user workflows
- [ ] **Manual testing** - manually verified functionality
- [ ] **Performance testing** - verified performance impact (if applicable)

### Test Scenarios
<!--
List specific test scenarios you executed:
-->
1.
2.
3.

### Test Environment
- **Python version(s):** (e.g., 3.12, 3.13)
- **Operating System:** (e.g., Windows 11, Ubuntu 22.04, macOS 14)
- **uv version:** (run `uv --version`)
- **Dependencies updated:** Yes/No

## 📊 Performance Impact

<!--
If your changes might affect performance, please provide details.
-->

- [ ] No performance impact expected
- [ ] Performance improvement (describe below)
- [ ] Potential performance impact (describe and justify below)

**Details:**

## 🔒 Security Considerations

<!--
If your changes have security implications, describe them here.
-->

- [ ] No security impact
- [ ] Security enhancement (describe below)
- [ ] Potential security implications (describe and justify below)

**Details:**

## 📖 Documentation

<!--
Describe any documentation changes needed or made.
-->

- [ ] No documentation changes needed
- [ ] Documentation updated (describe below)
- [ ] Documentation needs to be updated separately

**Changes needed:**

## 🔄 Migration Guide

<!--
If this is a breaking change, provide migration instructions for users.
-->

- [ ] No migration needed
- [ ] Migration required (provide details below)

**Migration steps:**

## ✅ Pre-Review Checklist

<!--
Complete this checklist before requesting review.
-->

### Code Quality
- [ ] My code follows the project's style guidelines (Ruff, MyPy)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas (in English)
- [ ] I have removed any debugging code, console logs, or temporary changes
- [ ] My code follows EAFP (Easier to Ask for Forgiveness than Permission) principles where applicable
- [ ] My code is simple, loosely coupled, and highly cohesive

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally (`uv run pytest`)
- [ ] Linting passes locally (`uv run ruff check .`)
- [ ] Type checking passes locally (`uv run mypy .`)
- [ ] Code formatting is correct (`uv run ruff format --check .`)
- [ ] Manual testing of CLI commands if applicable (e.g., `textkit text transform`, `textkit crypto encrypt`, `textkit rules list`)

### Documentation
- [ ] I have made corresponding changes to the documentation
- [ ] I have updated docstrings for any new/modified functions or classes
- [ ] I have updated the CHANGELOG if this is a user-facing change

### Dependencies & Configuration
- [ ] Any new dependencies are justified and documented
- [ ] I have updated dependency specifications if needed
- [ ] Configuration changes are documented and backwards compatible

### Polylith Architecture
- [ ] Changes respect the Polylith component boundaries
- [ ] No inappropriate dependencies between components
- [ ] Shared functionality is properly placed in components, not bases or projects

## 🔍 Review Focus Areas

<!--
Help reviewers by highlighting areas that need special attention.
-->

Please pay special attention to:
- [ ] Algorithm correctness
- [ ] Error handling
- [ ] Performance implications
- [ ] Security considerations
- [ ] API design
- [ ] User experience
- [ ] Documentation clarity
- [ ] Test coverage

**Specific areas:**

## 📸 Screenshots/Demos

<!--
If applicable, add screenshots or demo GIFs to help illustrate the changes.
-->

## 🤔 Questions for Reviewers

<!--
List any specific questions or concerns you have about the implementation.
-->

1.
2.
3.

## 📚 Additional Context

<!--
Add any other context about the pull request here.
Include links to relevant resources, discussions, or research.
-->

---

### For Maintainers

- [ ] This PR is ready for review
- [ ] This PR needs additional work before review
- [ ] This PR is a draft/work-in-progress

**Reviewer Assignment:** @<!-- username -->

---

<!--
🎉 Thank you for contributing to the Text Processing Toolkit!
Your pull request helps make this project better for everyone.
-->