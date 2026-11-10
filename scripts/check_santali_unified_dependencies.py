"""Check the installed dependencies for the unified Santali paths.

This is an import/version check only. It does not download any model weights.
"""
from __future__ import annotations

import importlib
import importlib.metadata

REQUIRED = {
    "onnx_asr": "onnx-asr",
    "av": "av",
    "onnxruntime": "onnxruntime",
    "huggingface_hub": "huggingface-hub",
    "transformers": "transformers",
    "sentencepiece": "sentencepiece",
    "soundfile": "soundfile",
    "numpy": "numpy",
    "torch": "torch",
    "psutil": "psutil",
    "requests": "requests",
    "dotenv": "python-dotenv",
    "multipart": "python-multipart",
}


def main() -> int:
    failures = []
    print("--- Unified Santali dependency check ---")
    print("One project / one environment. No models will be downloaded.\n")

    for module_name, distribution_name in REQUIRED.items():
        try:
            module = importlib.import_module(module_name)
            try:
                version = importlib.metadata.version(distribution_name)
            except importlib.metadata.PackageNotFoundError:
                version = getattr(module, "__version__", "installed; version unknown")
            print(f"OK   {distribution_name}: {version}")
        except Exception as exc:
            failures.append((module_name, distribution_name, exc))
            print(f"FAIL {distribution_name}: {type(exc).__name__}: {exc}")

    # IndicTransToolkit has had two public import shapes across builds.
    try:
        try:
            from IndicTransToolkit import IndicProcessor  # noqa: F401
        except ImportError:
            from IndicTransToolkit.processor import IndicProcessor  # noqa: F401
        version = importlib.metadata.version("IndicTransToolkit")
        print(f"OK   IndicTransToolkit IndicProcessor: {version}")
    except Exception as exc:
        failures.append(("IndicTransToolkit IndicProcessor", "IndicTransToolkit", exc))
        print(f"FAIL IndicTransToolkit IndicProcessor: {type(exc).__name__}: {exc}")

    try:
        import transformers
        from packaging.version import Version
        version = Version(transformers.__version__)
        if version >= Version("5.0"):
            failures.append(("transformers version", "transformers<5", RuntimeError(str(version))))
            print(f"FAIL transformers version: {version}; this integration requires transformers<5")
    except Exception as exc:
        if not any(item[0] == "transformers" for item in failures):
            failures.append(("transformers version", "transformers<5", exc))

    if failures:
        print(f"\nDependency check reported {len(failures)} issue(s).")
        print("Do not create another requirements file or reinstall the entire environment blindly.")
        print("The installer updates the existing requirements.txt (and an existing Docker requirements file, if present).")
        print("If the error mentions a missing module, install only that missing distribution and re-run this check.")
        print("IndicTransToolkit currently documents Linux/macOS rather than Windows as supported/tested platforms;")
        print("a Windows native-extension error may require running the backend in Linux (such as your Docker service).")
        return 1

    print("\nAll required imports passed. The existing dependency set appears sufficient.")
    print("This checks imports only; it does not prove translation accuracy or model downloads.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
