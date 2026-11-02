
# 🌿 Multilingual Tribal AI Chatbot & Language Lab

An AI-powered multilingual chatbot designed to improve access to information and language technology for tribal and underserved communities. The platform combines conversational AI, document-based question answering, speech recognition, translation, and text-to-speech capabilities.

## ✨ Features

- **Multilingual Conversational AI:** Generate context-aware responses using Large Language Models.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant information from knowledge bases using semantic search.
- **Voice Interaction:** Convert speech to text and generate spoken responses.
- **Translation:** Integrate multilingual translation workflows for supported languages.
- **Document Question Answering:** Upload documents and ask questions about their content.
- **Conversation History:** Manage chat sessions and retain conversation history.
- **Web Search Integration:** Access current information through web search tools using the Model Context Protocol (MCP).
- **Language Information APIs:** Retrieve supported language metadata and service health information.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| LLM | Llama 3 |
| AI Framework | LangChain |
| Backend | FastAPI, REST APIs |
| Frontend | Streamlit |
| Vector Search | FAISS |
| Database | MongoDB |
| Speech-to-Text | Faster-Whisper |
| Translation & Text-to-Speech | Meta SeamlessM4T, IndicTrans |
| Web Search Integration | Model Context Protocol (MCP) |
| Tools | Git, GitHub, Docker |

## 🏗️ Architecture

```text
User
 │
 ▼
Streamlit Frontend
 │
 ▼
FastAPI Backend
 │
 ├── LLM Conversation Service (Llama 3)
 ├── RAG Retrieval (LangChain + FAISS)
 ├── Speech-to-Text (Faster-Whisper)
 ├── Translation & Text-to-Speech
 ├── MongoDB (Chat History)
 └── MCP Web Search Integration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- Git
- [Ollama](https://ollama.com/) installed
- MongoDB instance
- FFmpeg installed for audio processing

### Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_NAME>
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**Windows**
```bash
.venv\Scripts\activate
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://localhost:11434
MONGODB_URI=your_mongodb_connection_string
```

Add any additional API keys required by your configured services. Do not commit secrets or credentials.

### Run the Application

Start the FastAPI backend:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Start the Streamlit frontend in a separate terminal:

```bash
streamlit run app.py
```

> Replace `app.py` with the actual Streamlit entry-point file in your repository.

## 📁 Project Structure

```text
.
├── backend/
│   └── main.py
├── frontend/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

> Update this structure to match the current repository layout.

## 🧪 Testing

Run the project tests with:

```bash
python -m pytest
```

## 🔒 Security

- Keep API keys and database credentials in environment variables.
- Never commit `.env` files or private datasets.
- Review uploaded documents and user data handling before deployment.

## 👨‍💻 Author

**Aishwar Gupta**  
AI Intern | Generative AI & Multilingual Applications  
[LinkedIn](https://www.linkedin.com/in/aishwar-gupta3101/) · [GitHub](https://github.com/aishwargupta3101)

## 📄 License

Add a license file if you intend to distribute or open-source this project.
