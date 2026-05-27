# 🤖 RAG-Based AI Business Assistant with CRM Integration

**BSc Dissertation — University of Derby — Module 6CM995 — May 2026**  
**Author:** Saridis Stavros | Student ID: 100728288  
**Supervisor:** Vasileios Markos

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LangChain](https://img.shields.io/badge/LangChain-1.2.14-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Chat%20UI-FF4B4B)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991)

---

## 📋 Overview

This project presents the design, implementation, and evaluation of a 
Retrieval-Augmented Generation (RAG) based AI business assistant integrated 
with a CRM system, built for a fictional UK-based B2B SaaS company, 
**NexusFlow Solutions**.

The system combines semantic vector retrieval with large language model 
generation to deliver grounded, context-aware responses to natural language 
business queries — without hallucinating data that doesn't exist.

---

## 🏗️ System Architecture

The system consists of five core modules:
User → Streamlit Chat UI → RAG Pipeline → ChromaDB + CRM API → GPT-4o-mini → Ethical Safeguards → Response

- **RAG Pipeline** — Embeds queries, retrieves top-8 relevant chunks, constructs grounded prompts
- **ChromaDB** — Local vector store with 82 chunks and 164 vectors
- **Mock CRM API** — FastAPI with 7 REST endpoints and Swagger documentation
- **Streamlit UI** — Dark theme chat interface with live metrics and source attribution
- **Ethical Safeguards** — PII detection, bias monitoring, content filtering, JSONL audit logging

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| LLM Framework | LangChain v1.2.14+ |
| Vector Database | ChromaDB (local persistent) |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | text-embedding-3-small (1,536 dimensions) |
| CRM API | FastAPI + Uvicorn |
| Chat UI | Streamlit |
| Evaluation | RAGAS-inspired framework |

---

## 📊 Evaluation Results

| Metric | Score |
|---|---|
| Keyword Coverage | 82.3% |
| Source Precision | 96.7% |
| Answer Relevancy | 4.73 / 5 |
| Faithfulness | 3.20 / 5 |
| Avg Response Latency | 3.80s |
| Hallucination Tests | 2/2 passed ✅ |

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))

### 1. Clone the repository
```bash
git clone https://github.com/ssaridis7-blip/bsc-dissertation-2026.git
cd bsc-dissertation-2026
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\Activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install langchain langchain-classic langchain-openai langchain-community langchain-text-splitters chromadb openai fastapi uvicorn streamlit python-dotenv pypdf tiktoken
```

### 4. Set up your OpenAI API key
Create a `.env` file in the project root:
OPENAI_API_KEY=your-api-key-here

---

## ▶️ Running the System

### Build the vector store
```bash
python src/rag_pipeline.py
```
This loads all documents, creates 82 chunks, generates 164 vectors and stores them in ChromaDB.

### Start the CRM API
```bash
python src/crm_api.py
```
Then open **http://localhost:8000/docs** to see the interactive Swagger UI with all 7 endpoints.

### Launch the Chat UI
```bash
streamlit run src/app.py
```
Then open **http://localhost:8501** to use the NexusFlow CRM Assistant.

### Run the evaluation framework
```bash
python evaluation/evaluate.py
```
Runs 15 test cases and generates a full evaluation report.

### Test the ethical safeguards
```bash
python src/ethical_safeguards.py
```
Runs 5 test scenarios covering PII detection, bias monitoring, and content filtering.

---

## 💬 Example Queries

**Single-source queries:**
- "Who is James Mitchell?"
- "What invoices are pending?"
- "What pricing tiers are available?"

**Multi-hop queries (system strength):**
- "Tell me about David Okafor's account, his interactions, and any invoices"
- "Give me a summary of Sarah Chen's pipeline — what deals is she managing?"
- "Which customers have both pending invoices and active deals?"

**Hallucination resistance (system should decline):**
- "What is the phone number for John Smith at DataCorp?"
- "What was the revenue for Q4 2025?"

---

## 📁 Project Structure
bsc-dissertation-2026/
├── data/
│   ├── synthetic_crm_data.json      # Synthetic CRM dataset
│   └── knowledge_base/              # 4 business knowledge documents
│       ├── company_overview.md
│       ├── product_faq.md
│       ├── sales_playbook.md
│       └── onboarding_guide.md
├── src/
│   ├── rag_pipeline.py              # Core RAG system
│   ├── crm_api.py                   # FastAPI mock CRM
│   ├── app.py                       # Streamlit chat UI
│   └── ethical_safeguards.py        # PII, bias, content filtering
├── evaluation/
│   ├── evaluate.py                  # 15-test evaluation framework
│   ├── evaluation_results.json      # Raw results
│   └── evaluation_report.txt        # Formatted report
├── Final_Thesis_FINAL.docx          # Full dissertation
├── test_setup.py                    # Setup verification
└── .gitignore

---

## 📄 Dissertation

The full dissertation (`Final_Thesis_FINAL.docx`) is included in this repository and covers:
- Literature review of RAG architectures and CRM integration
- System design and implementation methodology
- Evaluation framework and results analysis
- Ethical safeguards design and validation
- Self-reflection and future work directions

---

## ⚠️ Important Notes

- This system uses **synthetic data only** — no real customer information
- You need your own OpenAI API key to run the system
- The `.env` file is excluded from the repository for security
- Approximately $2–5 of OpenAI credits is sufficient to run all tests

---

*Built as part of a BSc Computer Science dissertation at the University of Derby, 2026.*
