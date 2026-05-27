# bsc-dissertation-2026
BSc Dissertation - RAG-Based AI Business Assistant with CRM Integration - University of Derby 2026

# RAG-Based AI Business Assistant with CRM Integration
**BSc Dissertation — University of Derby — Module 6CM995 — May 2026**
**Author:** Saridis Stavros | Student ID: 100728288

## Overview
This dissertation presents the design, implementation, and evaluation 
of a Retrieval-Augmented Generation (RAG) based AI business assistant 
integrated with a CRM system, built for a fictional UK-based B2B SaaS 
company, NexusFlow Solutions.

## Tech Stack
- Python 3.12
- LangChain — RAG pipeline orchestration
- ChromaDB — Vector store (82 chunks, 164 vectors)
- OpenAI GPT-4o-mini — Response generation
- OpenAI text-embedding-3-small — 1,536-dimensional embeddings
- FastAPI — Mock CRM API (7 REST endpoints)
- Streamlit — Chat UI with live metrics and source attribution

## Key Results
- 82.3% keyword coverage
- 96.7% source precision
- 4.73/5 answer relevancy
- 2/2 hallucination resistance tests passed

## Structure
- 6 chapters (~13,700 words)
- 31 APA references
- 5 architecture diagrams
- 13 system screenshots
- RAGAS-inspired evaluation framework (15 test cases)
- Ethical safeguards module (PII detection, bias monitoring, 
  content filtering, JSONL audit logging)
