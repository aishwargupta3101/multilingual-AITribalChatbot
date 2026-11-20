"""
RunPod Serverless client for the Tribal AI Chatbot.

Implements the translate() and translate_batch() interface used by the
existing central TranslationService. Jobs are submitted asynchronously and
polled until completion. The existing local IndicTrans2 service is retained
as a fallback when RunPod requests fail.
"""

import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class RunPodIndicTransClient:
    def __init__(
        self,
        endpoint_id: str,
        api_key: str,
        timeout_seconds: float = 600.0,
        poll_interval_seconds: float = 2.0,
        fallback_service=None,
    ):
        self.endpoint_id = str(endpoint_id or "").strip()
        self.api_key = str(api_key or "").strip()
        self.timeout_seconds = max(30.0, float(timeout_seconds))
        self.poll_interval_seconds = max(0.5, float(poll_interval_seconds))
        self.fallback_service = fallback_service

        if not self.endpoint_id or not self.api_key:
            raise ValueError("RunPod endpoint ID and API key are required.")

        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"

    def _http_json(self, method: str, url: str, payload=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1200]
            raise RuntimeError(
                f"RunPod API returned HTTP {exc.code}: {detail}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach RunPod API: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("RunPod returned invalid JSON.") from exc

    def _submit_and_wait(self, job_input: dict) -> dict:
        started = time.monotonic()
        response = self._http_json(
            "POST",
            f"{self.base_url}/run",
            {"input": job_input},
        )

        job_id = response.get("id")
        status = str(response.get("status", "")).upper()

        if not job_id:
            if status == "COMPLETED" and isinstance(response.get("output"), dict):
                return response["output"]
            raise RuntimeError(
                f"RunPod did not return a job ID: {str(response)[:1200]}"
            )

        logger.info(
            "RunPod IndicTrans2 job submitted | job_id=%s | status=%s",
            job_id,
            status or "UNKNOWN",
        )

        while time.monotonic() - started < self.timeout_seconds:
            if status == "COMPLETED":
                output = response.get("output")
                if isinstance(output, dict):
                    return output
                raise RuntimeError("RunPod completed without a valid output object.")

            if status in {"FAILED", "CANCELLED", "TIMED_OUT"}:
                raise RuntimeError(
                    f"RunPod job {job_id} ended with status {status}: "
                    f"{str(response)[:1200]}"
                )

            time.sleep(self.poll_interval_seconds)
            response = self._http_json(
                "GET",
                f"{self.base_url}/status/{job_id}",
            )
            status = str(response.get("status", "")).upper()

        raise TimeoutError(
            f"RunPod job {job_id} exceeded {self.timeout_seconds:.0f} seconds."
        )

    @staticmethod
    def _raise_if_worker_error(output: dict):
        if output.get("error"):
            error_type = output.get("error_type", "RunPodWorkerError")
            detail = output.get("error_detail") or output.get("error")
            raise RuntimeError(f"{error_type}: {detail}")

    def translate(self, text, source_language, target_language):
        text = str(text or "").strip()
        if not text:
            return ""
        if source_language == target_language:
            return text

        try:
            output = self._submit_and_wait({
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            })
            self._raise_if_worker_error(output)

            translated = output.get("translation")
            if not isinstance(translated, str) or not translated.strip():
                raise RuntimeError(
                    f"RunPod response has no translation: {str(output)[:1200]}"
                )
            return translated.strip()

        except Exception:
            if self.fallback_service is None:
                raise
            logger.exception(
                "RunPod translation failed; using local IndicTrans2 fallback."
            )
            return self.fallback_service.translate(
                text, source_language, target_language
            )

    def translate_batch(
        self,
        texts,
        source_language,
        target_language,
        batch_size=8,
    ):
        if not texts:
            return []

        cleaned = [str(item or "").strip() for item in texts]
        if source_language == target_language:
            return cleaned

        try:
            output = self._submit_and_wait({
                "texts": cleaned,
                "source_language": source_language,
                "target_language": target_language,
                "batch_size": max(1, min(int(batch_size), 8)),
            })
            self._raise_if_worker_error(output)

            translations = output.get("translations")
            if (
                not isinstance(translations, list)
                or len(translations) != len(cleaned)
            ):
                raise RuntimeError("RunPod returned an invalid batch response.")

            if any(
                not isinstance(item, str) or not item.strip()
                for item in translations
            ):
                raise RuntimeError(
                    "RunPod returned an empty item in the batch response."
                )

            return [item.strip() for item in translations]

        except Exception:
            if self.fallback_service is None:
                raise
            logger.exception(
                "RunPod batch failed; using local IndicTrans2 fallback."
            )
            return self.fallback_service.translate_batch(
                cleaned,
                source_language,
                target_language,
                batch_size=batch_size,
            )

    def clear_cache(self):
        # Keep the persistent RunPod model cache intact.
        logger.info("RunPod persistent model cache retained.")
        if self.fallback_service is not None:
            self.fallback_service.clear_cache()
