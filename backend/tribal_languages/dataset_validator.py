
"""Local, dependency-free validation for experimental tribal-language datasets.

This module checks dataset manifest quality and safe local audio paths. It does
not assess transcription accuracy, consent legality, model quality, or licensing
compatibility; those require human review.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

LANGUAGE_CODE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
REQUIRED_FIELDS = ("dataset_id", "language_code", "audio_path", "transcript", "source", "license")
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".webm", ".opus"}


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    entry_id: str | None = None


@dataclass
class ValidationReport:
    manifest_path: str
    entries_checked: int
    valid_entries: int
    issues: list[ValidationIssue]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_path": self.manifest_path,
            "entries_checked": self.entries_checked,
            "valid_entries": self.valid_entries,
            "ok": self.ok,
            "issues": [asdict(issue) for issue in self.issues],
        }


def _issue(severity: str, code: str, message: str, entry_id: str | None = None) -> ValidationIssue:
    return ValidationIssue(severity=severity, code=code, message=message, entry_id=entry_id)


def _safe_audio_path(dataset_root: Path, relative_path: str) -> Path | None:
    """Resolve an audio path only if it stays inside dataset_root."""
    raw = Path(relative_path)
    if raw.is_absolute():
        return None
    root = dataset_root.resolve()
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def validate_manifest(manifest_path: str | Path, dataset_root: str | Path | None = None) -> ValidationReport:
    manifest = Path(manifest_path)
    issues: list[ValidationIssue] = []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ValidationReport(str(manifest), 0, 0, [_issue("error", "manifest_not_found", "Manifest file does not exist.")])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return ValidationReport(str(manifest), 0, 0, [_issue("error", "invalid_json", f"Manifest is not valid UTF-8 JSON: {exc}")])

    if not isinstance(data, dict):
        return ValidationReport(str(manifest), 0, 0, [_issue("error", "invalid_root", "Manifest root must be a JSON object.")])
    entries = data.get("datasets")
    if not isinstance(entries, list):
        return ValidationReport(str(manifest), 0, 0, [_issue("error", "datasets_not_list", "Manifest must contain a 'datasets' list.")])

    root = Path(dataset_root) if dataset_root is not None else manifest.parent
    valid_entries = 0
    seen_ids: set[str] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            issues.append(_issue("error", "entry_not_object", f"Entry at index {index} must be an object."))
            continue

        entry_id = str(entry.get("dataset_id", f"index-{index}"))
        before = len(issues)

        for field in REQUIRED_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(_issue("error", f"missing_{field}", f"Required field '{field}' must be a non-empty string.", entry_id))

        if entry_id in seen_ids:
            issues.append(_issue("error", "duplicate_dataset_id", f"Duplicate dataset_id '{entry_id}'.", entry_id))
        seen_ids.add(entry_id)

        language_code = entry.get("language_code")
        if isinstance(language_code, str) and language_code and not LANGUAGE_CODE_RE.fullmatch(language_code):
            issues.append(_issue("error", "invalid_language_code", "Use a language code such as 'sat', 'gon', or 'twm'.", entry_id))

        transcript = entry.get("transcript")
        if isinstance(transcript, str) and transcript.strip() and transcript.strip().lower() in {"[unintelligible]", "[unknown]", "n/a"}:
            issues.append(_issue("warning", "review_transcript", "Transcript is a placeholder; review it before training or evaluation.", entry_id))

        license_value = entry.get("license")
        if isinstance(license_value, str) and license_value.strip().lower() in {"unknown", "tbd", "to be determined", "n/a"}:
            issues.append(_issue("error", "license_unverified", "Record the actual dataset/audio license before using this entry.", entry_id))

        audio_value = entry.get("audio_path")
        if isinstance(audio_value, str) and audio_value.strip():
            audio_path = _safe_audio_path(root, audio_value)
            if audio_path is None:
                issues.append(_issue("error", "unsafe_audio_path", "Audio path must be relative and must not escape the dataset root.", entry_id))
            elif audio_path.suffix.lower() not in AUDIO_EXTENSIONS:
                issues.append(_issue("warning", "unusual_audio_extension", "Audio extension is not in the common supported list.", entry_id))
            elif not audio_path.is_file():
                issues.append(_issue("error", "audio_file_missing", f"Audio file was not found: {audio_value}", entry_id))
            elif audio_path.stat().st_size == 0:
                issues.append(_issue("error", "audio_file_empty", f"Audio file is empty: {audio_value}", entry_id))

        # Consent/source evidence is deliberately surfaced as a warning, not inferred.
        if not entry.get("consent_status"):
            issues.append(_issue("warning", "consent_status_missing", "Add consent_status or a documented basis for using this data.", entry_id))
        if len(issues) == before:
            valid_entries += 1

    if not entries:
        issues.append(_issue("warning", "empty_dataset_list", "The manifest contains no dataset entries yet."))
    return ValidationReport(str(manifest), len(entries), valid_entries, issues)


def validate_model_config(config: dict[str, Any]) -> list[ValidationIssue]:
    """Validate metadata only; never downloads models or enables inference."""
    issues: list[ValidationIssue] = []
    model_id = config.get("model_id")
    language_code = config.get("language_code")
    if not isinstance(model_id, str) or not model_id.strip():
        issues.append(_issue("error", "missing_model_id", "model_id must be a non-empty string."))
    elif model_id.startswith("/") or "\\" in model_id or ".." in model_id.split("/"):
        issues.append(_issue("error", "invalid_model_id", "model_id must be a repository identifier, not a local/traversal path."))
    elif model_id.count("/") > 1 or any(not part for part in model_id.split("/")):
        issues.append(_issue("error", "invalid_model_id", "Use a repository ID such as 'organization/model-name'."))
    if not isinstance(language_code, str) or not LANGUAGE_CODE_RE.fullmatch(language_code):
        issues.append(_issue("error", "invalid_language_code", "language_code must be a valid BCP-47-like code, e.g. 'sat' or 'twm'."))
    if config.get("verified") is not True:
        issues.append(_issue("warning", "model_not_verified", "Model is not marked verified; keep inference disabled until compatibility is tested."))
    if config.get("commercial_use_reviewed") is not True:
        issues.append(_issue("warning", "license_review_needed", "Commercial-use rights have not been explicitly reviewed."))
    return issues
