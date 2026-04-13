# 🚀 RAG PDF Intelligence System

A modern **Retrieval-Augmented Generation (RAG)** application that ingests PDF documents, converts them into embeddings, stores them in a vector database, and enables intelligent querying using LLMs.

---

## 📌 Overview

This project combines **FastAPI**, **Inngest**, **LlamaIndex**, **Qdrant**, and **Ollama** to build a scalable and production-ready RAG pipeline.

It allows you to:
- 📂 Upload and process PDFs  
- 🧠 Convert documents into embeddings  
- 🔍 Store & search vectors efficiently  
- 🤖 Query documents using AI  
- ⚙️ Run asynchronous workflows  

---

## 🏗️ Architecture

User → FastAPI → Inngest → LlamaIndex → Qdrant → Ollama  
                          ↓  
                     Streamlit UI  

---

## 🛠️ Tech Stack

- Python  
- FastAPI  
- Inngest  
- LlamaIndex  
- Qdrant  
- Ollama  
- Streamlit  

---

## 📦 Package Management

```bash
uv init .
uv add fastapi
```

---

## ⚙️ Running the Project

```bash
uv run uvicorn main:app
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
uv run streamlit run streamlit_app.py
```

---

## 📂 Project Structure

.
├── main.py  
├── vector_db.py  
├── query_engine.py  
├── data_loader.py  
├── custom_types.py  
├── streamlit_app.py  
├── query_engine.py  
---

## 📌 Features

- Async workflows  
- Vector search  
- Modular architecture  
- Streamlit UI  
- Production-ready  

---

## 👨‍💻 Author

AI & Software Engineering Enthusiast