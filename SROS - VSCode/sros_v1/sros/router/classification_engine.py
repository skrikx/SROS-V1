"""
Classification Engine for SRX Router
====================================

Classifies incoming task intents into predefined labels (code, tests, docs,
research, governance) by pattern matching against the intent text.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class TaskLabel(Enum):
    """Predefined task classification labels."""
    CODE = "code"
    TESTS = "tests"
    DOCS = "docs"
    RESEARCH = "research"
    GOVERNANCE = "governance"
    UNCLASSIFIED = "unclassified"


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    primary_label: TaskLabel
    confidence: float  # 0.0 to 1.0
    matched_patterns: List[str]
    secondary_labels: List[TaskLabel]


class ClassificationEngine:
    """
    Classifies incoming intents into task labels using pattern matching.
    
    Patterns are defined per label and matched case-insensitively against
    the full intent text. Confidence is based on number and specificity of matches.
    """

    # Classification patterns per label (from SRX schema)
    PATTERNS = {
        TaskLabel.CODE: [
            r"\brefactor\b",
            r"\bimplement\b",
            r"\bfix\s+bug",
            r"\badapter\b",
            r"\bintegration\s+code\b",
            r"\bpython\s+module\b",
            r"\btypescript\b",
            r"\bfunction\b",
            r"\bclass\b",
            r"\bmethod\b",
            r"\bmodule\b",
            r"\bapi\b",
        ],
        TaskLabel.TESTS: [
            r"\bunit\s+test",
            r"\bpytest\b",
            r"\bintegration\s+test",
            r"\bcoverage\b",
            r"\btest\s+case",
            r"\btest\s+suite",
            r"\bfixture",
            r"\bmock\b",
        ],
        TaskLabel.DOCS: [
            r"\breadme\b",
            r"\bdocumentation\b",
            r"\bdocstring",
            r"\bguide\b",
            r"\btutorial\b",
            r"\bexample\b",
            r"\bapi\s+reference",
            r"\bcomment\b",
        ],
        TaskLabel.RESEARCH: [
            r"\bresearch\b",
            r"\bcompare\b",
            r"\bsurvey\b",
            r"\bliterature\b",
            r"\banalyze\b",
            r"\bevaluate\b",
            r"\bstudy\b",
        ],
        TaskLabel.GOVERNANCE: [
            r"\bsafety\b",
            r"\brisk\b",
            r"\bpolicy\b",
            r"\bgovernance\b",
            r"\bsecurity\b",
            r"\bcompliance\b",
            r"\baudit\b",
            r"\bcontrol\b",
        ],
    }

    def __init__(self):
        """Initialize classification engine with compiled regex patterns."""
        self.compiled_patterns = {}
        for label, patterns in self.PATTERNS.items():
            self.compiled_patterns[label] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def classify(self, intent_text: str) -> ClassificationResult:
        """
        Classify an intent into one or more task labels.
        
        Args:
            intent_text: The raw intent/request text to classify
            
        Returns:
            ClassificationResult with primary label, confidence, and matches
        """
        if not intent_text or not isinstance(intent_text, str):
            return ClassificationResult(
                primary_label=TaskLabel.UNCLASSIFIED,
                confidence=0.0,
                matched_patterns=[],
                secondary_labels=[],
            )

        # Score each label based on pattern matches
        label_scores: Dict[TaskLabel, Tuple[int, List[str]]] = {}
        
        for label, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                if pattern.search(intent_text):
                    matches.append(pattern.pattern)
            
            if matches:
                label_scores[label] = (len(matches), matches)

        # If no matches, return unclassified
        if not label_scores:
            return ClassificationResult(
                primary_label=TaskLabel.UNCLASSIFIED,
                confidence=0.0,
                matched_patterns=[],
                secondary_labels=[],
            )

        # Sort by match count (descending) to find primary and secondary labels
        sorted_labels = sorted(
            label_scores.items(), key=lambda x: x[1][0], reverse=True
        )
        
        primary_label, (primary_count, primary_patterns) = sorted_labels[0]
        
        # Confidence based on match count and pattern specificity
        # Max confidence when >3 patterns match, gradually decrease below
        confidence = min(1.0, primary_count / 4.0)
        
        # Secondary labels are those with at least half the primary count
        secondary_labels = []
        if len(sorted_labels) > 1:
            primary_threshold = primary_count / 2.0
            for label, (count, _) in sorted_labels[1:]:
                if count >= primary_threshold:
                    secondary_labels.append(label)

        return ClassificationResult(
            primary_label=primary_label,
            confidence=confidence,
            matched_patterns=primary_patterns,
            secondary_labels=secondary_labels,
        )

    def get_label_patterns(self, label: TaskLabel) -> List[str]:
        """Get all pattern strings for a specific label."""
        return self.PATTERNS.get(label, [])

    def add_custom_pattern(self, label: TaskLabel, pattern: str) -> None:
        """
        Add a custom regex pattern to a label.
        
        Args:
            label: The task label to add pattern to
            pattern: The regex pattern string
        """
        if label not in self.PATTERNS:
            self.PATTERNS[label] = []
        
        self.PATTERNS[label].append(pattern)
        
        # Recompile patterns for this label
        self.compiled_patterns[label] = [
            re.compile(p, re.IGNORECASE) for p in self.PATTERNS[label]
        ]
