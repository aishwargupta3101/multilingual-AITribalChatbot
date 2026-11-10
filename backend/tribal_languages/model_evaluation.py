
"""Offline evaluation-record validation for experimental tribal-language models.

This module validates recorded evaluation evidence. It does not download models,
run inference, or claim that a model supports a language.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

CAPABILITIES = {"asr", "translation", "tts"}
REQUIRED_CASE_FIELDS = {"case_id", "language_code", "capability", "status", "notes"}
ALLOWED_STATUSES = {"pass", "fail", "needs_review", "not_run"}


@dataclass
class EvaluationIssue:
    severity: str
    code: str
    message: str
    record_id: str | None = None


@dataclass
class EvaluationReport:
    records_checked: int
    eligible_records: int
    issues: list[EvaluationIssue]

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "records_checked": self.records_checked,
            "eligible_records": self.eligible_records,
            "ok": self.ok,
            "issues": [asdict(item) for item in self.issues],
        }


def validate_evaluation_records(path: str | Path) -> EvaluationReport:
    """Validate a JSON file containing manually reviewed model evaluation records."""
    source = Path(path)
    issues: list[EvaluationIssue] = []
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return EvaluationReport(0, 0, [EvaluationIssue("error", "file_not_found", "Evaluation file was not found.")])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return EvaluationReport(0, 0, [EvaluationIssue("error", "invalid_json", f"Evaluation file is not valid UTF-8 JSON: {exc}")])

    if not isinstance(data, dict) or not isinstance(data.get("evaluations"), list):
        return EvaluationReport(0, 0, [EvaluationIssue("error", "invalid_structure", "Root must be an object with an 'evaluations' list.")])

    records = data["evaluations"]
    eligible = 0
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(EvaluationIssue("error", "record_not_object", f"Record at index {index} must be an object."))
            continue
        record_id = str(record.get("case_id", f"index-{index}"))
        before = len(issues)
        missing = REQUIRED_CASE_FIELDS - set(record)
        for field in sorted(missing):
            issues.append(EvaluationIssue("error", f"missing_{field}", f"Required field '{field}' is missing.", record_id))
        if record_id in seen:
            issues.append(EvaluationIssue("error", "duplicate_case_id", f"Duplicate case_id '{record_id}'.", record_id))
        seen.add(record_id)

        capability = record.get("capability")
        if capability not in CAPABILITIES:
            issues.append(EvaluationIssue("error", "invalid_capability", "capability must be asr, translation, or tts.", record_id))
        if record.get("status") not in ALLOWED_STATUSES:
            issues.append(EvaluationIssue("error", "invalid_status", "status must be pass, fail, needs_review, or not_run.", record_id))

        if capability == "asr":
            if not record.get("reference_transcript") or not record.get("predicted_transcript"):
                issues.append(EvaluationIssue("warning", "asr_text_missing", "Record reference and predicted transcripts for ASR evaluation.", record_id))
        elif capability == "translation":
            if not record.get("source_text") or not record.get("translated_text") or not record.get("reviewer"):
                issues.append(EvaluationIssue("warning", "translation_review_missing", "Record source text, translated text, and a human reviewer.", record_id))
        elif capability == "tts":
            if not record.get("audio_path") or not record.get("reviewer"):
                issues.append(EvaluationIssue("warning", "tts_review_missing", "Record generated audio path and human listener/reviewer.", record_id))

        if record.get("status") == "pass" and not record.get("evidence"):
            issues.append(EvaluationIssue("warning", "pass_without_evidence", "A passing status should include evidence, such as output paths or reviewer notes.", record_id))

        if len(issues) == before:
            eligible += 1

    return EvaluationReport(len(records), eligible, issues)


def summarize_results(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize statuses without treating a single pass as production readiness."""
    summary: dict[str, Any] = {}
    for capability in sorted(CAPABILITIES):
        subset = [r for r in records if r.get("capability") == capability]
        summary[capability] = {
            "total": len(subset),
            "pass": sum(r.get("status") == "pass" for r in subset),
            "fail": sum(r.get("status") == "fail" for r in subset),
            "needs_review": sum(r.get("status") == "needs_review" for r in subset),
            "not_run": sum(r.get("status") == "not_run" for r in subset),
            "production_ready": False,
            "note": "Manual review and representative testing are required before production use.",
        }
    return summary
