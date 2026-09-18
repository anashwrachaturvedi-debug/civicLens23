"""Severity scoring engine.

Converts a raw AI detection (category, bounding-box size, confidence)
into a single 0-100 severity score and a discrete priority tier. This
is the bridge between what the computer-vision model sees and what
actually gets surfaced to authorities as "how urgent is this."
"""

from dataclasses import dataclass

from app.models.issue import IssueCategory, IssuePriority
from app.services.ai_service import AIDetectionResult, Detection
from app.utils.constants import (
    CATEGORY_RISK_WEIGHTS,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_MEDIUM_THRESHOLD,
)

_VISUAL_SEVERITY_SCALE = 300.0
"""Multiplier converting a small bounding-box-area ratio into a 0-100-ish scale."""


@dataclass(frozen=True, slots=True)
class SeverityResult:
    """The final severity score, priority, and supporting detail for one issue."""

    category: IssueCategory
    severity_score: float
    confidence_score: float
    priority: IssuePriority


class SeverityService:
    """Computes severity scores and priority levels from AI detection output."""

    def score_detection(self, detection: Detection) -> SeverityResult:
        """Compute a severity score and priority for a single detection.

        The score combines three factors: how much of the frame the
        damage occupies (a proxy for visual severity), how inherently
        risky that issue category is, and how confident the model is —
        a low-confidence detection is deliberately dampened rather than
        treated as equally trustworthy as a high-confidence one.
        """
        visual_severity = min(detection.box_area_ratio * _VISUAL_SEVERITY_SCALE, 100.0)
        category_weight = CATEGORY_RISK_WEIGHTS.get(detection.category.value, 0.5)

        raw_score = visual_severity * category_weight * detection.confidence
        severity_score = round(min(max(raw_score, 0.0), 100.0), 2)

        return SeverityResult(
            category=detection.category,
            severity_score=severity_score,
            confidence_score=round(detection.confidence, 4),
            priority=self._score_to_priority(severity_score),
        )

    def score_ai_result(self, ai_result: AIDetectionResult) -> SeverityResult:
        """Score the highest-confidence detection from a full AI result.

        Raises:
            ValueError: If the AI result contains no detections at all.
        """
        best_detection = ai_result.best_detection
        if best_detection is None:
            raise ValueError("Cannot score severity: no issue was detected in the image.")
        return self.score_detection(best_detection)

    def _score_to_priority(self, severity_score: float) -> IssuePriority:
        """Map a numeric severity score to a discrete priority tier."""
        if severity_score >= SEVERITY_HIGH_THRESHOLD:
            return IssuePriority.HIGH
        if severity_score >= SEVERITY_MEDIUM_THRESHOLD:
            return IssuePriority.MEDIUM
        return IssuePriority.LOW