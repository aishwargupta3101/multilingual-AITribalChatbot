# 🌿 Tribal AI Chatbot
> Breaking language barriers by enabling tribal communities to communicate with AI in their native languages.
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-darkgreen)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![AWS](https://img.shields.io/badge/Deployment-AWS-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 📖 Overview
**Tribal AI Chatbot** is an AI-powered multilingual conversational assistant designed specifically for tribal communities in India. The chatbot enables users to communicate naturally through **speech or text** in their native language.
The system automatically converts speech to text, translates it into the language understood by the Large Language Model (LLM), retrieves relevant knowledge using Retrieval-Augmented Generation (RAG), generates intelligent responses, translates them back into the user's language, and finally converts the response into natural speech.
The goal is to bridge the digital language divide and provide easy access to education, healthcare information, government schemes, agriculture support, and general knowledge.


# 🎯 Objectives
- Support tribal languages
- Voice-to-Voice conversations
- Accurate multilingual translation
- AI-powered question answering
- Retrieval-Augmented Generation (RAG)
- Easy-to-use interface
- Scalable backend architecture

# 🌍 Supported Languages
### Initial Release
- Gondi
- Santali
- Kokborok

### Future Expansion
- Bhili
- Ho
- Kurukh
- Khasi
- Mizo
- Bodo
- Oraon
- More Indian tribal languages

# 🚀 Features

## 🎤 Speech-to-Text

- Record voice
- Automatic speech recognition
- Noise tolerant transcription

**Model**
- NVIDIA NeMo

## 🌐 Language Translation

- Tribal Language → English
- English → Tribal Language

**Model**
- Meta SeamlessM4T

## 🤖 AI Assistant

- Conversational AI
- Context-aware responses
- Memory support
- Multi-turn conversations

**LLM**
- Llama 3


## 📚 Retrieval-Augmented Generation (RAG)

The chatbot retrieves relevant documents before generating responses.

Knowledge sources can include:
- Government schemes
- Healthcare
- Agriculture
- Education
- Local information
- Tribal documentation


## 🔊 Text-to-Speech

- Natural voice generation
- Response spoken in the user's native language

**Model**

- Meta SeamlessM4T
## 💾 Chat History

- Store conversations
- Retrieve previous chats
- User session management

Database:

- MongoDB

# 🏗️ System Architecture

```
User
   │
   ▼
Speech Input
   │
   ▼
NVIDIA NeMo
(Speech-to-Text)
   │
   ▼
Meta SeamlessM4T
(Translation)
   │
   ▼
Llama 3 + LangChain
        │
        ▼
      FAISS
(Vector Search)
        │
        ▼
Generated Response
        │
        ▼
Meta SeamlessM4T
(Text-to-Speech)
        │
        ▼
Voice Output
```

---

# 🛠️ Technology Stack

| Component | Technology |
|------------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Llama 3 |
| Speech-to-Text | NVIDIA NeMo |
| Translation | Meta SeamlessM4T |
| Text-to-Speech | Meta SeamlessM4T |
| Framework | LangChain |
| Vector Database | FAISS |
| Database | MongoDB |
| Deployment | Docker |
| Cloud | AWS |


# 📂 Project Structure

```
tribal-ai-chatbot/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── database/
│   └── main.py
│
├── frontend/
│   ├── pages/
│   ├── components/
│   └── app.py
│
├── rag/
│   ├── embeddings/
│   ├── vector_store/
│   └── documents/
│
├── models/
│
├── docker/
│
├── tests/
│
├── requirements.txt
│
├── Dockerfile
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/tribal-ai-chatbot.git

cd tribal-ai-chatbot
```


## Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
uvicorn backend.main:app --reload
```

---

## Run Frontend

```bash
streamlit run frontend/app.py
```

---

# 🐳 Docker

Build

```bash
docker build -t tribal-chatbot .
```

Run

```bash
docker run -p 8000:8000 tribal-chatbot
```

# ☁️ AWS Deployment

The application can be deployed using:

- AWS EC2
- Docker
- Nginx
- MongoDB Atlas

# 🔮 Future Improvements

- Offline mode
- Mobile application
- AI Agents
- Image understanding
- Video understanding
- Live translation
- Government scheme assistant
- Healthcare assistant
- Agriculture advisor
- Multi-user authentication
- Analytics Dashboard

---

# 📈 Roadmap

- ✅ Speech Recognition
- ✅ Translation
- ✅ RAG Integration
- ✅ Voice Output
- ⏳ AI Agents
- ⏳ Mobile App
- ⏳ Offline Deployment
- ⏳ More Tribal Languages

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Aishwar Gupta**

B.Tech Computer Science Engineering

Generative AI Developer

---

## ⭐ Support

If you like this project, consider giving it a **Star ⭐** on GitHub.
