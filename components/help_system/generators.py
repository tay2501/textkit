"""
Help Content Generators.

This module provides specific help content generators
for different types of help content in the application.
"""

from __future__ import annotations

from typing import Dict, Any, List, TYPE_CHECKING

from .core import HelpGenerator, HelpSection

if TYPE_CHECKING:
    from ..text_core import TextTransformationEngine


class DynamicHelpGenerator(HelpGenerator):
    """Generator for dynamic help content.

    This generator creates help content based on the current
    state of the application and available components.
    """

    def __init__(self, transformation_engine: TextTransformationEngine = None) -> None:
        """Initialize the dynamic help generator.

        Args:
            transformation_engine: Optional transformation engine for rule help
        """
        self._transformation_engine = transformation_engine

    def generate_help(self, context: Dict[str, Any] = None) -> List[HelpSection]:
        """Generate dynamic help content.

        Args:
            context: Context information for generation

        Returns:
            List of help sections
        """
        sections = []

        # Generate overview section
        sections.append(self._generate_overview_section())

        # Generate quick start section
        sections.append(self._generate_quickstart_section())

        # Generate examples section
        sections.append(self._generate_examples_section(context))

        return sections

    def get_supported_topics(self) -> List[str]:
        """Get supported help topics.

        Returns:
            List of supported topic names
        """
        return ["overview", "quickstart", "examples", "getting-started"]

    def _generate_overview_section(self) -> HelpSection:
        """Generate application overview section."""
        content = """
        Text Processing Toolkit is a modern, modular text transformation
        system built with Polylith architecture. It provides:

        - Comprehensive text transformations
        - Encryption/decryption capabilities
        - Multiple input/output methods
        - Extensible plugin system
        - Rich CLI interface with help system
        """
        return HelpSection("Overview", content.strip())

    def _generate_quickstart_section(self) -> HelpSection:
        """Generate quick start section."""
        content = """
        Getting started is simple:

        1. Basic transformation:
           text-processing-toolkit transform '/t/l' --text "  Hello World  "

        2. From clipboard:
           text-processing-toolkit transform '/u'

        3. See all rules:
           text-processing-toolkit rules

        4. Get help:
           text-processing-toolkit transform --help
        """
        return HelpSection("Quick Start", content.strip())

    def _generate_examples_section(self, context: Dict[str, Any] = None) -> HelpSection:
        """Generate examples section."""
        examples = [
            "Transform text case: '/u' (uppercase), '/l' (lowercase), '/p' (PascalCase)",
            "Clean whitespace: '/t' (trim), '/r' (remove spaces)",
            "Encode/decode: '/b64e' (base64 encode), '/b64d' (base64 decode)",
            "Combine rules: '/t/l/p' (trim, lowercase, then PascalCase)",
        ]

        if context and context.get("include_crypto"):
            examples.extend([
                "Encrypt text: text-processing-toolkit encrypt",
                "Decrypt text: text-processing-toolkit decrypt",
            ])

        content = "Common usage examples:\n\n" + "\n".join(f"- {ex}" for ex in examples)
        return HelpSection("Examples", content)


class RulesHelpGenerator(HelpGenerator):
    """Generator for transformation rules help.

    This generator creates detailed help content about
    available transformation rules and their usage.
    """

    def __init__(self, transformation_engine: TextTransformationEngine = None) -> None:
        """Initialize the rules help generator.

        Args:
            transformation_engine: Transformation engine for rule information
        """
        self._transformation_engine = transformation_engine

    def generate_help(self, context: Dict[str, Any] = None) -> List[HelpSection]:
        """Generate rules help content.

        Args:
            context: Context information for generation

        Returns:
            List of help sections
        """
        sections = []

        if self._transformation_engine:
            rules = self._transformation_engine.get_available_rules()

            # Group rules by category
            rule_groups = self._group_rules_by_category(rules)

            for category, category_rules in rule_groups.items():
                section = self._generate_rule_category_section(category, category_rules)
                sections.append(section)
        else:
            # Fallback static content
            sections.append(self._generate_static_rules_section())

        return sections

    def get_supported_topics(self) -> List[str]:
        """Get supported help topics.

        Returns:
            List of supported topic names
        """
        return ["rules", "transformations", "commands", "reference"]

    def _group_rules_by_category(self, rules: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Group rules by category for better organization."""
        categories = {
            "Text Case": ["l", "u", "p", "c", "s"],
            "Text Cleanup": ["t", "r", "n"],
            "Encoding": ["b64e", "b64d", "e", "d"],
            "Japanese Text": ["fh", "hf", "j", "J"],
            "Cryptography": ["sha256"],
            "Utilities": ["R", "json", "tr"],
        }

        grouped = {}
        used_rules = set()

        for category, rule_keys in categories.items():
            category_rules = {}
            for rule_key in rule_keys:
                if rule_key in rules:
                    category_rules[rule_key] = rules[rule_key]
                    used_rules.add(rule_key)

            if category_rules:
                grouped[category] = category_rules

        # Add remaining rules to "Other" category
        remaining_rules = {k: v for k, v in rules.items() if k not in used_rules}
        if remaining_rules:
            grouped["Other"] = remaining_rules

        return grouped

    def _generate_rule_category_section(self, category: str, rules: Dict[str, Any]) -> HelpSection:
        """Generate help section for a rule category."""
        content_lines = [f"**{category} Transformations**\n"]

        for rule_key, rule_info in rules.items():
            content_lines.append(f"/{rule_key} - {rule_info.name}")
            content_lines.append(f"    {rule_info.description}")

            example = getattr(rule_info, "example", None)
            if example and example != "N/A":
                content_lines.append(f"    Example: {example}")

            content_lines.append("")  # Empty line between rules

        return HelpSection(category, "\n".join(content_lines))

    def _generate_static_rules_section(self) -> HelpSection:
        """Generate static rules section when transformation engine is not available."""
        content = """
        Common transformation rules:

        Text Case:
        - /l - Convert to lowercase
        - /u - Convert to uppercase
        - /p - Convert to PascalCase
        - /c - Convert to camelCase
        - /s - Convert to snake_case

        Text Cleanup:
        - /t - Trim whitespace
        - /r - Remove spaces
        - /n - Normalize Unicode

        Encoding:
        - /b64e - Base64 encode
        - /b64d - Base64 decode
        - /e - URL encode
        - /d - URL decode

        Use 'text-processing-toolkit rules' for complete list.
        """
        return HelpSection("Transformation Rules", content.strip())
