from __future__ import annotations

import json
from typing import Any


def render(report: dict[str, Any], format: str) -> str:
    if format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if format == "markdown":
        metrics = report.get("metrics", {})
        lines = ["# eSpeak IPA3 benchmark", "", f"- Candidate: `{report.get('candidate')}`", f"- Voice: `{report.get('voice')}`", "", "## Metrics", ""]
        lines.extend(f"- **{key}**: {value}" for key, value in metrics.items())
        failures = [item for item in report.get("comparisons", []) if not item.get("passed")]
        if failures:
            lines.extend(["", "## Mismatches", ""])
            lines.extend(f"- `{item['case_id']}` at index `{item['first_difference']}`" for item in failures)
        return "\n".join(lines)
    return "\n".join(f"{key}: {value}" for key, value in report.get("metrics", {}).items())
