"""Non-invasive readiness/preflight checks for the gated Santali model stack.

This module checks installed package availability, configuration gates, and (when
explicitly requested) access to small README files from gated Hugging Face repos.
It never downloads model weights or enables inference.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

MODEL_REPOSITORIES: dict[str, str] = {
    "stt": "ai4bharat/indic-conformer-600m-multilingual",
    "translation_en_to_santali": "ai4bharat/indictrans2-en-indic-dist-200M",
    "translation_santali_to_en": "ai4bharat/indictrans2-indic-en-dist-200M",
    "translation_hindi_to_santali": "ai4bharat/indictrans2-indic-indic-dist-320M",
    "translation_santali_to_hindi": "ai4bharat/indictrans2-indic-indic-dist-320M",
    "tts": "ai4bharat/indic-parler-tts",
}

CAPABILITY_IMPORTS: dict[str, tuple[str, ...]] = {
    "stt": ("torch", "transformers", "soundfile", "scipy"),
    "translation": ("torch", "transformers", "sentencepiece", "IndicTransToolkit"),
    "tts": ("torch", "transformers", "parler_tts", "soundfile"),
}

CAPABILITY_FLAGS: dict[str, tuple[str, str]] = {
    "stt": ("TRIBAL_SANTALI_STT_ENABLED", "TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED"),
    "translation": (
        "TRIBAL_SANTALI_TRANSLATION_ENABLED",
        "TRIBAL_SANTALI_TRANSLATION_HF_ACCESS_ACCEPTED",
    ),
    "tts": ("TRIBAL_SANTALI_TTS_ENABLED", "TRIBAL_SANTALI_TTS_HF_ACCESS_ACCEPTED"),
}


def env_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def dependency_report() -> dict[str, dict[str, bool]]:
    return {
        capability: {module: _module_available(module) for module in modules}
        for capability, modules in CAPABILITY_IMPORTS.items()
    }


def configuration_report(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    flags: dict[str, dict[str, bool]] = {}
    for capability, (enabled_name, access_name) in CAPABILITY_FLAGS.items():
        enabled = env_truthy(env.get(enabled_name))
        access_ack = env_truthy(env.get(access_name))
        missing_dependencies = [
            module for module, present in dependency_report()[capability].items() if not present
        ]
        flags[capability] = {
            "enabled": enabled,
            "access_acknowledged_in_env": access_ack,
            "dependencies_present": not missing_dependencies,
            "missing_dependencies": missing_dependencies,
            "safe_to_attempt_only_after_repo_access_probe": (
                enabled and access_ack and not missing_dependencies
            ),
        }
    pairs = sorted({
        pair.strip().lower()
        for pair in str(env.get("TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS", "")).split(",")
        if pair.strip()
    })
    return {
        "capabilities": flags,
        "translation_verified_pairs": pairs,
        "hf_token_configured": bool(str(env.get("HF_TOKEN", "")).strip()),
        "note": "This reports configuration only; it does not prove model quality or automatically enable inference.",
    }


def probe_repo_readme_access(repo_id: str, token: str, hf_hub_download_fn=None) -> dict[str, Any]:
    """Probe gated-file access using only the small README.md, never model weights.

    A temporary cache is used and deleted after the probe. Token and exception text
    are intentionally never included in the returned object.
    """
    if not token.strip():
        return {"repo_id": repo_id, "status": "skipped_no_HF_TOKEN", "readme_accessible": False}
    if hf_hub_download_fn is None:
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            return {"repo_id": repo_id, "status": "huggingface_hub_missing", "readme_accessible": False}
        hf_hub_download_fn = hf_hub_download
    try:
        with tempfile.TemporaryDirectory(prefix="tribal-santali-preflight-") as tmp:
            hf_hub_download_fn(
                repo_id=repo_id,
                filename="README.md",
                repo_type="model",
                token=token,
                cache_dir=str(Path(tmp) / "cache"),
                local_dir=str(Path(tmp) / "files"),
            )
        return {"repo_id": repo_id, "status": "readme_accessible", "readme_accessible": True}
    except Exception as exc:  # avoid echoing exception text that could contain sensitive request detail
        response = getattr(exc, "response", None)
        code = getattr(response, "status_code", None)
        name = type(exc).__name__
        if code in (401, 403) or name in {"GatedRepoError", "RepositoryNotFoundError", "RevisionNotFoundError"}:
            status = "access_denied_or_repo_unavailable_check_HF_terms_token_and_repo_id"
        elif code == 404:
            status = "file_or_repo_not_found_check_repo_id"
        elif name in {"Timeout", "ConnectTimeout", "ReadTimeout", "ConnectionError"}:
            status = "network_error_retry_later"
        else:
            status = "probe_failed_check_backend_logs"
        result: dict[str, Any] = {"repo_id": repo_id, "status": status, "readme_accessible": False}
        if code is not None:
            result["http_status"] = int(code)
        result["exception_type"] = name
        return result


def probe_required_repositories(token: str, hf_hub_download_fn=None) -> list[dict[str, Any]]:
    unique_repos = list(dict.fromkeys(MODEL_REPOSITORIES.values()))
    return [probe_repo_readme_access(repo, token, hf_hub_download_fn) for repo in unique_repos]


def resource_report() -> dict[str, Any]:
    cache = Path(os.getenv("HF_HUB_CACHE") or (Path(os.getenv("HF_HOME", str(Path.home() / ".cache" / "huggingface"))) / "hub"))
    try:
        disk_root = cache
        while not disk_root.exists() and disk_root != disk_root.parent:
            disk_root = disk_root.parent
        free_gb = round(shutil.disk_usage(disk_root).free / (1024 ** 3), 2)
    except OSError:
        free_gb = None
    ram_gb = None
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2)
    except Exception:
        pass
    return {
        "hf_cache_path": str(cache),
        "free_disk_gb_for_cache_volume": free_gb,
        "available_ram_gb": ram_gb,
        "model_size_note": "Indic Parler-TTS is multi-gigabyte (model.safetensors is about 3.75 GB on the listed revision); actual inference needs additional RAM/VRAM.",
    }
