# 🌿 Tribal AI Chatbot

> Breaking language barriers by enabling tribal communities to communicate with AI in their native languages.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-darkgreen)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![AWS](https://img.shields.io/badge/Deployment-AWS-orange)

## 📖 Overview

**Tribal AI Chatbot** is an AI-powered multilingual conversational assistant designed to help tribal communities in India interact with AI through text and speech in their preferred languages.

The intended pipeline accepts text or speech, performs speech recognition and language processing where supported, generates an answer using a large language model (LLM) and retrieval-augmented generation (RAG), and returns a text or audio response when the required language services are available.

Potential application areas include education, government-scheme information, agriculture, local knowledge, and general information. Responses in high-impact domains should be checked against reliable sources.

## 🎯 Objectives

- Support communication in tribal and regional languages.
- Enable voice-based and text-based conversations.
- Provide translation where the selected language pair is supported.
- Generate context-aware AI responses.
- Retrieve relevant information from configured knowledge sources using RAG.
- Provide a simple user interface.
- Keep the backend modular so additional languages can be evaluated safely.

## 🌍 Language Support

### Existing project language configuration

The project README and configuration have referenced the following languages:

- English
- Hindi
- Manipuri
- Monpa
- Tai Khamti

Actual capabilities may differ by language and by feature. A language being listed in the interface does not by itself confirm that STT, translation, and TTS are all available or validated in production.

### Experimental Tribal Language Lab

The experimental expansion is intended to evaluate these additional languages:

- **Gondi**
- **Santali**
- **Monpa** (with the specific language variety identified before model selection)

The lab is being developed as a modular extension. Do not describe a language pipeline as production-ready until the model, dataset, and end-to-end behavior have been tested.

## 🚀 Features

### 🎤 Speech-to-Text (STT)

- Speech input and transcription through configured ASR services.
- Audio preprocessing and explicit handling of unsupported language/model combinations.
- Language-specific model selection where a compatible checkpoint is available.

**Existing project technology:** Faster-Whisper is listed in the existing project documentation. Other ASR models are candidates for evaluation, not assumed to be enabled.

### 🌐 Language Translation

- Translation between a user's language and a language understood by the response-generation pipeline, where supported.
- Language-pair validation and explicit handling when a model does not support the requested pair.
- Evaluation using human-verified examples for low-resource languages.

**Candidate technology:** Meta NLLB-200. Verify the model's language-token inventory, language-pair support, and licence before use.

### 🤖 AI Assistant

- Conversational question answering.
- Multi-turn context where configured.
- Integration with the project's selected LLM.

**Existing project documentation:** Llama 3.

### 📚 Retrieval-Augmented Generation (RAG)

RAG retrieves relevant material from configured knowledge sources to help ground responses.

Possible knowledge sources include:

- Government schemes
- Education
- Agriculture
- Local information
- Tribal-language documentation

The accuracy of answers depends on the quality, coverage, and freshness of the indexed sources.

### 🔊 Text-to-Speech (TTS)

- Audio responses where a compatible speech-synthesis service is configured.
- Language-specific voice selection and validation.
- Safe fallback when a compatible voice model is unavailable.

**Existing project documentation:** An XTTS service is mentioned, with SeamlessM4T used for some current audio functionality. Confirm the actual runtime path before assuming a particular TTS engine is active for every language.

### 💾 Chat History

- Conversation history and session handling where configured.
- MongoDB integration as documented by the project.

## 🧪 Tribal Language Lab — Steps 1–7

The Tribal Language Lab is a separate experimental extension. The first seven development steps add a language registry, service interfaces, a metadata-only FastAPI router, dataset validation, and a model-evaluation evidence tracker. These tools are designed to avoid replacing existing working language services.

### Modules added across the seven steps

| Component | File | Purpose / current status |
|---|---|---|
| Language registry | `backend/tribal_languages/language_registry.py` | Experimental language metadata and capability flags. |
| STT adapter | `backend/tribal_languages/stt_service.py` | Separate interface for ASR backends; not proof that a target-language ASR model is compatible. |
| Translation adapter | `backend/tribal_languages/translation_service.py` | Validates language pairs and calls a configured adapter only when enabled. |
| TTS adapter | `backend/tribal_languages/tts_service.py` | Separate interface for speech-synthesis backends; capability is disabled until verified. |
| FastAPI router | `backend/tribal_languages/router.py` | Metadata-only API endpoints for experimental language status. |
| Dataset validator | `backend/tribal_languages/dataset_validator.py` | Checks manifest fields, audio paths, duplicates, and licensing/consent metadata. |
| Model metadata validator | `backend/tribal_languages/model_validation.py` | Checks model ID/language-code metadata and flags missing verification or licence review. |
| Model evaluation tracker | `backend/tribal_languages/model_evaluation.py` | Validates recorded ASR, translation, and TTS evaluation evidence. |
| Dataset manifest example | `data/tribal_languages/dataset_manifest.example.json` | Example format only; it contains placeholders, not a real dataset. |
| Model evaluation example | `data/tribal_languages/model_evaluation.example.json` | Example evaluation records; results must be replaced with actual reviewed evidence. |
| Dataset validator CLI | `scripts/validate_tribal_datasets.py` | Validates a dataset manifest from the command line. |
| Evaluation validator CLI | `scripts/validate_model_evaluations.py` | Validates recorded model evaluation entries. |

The experimental router is registered in `backend/main.py` in the current development setup. It reports metadata; it does not automatically connect the experimental STT, translation, or TTS adapters to the deployed chat flow. The frontend has not been assumed to expose these capabilities unless explicitly implemented in your checkout.

### Experimental API endpoints

When the router is included in the running FastAPI application, these metadata endpoints are available:

- `GET /api/v1/tribal-languages/health`
- `GET /api/v1/tribal-languages/languages`
- `GET /api/v1/tribal-languages/languages/{language_code}`

The experimental language entries are disabled by default. A listed language is not a claim of working speech recognition, translation, or synthesis.

### Seven-step development summary

1. **Language registry:** introduced a separate registry for experimental language metadata.
2. **STT interface:** added an isolated speech-recognition adapter and tests.
3. **Translation interface:** added language-pair validation and disabled-by-default behavior.
4. **TTS interface:** added a separate synthesis adapter and tests.
5. **FastAPI metadata router:** added endpoints for checking language metadata without enabling inference.
6. **Dataset validation:** added local checks for manifest structure, transcripts, audio files, duplicate IDs, and metadata.
7. **Model evaluation evidence:** added a structured way to record and validate actual ASR, translation, and TTS test evidence.

Unit tests for these steps have passed in the development/package test environments; rerun the commands in the Testing section inside your own checkout after copying all step packages. Passing unit tests does not prove real-world language accuracy or production readiness.

### Candidate models and datasets

- **ARTPARK-IISc Vaani:** Candidate dataset resource for Indian-language speech research. Check the actual language configurations, recordings, transcripts, access requirements, and licence.
- **Meta MMS:** Candidate ASR foundation models and language-specific TTS checkpoints. Verify the exact language code and checkpoint.
- **Meta NLLB-200:** Candidate machine-translation model. Verify support for the exact language and translation direction.
- **Mozilla Common Voice:** Potential source of labelled speech when the required language and release are available.
- **AIKosh and Bhashini:** Resources to investigate for Indian-language datasets and services.
- **Custom datasets:** May be required for language varieties that lack suitable pretrained models. Collect data with informed speaker consent and document its provenance.

Model-family coverage does not guarantee that a specific dialect or language variety is supported.

### Language-specific validation plan

| Language | STT validation | Translation validation | TTS validation |
|---|---|---|---|
| Gondi | Identify the intended variety and evaluate a compatible checkpoint on verified recordings. | Verify supported language pairs or prepare a reviewed parallel corpus. | Investigate a compatible dedicated voice checkpoint and evaluate pronunciation. |
| Santali | Check the availability and licence of labelled recordings; test recognition quality. | Verify model token support and evaluate with human-reviewed examples. | Check for a suitable voice checkpoint or plan custom model development. |
| Monpa | Identify the exact variety first, such as Tawang Monpa or Kalaktang Monpa, then verify model compatibility. | Verify direct support; do not assume general multilingual coverage is sufficient. | Verify a compatible checkpoint or plan data collection and custom synthesis. |

### Development principles

- Keep experimental modules separate from existing working services.
- Do not change the language code of an existing ASR service to force another language.
- Do not claim a capability is supported until it has been tested.
- Return a clear unsupported status when a compatible model is unavailable.
- Test changes locally before deploying them.
- Check model and dataset licences, especially before commercial use.
- Protect credentials and never commit `.env` files, API keys, or access tokens.

## 🏗️ System Architecture

The intended high-level flow is:

```text
User text or speech
        |
        v
Frontend (Streamlit)
        |
        v
Backend API (FastAPI)
        |
        v
Language and capability selection
        |
        +---- Speech-to-Text (when applicable)
        |
        +---- Translation (when required and supported)
        |
        v
LLM + RAG retrieval
        |
        v
Response generation
        |
        +---- Translation (when required and supported)
        |
        +---- Text-to-Speech (when available)
        |
        v
Text or audio response
```

The precise runtime flow depends on which services are integrated and configured for the selected language.

## 🛠️ Technology Stack

| Component | Technology documented or considered |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Llama 3 |
| Speech-to-Text | Faster-Whisper; other checkpoints under evaluation |
| Translation | Meta NLLB-200 candidate; verify language-pair support |
| Text-to-Speech | Existing audio/TTS services; validate the active engine |
| Orchestration | LangChain |
| Retrieval | FAISS; hybrid retrieval components where configured |
| Database | MongoDB |
| Containers | Docker |
| Deployment | Existing deployment configuration; environment-specific setup required |
| Model and dataset resources | Hugging Face, AIKosh, Bhashini, and other appropriately licensed sources |

This table includes technologies documented in the project and candidates for the experimental lab; it does not mean every candidate is currently enabled.

## 📂 Project Structure

The following is a conceptual structure. Preserve the actual paths in your checkout if they differ.

```text
tribal-ai-chatbot/
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── database/
│   ├── translation/
│   ├── tribal_languages/       # Experimental language modules
│   └── main.py
├── frontend/
│   ├── pages/
│   ├── components/
│   └── app.py
├── rag/
│   ├── embeddings/
│   ├── vector_store/
│   └── documents/
├── data/
│   └── tribal_languages/       # Dataset manifest and local datasets
├── models/
├── docker/
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

Do not commit large model files, private recordings, credentials, or datasets whose licences do not allow redistribution.

## ⚙️ Installation

### 1. Clone the repository

Replace the example URL with the actual repository URL:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_DIRECTORY>
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use the project's existing Python version and dependency instructions if they differ from these examples.

### 4. Configure environment variables

Create a local `.env` file only if required by the project. Add the configuration values needed by your deployment, such as model-provider credentials and database connection settings.

Never commit `.env` or real credentials to version control.

### 5. Run the backend

From the repository root, if `backend/main.py` exposes the FastAPI application as `app`:

```bash
uvicorn backend.main:app --reload
```

Open `http://localhost:8000/docs` to inspect the API routes registered by the application.

### 6. Run the frontend

If the frontend entry point is `frontend/app.py`:

```bash
streamlit run frontend/app.py
```

Use the actual entry point in your checkout if the path differs.

## 🧪 Testing

Run the tests available in your repository. If pytest is configured, you can run:

```powershell
python -m pytest -q
```

The following targeted commands cover the added Step 6 and Step 7 validation tools, plus the Step 5 router. Run them from the repository root in your activated project environment:

```powershell
python -m unittest tests.test_tribal_dataset_validator -v
python -m unittest tests.test_tribal_model_evaluation -v
python -m unittest tests.test_tribal_language_router -v
```

The Step 2–4 tests are included in their respective step packages; use the test module names in those packages' README files. Run only test commands for files that you have copied into your checkout.

For experimental language support, test each capability separately:

1. Registry and language-code validation.
2. Model loading and dependency availability.
3. Speech recognition against human-verified transcripts.
4. Translation in each direction using reviewed examples.
5. Speech synthesis, pronunciation, and audio output.
6. API integration and frontend behavior.
7. Regression tests for existing languages.

A passing unit test does not establish real-world language accuracy. Record actual evaluation results before declaring a language ready for production.

## 🐳 Docker

Build the image using the Dockerfile and build context configured by your project:

```bash
docker build -t tribal-chatbot .
```

Run it only with the required environment variables, network configuration, ports, and services for your application. For example, if the image serves the backend on port 8000:

```bash
docker run --env-file .env -p 8000:8000 tribal-chatbot
```

This example assumes the image starts the backend and that its environment is configured correctly. Follow your actual Dockerfile and Compose configuration.

## ☁️ Deployment

The project may be deployed to a suitable cloud or container platform. Deployment configuration should account for:

- CPU/GPU and memory requirements of the selected models.
- Model download size and startup time.
- Persistent storage for indexes and required assets.
- Secure environment variables and database credentials.
- Audio upload limits, request timeouts, and concurrency.
- Language-specific quality checks and service monitoring.
- Model and dataset licence requirements.

Do not deploy experimental language services as production-ready until end-to-end validation has passed.

## 🔐 Privacy, Data, and Licensing

- Obtain consent before recording or using speakers' voices for dataset creation.
- Document dataset origin, language variety, consent, and usage restrictions.
- Review model licences before deployment, redistribution, or commercial use.
- Avoid storing sensitive audio or conversation data unless necessary and appropriately protected.
- Keep API keys, tokens, passwords, and private configuration out of source control.

## 🛣️ Roadmap

- [x] Add an experimental language registry.
- [x] Add separate STT, translation, and TTS adapter interfaces with conservative defaults.
- [x] Register a metadata-only FastAPI router.
- [x] Add dataset manifest validation tooling.
- [x] Add model-evaluation evidence validation tooling.
- [ ] Identify exact model checkpoints and versions for each target language/variety.
- [ ] Build or curate permissioned, representative evaluation datasets.
- [ ] Run ASR, translation, and TTS experiments and record human-reviewed evidence.
- [ ] Review each model and dataset licence for the intended deployment/commercial use.
- [ ] Connect only validated capabilities to the existing chat pipeline.
- [ ] Add frontend indicators and safe fallbacks for newly validated languages.
- [ ] Run regression tests for existing languages and deployed endpoints.
- [ ] Measure accuracy, latency, memory, and hosting cost before production rollout.

## 🤝 Contributing

Contributions should include a clear description of the change, the language variety involved where relevant, dataset/model provenance, licence information, and tests for any new functionality.

## ⭐ Support

If you find this project useful, consider starring the repository on GitHub.

---

**Project status:** The Tribal AI Chatbot is an ongoing project. Steps 1–7 provide experimental language metadata, service interfaces, and validation/evaluation tools. The Gondi, Santali, and Monpa experimental capabilities remain unverified and disabled by default until compatible models, datasets, licences, and end-to-end behavior have been checked. Existing production-language behavior should be preserved while this work continues.
