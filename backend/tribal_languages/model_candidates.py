"""Evidence-based candidate catalog for Gondi, Santali, and Monpa.

This module is descriptive: candidates are NOT enabled automatically. Licensing,
access gates, variety fit, and native-speaker evaluation remain explicit gates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

DeploymentMode = Literal["local_noncommercial_demo", "commercial_product", "hosted_api"]


@dataclass(frozen=True)
class ModelCandidate:
    language: str
    capability: str
    model_id: str | None
    language_code: str | None
    license_id: str | None
    status: str
    requires_hf_access_acceptance: bool = False
    noncommercial_only: bool = False
    hosted_api_permission_required: bool = False
    notes: str = ""
    source_url: str = ""
    enabled: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


_CANDIDATES: tuple[ModelCandidate, ...] = (
    ModelCandidate(
        language="gondi", capability="stt", model_id="facebook/mms-1b-all",
        language_code="wsg", license_id="CC-BY-NC-4.0",
        status="research_candidate_not_enabled", noncommercial_only=True,
        notes=("wsg is the Adilabad Gondi code. Confirm the actual MMS adapter loads "
               "and matches community speech samples. Do not use commercially "
               "without separate written permission/licensing."),
        source_url="https://huggingface.co/facebook/mms-1b-all",
    ),
    ModelCandidate(
        language="gondi", capability="tts", model_id="facebook/mms-tts-wsg",
        language_code="wsg", license_id="CC-BY-NC-4.0",
        status="research_candidate_not_enabled", noncommercial_only=True,
        notes=("Official model card labels this as Gondi, Adilabad. Not a generic "
               "guarantee for every Gondi variety; license is non-commercial."),
        source_url="https://huggingface.co/facebook/mms-tts-wsg",
    ),
    ModelCandidate(
        language="gondi", capability="translation", model_id=None,
        language_code="gon", license_id=None,
        status="no_verified_general_model", notes=(
            "No verified commercial-ready Gondi-Hindi/English translation model "
            "was established in this research. Start with a native-reviewed parallel "
            "corpus and evaluate a dedicated model; do not treat a generic LLM output "
            "as a validated translation."),
        source_url="https://huggingface.co/ai4bharat/models",
    ),
    ModelCandidate(
        language="santali", capability="stt",
        model_id="ai4bharat/indic-conformer-600m-multilingual",
        language_code="sat", license_id="MIT", status="candidate_access_gated",
        requires_hf_access_acceptance=True,
        notes=("The model card lists Santali among its 22 supported languages and "
               "declares MIT. Hugging Face repository access is gated; accept access "
               "terms first, then evaluate Ol Chiki/recording conditions."),
        source_url="https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual",
    ),
    ModelCandidate(
        language="santali", capability="translation", model_id="ai4bharat/indictrans2-indic-indic-dist-320M",
        language_code="sat_Olck", license_id="MIT", status="candidate_access_gated",
        requires_hf_access_acceptance=True,
        notes=("Official model card lists sat_Olck (Santali in Ol Chiki) and MIT. "
               "Human-evaluate direction-specific output before enabling pairs."),
        source_url="https://huggingface.co/ai4bharat/indictrans2-indic-indic-dist-320M",
    ),
    ModelCandidate(
        language="santali", capability="translation_en_to_santali",
        model_id="ai4bharat/indictrans2-en-indic-dist-200M",
        language_code="eng_Latn->sat_Olck", license_id="MIT",
        status="candidate_access_gated", requires_hf_access_acceptance=True,
        notes="Separate English-to-Indic checkpoint; gate/terms and translation quality still need validation.",
        source_url="https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M",
    ),
    ModelCandidate(
        language="santali", capability="translation_santali_to_en",
        model_id="ai4bharat/indictrans2-indic-en-dist-200M",
        language_code="sat_Olck->eng_Latn", license_id="MIT",
        status="candidate_access_gated", requires_hf_access_acceptance=True,
        notes="Separate Indic-to-English checkpoint; gate/terms and translation quality still need validation.",
        source_url="https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M",
    ),
    ModelCandidate(
        language="santali", capability="tts", model_id="ai4bharat/indic-parler-tts",
        language_code="sat", license_id="Apache-2.0", status="candidate_access_gated",
        requires_hf_access_acceptance=True,
        notes=("Model card lists Santali as officially supported and declares Apache-2.0; "
               "repository access is gated. Large model; validate Ol Chiki pronunciation "
               "and CPU/GPU/RAM latency with native speakers."),
        source_url="https://huggingface.co/ai4bharat/indic-parler-tts",
    ),
    ModelCandidate(
        language="santali", capability="tts_alternative", model_id="bodhan-ai/indic-speak",
        language_code="sat", license_id="Indic Open Model License v1.0",
        status="preview_requires_hosting_permission",
        requires_hf_access_acceptance=True, hosted_api_permission_required=True,
        notes=("Santali is Preview tier. License allows several uses but the model card "
               "says hosting it as an API for others requires written sign-off. Not the "
               "default recommendation for a public Render API without permission."),
        source_url="https://huggingface.co/bodhan-ai/indic-speak",
    ),
    ModelCandidate(
        language="monpa", capability="stt", model_id=None,
        language_code=None, license_id=None, status="blocked_variety_and_model_review",
        notes=("No verified model was established for a selected Monpa variety. Ask the "
               "community which language/variety and writing system to support first."),
        source_url="https://glottolog.org/resource/reference/id/500239",
    ),
    ModelCandidate(
        language="monpa", capability="translation", model_id=None,
        language_code=None, license_id=None, status="blocked_variety_and_corpus",
        notes="Choose and name the exact variety, then build/evaluate consented parallel text; do not assign a generic code by guess.",
        source_url="https://glottolog.org/resource/reference/id/500239",
    ),
    ModelCandidate(
        language="monpa", capability="tts", model_id=None,
        language_code=None, license_id=None, status="blocked_variety_and_voice_data",
        notes="No verified voice checkpoint was established. Requires suitable, consented voice recordings or a compatible validated model.",
        source_url="https://glottolog.org/resource/reference/id/500239",
    ),
)


def list_model_candidates(language: str | None = None) -> list[dict]:
    """Return candidate records; every record remains disabled/non-production."""
    key = language.strip().lower() if language else None
    records = [item.to_dict() for item in _CANDIDATES if key is None or item.language == key]
    if key and not records:
        raise ValueError(f"Unknown candidate language: {language}")
    return records


def resolve_indictrans2_route(source: str, target: str) -> tuple[str, str, str]:
    """Return (model_id, source_token, target_token) for supported Santali pivots.

    This helper only chooses a checkpoint route; it does not enable a translation
    pair or claim quality. All pairs must still be human-evaluated.
    """
    aliases = {
        "en": "english", "eng": "english", "eng_latn": "english",
        "hi": "hindi", "hin": "hindi", "hin_deva": "hindi",
        "sat": "santali", "sat_olck": "santali",
    }
    src = aliases.get(str(source).strip().lower(), str(source).strip().lower())
    tgt = aliases.get(str(target).strip().lower(), str(target).strip().lower())
    tokens = {"english": "eng_Latn", "hindi": "hin_Deva", "santali": "sat_Olck"}
    if src not in tokens or tgt not in tokens or src == tgt:
        raise ValueError("Route must be between distinct English, Hindi, and Santali languages")
    if "santali" not in {src, tgt}:
        raise ValueError("This helper only resolves translation pairs involving Santali")
    if src == "english":
        model = "ai4bharat/indictrans2-en-indic-dist-200M"
    elif tgt == "english":
        model = "ai4bharat/indictrans2-indic-en-dist-200M"
    else:
        model = "ai4bharat/indictrans2-indic-indic-dist-320M"
    return model, tokens[src], tokens[tgt]


def candidate_is_eligible(
    candidate: ModelCandidate,
    *,
    deployment_mode: DeploymentMode,
    hf_access_accepted: bool = False,
    commercial_license_permission: bool = False,
    noncommercial_acknowledged: bool = False,
    hosted_api_permission: bool = False,
) -> tuple[bool, str]:
    """Conservative policy gate; this is not legal advice or proof of model quality."""
    if candidate.model_id is None:
        return False, "No model candidate has been verified."
    if candidate.requires_hf_access_acceptance and not hf_access_accepted:
        return False, "Accept the model repository's access conditions before loading it."
    if candidate.noncommercial_only and deployment_mode != "local_noncommercial_demo":
        if not commercial_license_permission:
            return False, "The candidate is CC-BY-NC; obtain commercial permission before this use."
    if (candidate.noncommercial_only and deployment_mode == "local_noncommercial_demo"
            and not commercial_license_permission and not noncommercial_acknowledged):
        return False, "Explicitly acknowledge non-commercial research/demo use before loading this candidate."
    if candidate.hosted_api_permission_required and deployment_mode == "hosted_api" and not hosted_api_permission:
        return False, "Written permission for hosted API use is required by the model card's stated terms."
    return True, "Candidate may be loaded for controlled evaluation; quality is not yet verified."


def get_candidate(language: str, capability: str, model_id: str | None = None) -> ModelCandidate:
    matches = [x for x in _CANDIDATES if x.language == language.strip().lower()
               and x.capability == capability.strip().lower()
               and (model_id is None or x.model_id == model_id)]
    if len(matches) != 1:
        raise ValueError("Expected exactly one matching model candidate")
    return matches[0]
