# 🧭 Travel Chatbot: RAG-Based Smart Assistant for Mumbai & Vijayawada

A personalized, Retrieval-Augmented Generation (RAG) based **AI-powered travel chatbot** designed to answer travel-related queries specifically for **Mumbai** and **Vijayawada**. This project uses custom-curated data, vector search via MongoDB Atlas, the `thenlper/gte-large` embedding model, and the `llama3-8b-8192` model served via Groq for language generation. It also supports **image recommendations** using AWS S3-hosted travel images.

---

## 🚀 Features

- ✈️ Travel query answering for **Mumbai** and **Vijayawada**.
- 🔍 Vector-based semantic search using `MongoDB Atlas Vector Search`.
- 🧠 RAG pipeline: Combines LLM + vector DB for accurate responses.
- 🏞️ Dynamic travel image recommendations based on keywords.
- 🧠 Embeddings powered by `thenlper/gte-large` (1024-dim).
- 💬 Responses generated via `llama3-8b-8192` model on Groq.
- ☁️ Image links fetched from a **preprocessed AWS S3 bucket**.
- 🛠️ Keywords for image search extracted using spaCy + custom LLM prompts.

---

## 🧠 Tech Stack

| Category         | Technology                                |
|------------------|--------------------------------------------|
| LLM              | `llama3-8b-8192` via `groq`                |
| Embeddings       | `thenlper/gte-large` (1024 dim)            |
| Vector Database  | MongoDB Atlas with `$vectorSearch`         |
| Programming Lang | Python                                     |
| Image Search     | Google Custom Search API / MongoDB         |
| Image Storage    | AWS S3                                     |
| NLP Tools        | `spaCy`, `langchain`, `PromptTemplate`     |

---

## 🧾 Sample Use Case

1. User enters a travel-related query:

2. Chatbot performs vector search over `data.json` in MongoDB.
3. Generates a precise answer using `llama3-8b-8192`.
4. Extracts travel-specific keywords: `["Marine Drive", "Carter Road", "Bandstand Promenade"]`.
5. Retrieves and returns image URLs from MongoDB S3-mapped dataset.

---

