"""Measurement report generator skeleton."""

from __future__ import annotations

from typing import Any


def render_markdown_summary(profile: dict[str, Any]) -> str:
    """Render a compact measurement-only Markdown report."""

    environment = profile.get("environment", {})
    return "\n".join(
        [
            "# K1 Measurement Report",
            "",
            f"- Robot: {profile.get('robot', 'unknown')}",
            f"- Confidence: {profile.get('confidence', 'unknown')}",
            f"- Floor type: {environment.get('floor_type', 'unknown')}",
            f"- Condition: {environment.get('condition', 'unknown')}",
            f"- Slope: {environment.get('slope', 'unknown')}",
            "",
            "This report is measurement-only and does not define compensation commands.",
        ]
    )
