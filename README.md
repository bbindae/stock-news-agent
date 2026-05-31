# 📈 Stock News AI Agent

An AI-powered financial agent built with LangGraph that automates fetching, bilingual summarizing, and storing top stock market news via LangServe REST APIs.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)
![uv](https://img.shields.io/badge/uv-Package_Manager-purple)

An AI-powered automated pipeline designed to fetch, summarize, and archive financial news for specific stock tickers. Built with **LangGraph**, this project serves as the foundational context-gathering module for a broader Multi-Agent Stock/Options Trading System.

## ✨ Key Features

* **Automated News Fetching:** Retrieves the top 3 latest news articles per given stock ticker using web search APIs.
* **Bilingual Summarization:** Leverages Local LLMs (via Ollama) to generate concise summaries of the news in both English and Korean.
* **Data Persistence:** Stores extracted metadata, original URLs, and summaries in a relational database (SQLite/SQLAlchemy) to be used as context for downstream trading agents.
* **REST API Endpoint:** Wrapped in **LangServe** and **FastAPI**, exposing the entire graph workflow as an accessible RESTful API endpoint.
* **Blazing Fast Environment:** Project dependencies and virtual environments are strictly managed using `uv` (Rust-based Python package manager) via `pyproject.toml`.

## 🛠️ Tech Stack

* **Frameworks:** LangChain, LangGraph, LangServe, FastAPI
* **LLM Engine:** Ollama (Qwen2.5, EXAONE 3.5 for optimized Korean/English reasoning)
* **Data & Storage:** SQLite, SQLAlchemy
* **Environment Management:** `uv`

## 🧠 LangGraph Architecture

The agent's workflow is defined as a directed graph with the following stateful nodes:
1. `search_news`: Fetches raw news data and URLs based on target tickers.
2. `summarize_news`: Processes raw text through the Local LLM to generate bilingual summaries.
3. `save_to_db`: Commits the structured data to the database for future RAG (Retrieval-Augmented Generation).

## 🚀 Future Roadmap

* **Vector DB Integration:** Migrate summaries to a Vector Database (e.g., ChromaDB, Pinecone) for advanced semantic search and macro-economic theme analysis.
* **Multi-Agent Expansion:** Integrate with a Trading & Options Analysis Agent that utilizes this database to generate actionable financial insights and trade suggestions.
