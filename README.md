# ClinicAI
AI Clinical Knowledge Assistant

## 1. Project overview

###  title

**AI Clinical Knowledge Assistant**

### One-line description

A doctor-facing chatbot that answers questions from trusted medical documents, returns citation-backed responses, summarizes protocols, and refuses unsupported answers.

### Why this project matters

This project demonstrates:

* applied AI system design
* retrieval-augmented generation (RAG)
* backend/API engineering
* vector search and metadata filtering
* healthcare-aware safety design
* production-minded architecture

### Target users

* doctors
* residents
* clinical staff
* hospital teams using internal protocols

### Primary use cases

* answer questions from hospital protocols and clinical guidelines
* summarize long guideline sections
* find relevant sections in documents quickly
* compare recommendations across documents
* draft handover notes or internal summaries from retrieved evidence

### Explicit non-goals

This system does **not**:

* diagnose patients autonomously
* prescribe treatment independently
* replace clinical judgment
* operate on live patient care without validation
* use real patient data in the MVP

---

## 2. MVP definition

### MVP goal

Build a doctor-facing assistant that can ingest trusted medical documents and answer questions using only retrieved document context.

### MVP features

1. Upload and index PDF/DOCX medical documents
2. Extract text and chunk documents
3. Generate embeddings and store them in a vector database
4. Retrieve relevant chunks for a doctor’s question
5. Generate an answer grounded only in retrieved content
6. Return inline citations and source metadata
7. Refuse unsupported answers when evidence is missing
8. Log all questions, retrieved sources, and answers for review

### Nice-to-have after MVP

* specialty filters
* document version comparison
* confidence banding
* reranking
* evaluation dashboard
* simple React UI
* clinician feedback buttons

---

## 3. Recommended tech stack

## Backend

* **Python 3.11+**
* **FastAPI**
* **Pydantic**
* **Uvicorn**

## AI / NLP

* LLM API (OpenAI or another provider)
* Embedding model API or local embedding model
* Optional reranker model

## Data / storage

* **PostgreSQL**
* **pgvector**
* SQLAlchemy or SQLModel
* Alembic for migrations
* Redis optional for caching/jobs

## Document processing

* PyMuPDF or pdfplumber for PDF extraction
* python-docx for DOCX
* tiktoken or custom tokenizer-aware chunker

## Frontend

* optional MVP: Swagger + Postman only
* phase 2: React / Next.js

## Infra / DevOps

* Docker
* docker-compose
* pytest
* GitHub Actions

---

## 4. High-level architecture

```text
                +-------------------+
                |   Doctor / User   |
                +---------+---------+
                          |
                          v
                +-------------------+
                |   FastAPI Layer   |
                | /ask /upload etc. |
                +----+---------+----+
                     |         |
         ingestion   |         | query
                     v         v
      +------------------+   +------------------+
      | Document Parser  |   | Retrieval Layer  |
      | chunk metadata   |   | vector search    |
      +--------+---------+   +--------+---------+
               |                      |
               v                      v
      +------------------+   +------------------+
      | Embedding Model  |   |  LLM Generation  |
      +--------+---------+   | source-grounded  |
               |             +--------+---------+
               v                      |
      +--------------------------+    |
      | Postgres + pgvector      |<---+
      | docs chunks embeddings   |
      | versions audit logs      |
      +--------------------------+
```

---

## 5. End-to-end data flow

## A. Document ingestion flow

1. User uploads a trusted medical document
2. Backend stores the raw file
3. Parser extracts text and metadata
4. Text is cleaned and split into chunks
5. Each chunk receives metadata:

   * document id
   * title
   * section
   * page number
   * specialty
   * source organization
   * version/date
6. Embeddings are created for each chunk
7. Chunks + embeddings are stored in Postgres/pgvector
8. Document status becomes `indexed`

## B. Question-answering flow

1. User submits a question
2. System classifies question type (optional)
3. Query embedding is created
4. Vector search retrieves top-k chunks
5. Optional reranker reorders chunks
6. Prompt builder composes:

   * system prompt
   * user question
   * retrieved context
   * citation instructions
   * refusal instructions
7. LLM generates answer
8. Safety checks run on output
9. API returns answer + citations + retrieved document metadata
10. Interaction is stored in audit tables

---

## 6. Core product requirements

## Functional requirements

* upload PDF and DOCX files
* parse and index medical documents
* perform semantic search over chunks
* support question answering with citations
* return source metadata with each answer
* allow filtering by specialty/source/version
* maintain document versions
* log every query and answer
* provide refusal response when evidence is insufficient

## Non-functional requirements

* deterministic API shape
* modular architecture
* secure file handling
* good observability and logs
* reproducible indexing pipeline
* low-latency retrieval for small corpora
* easy local development with Docker

---

## 7. Suggested repository structure

```text
clinical-knowledge-assistant/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ask.py
│   │   │   ├── documents.py
│   │   │   ├── search.py
│   │   │   └── feedback.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── schemas/
│   │   ├── ask.py
│   │   ├── document.py
│   │   └── feedback.py
│   ├── services/
│   │   ├── parser_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── retrieval_service.py
│   │   ├── prompt_service.py
│   │   ├── llm_service.py
│   │   ├── safety_service.py
│   │   └── indexing_service.py
│   ├── utils/
│   │   └── text_cleaning.py
│   └── main.py
├── data/
│   ├── raw/
│   └── processed/
├── tests/
│   ├── test_ask.py
│   ├── test_documents.py
│   └── test_retrieval.py
├── scripts/
│   ├── seed_documents.py
│   └── evaluate_rag.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## 8. Database schema blueprint

## Table: documents

Fields:

* `id` (uuid)
* `title`
* `source_name`
* `source_type` (guideline, protocol, formulary, SOP)
* `specialty`
* `version_label`
* `publication_date`
* `file_path`
* `checksum`
* `status` (uploaded, parsed, indexed, failed)
* `created_at`
* `updated_at`

## Table: document_chunks

Fields:

* `id` (uuid)
* `document_id` (fk)
* `chunk_index`
* `page_number`
* `section_title`
* `content`
* `token_count`
* `embedding` (vector)
* `created_at`

## Table: document_versions

Fields:

* `id`
* `document_family_key`
* `document_id`
* `is_latest`
* `supersedes_document_id`

## Table: query_logs

Fields:

* `id`
* `question`
* `normalized_question`
* `user_role`
* `specialty_filter`
* `created_at`

## Table: retrieval_logs

Fields:

* `id`
* `query_log_id`
* `chunk_id`
* `rank`
* `similarity_score`
* `rerank_score`

## Table: answer_logs

Fields:

* `id`
* `query_log_id`
* `answer_text`
* `model_name`
* `prompt_version`
* `refused` (bool)
* `safety_flag` (bool)
* `latency_ms`
* `created_at`

## Table: feedback

Fields:

* `id`
* `query_log_id`
* `rating` (helpful, unsafe, incomplete)
* `comment`
* `created_at`

---

## 9. API design

## POST /documents/upload

Uploads a file.

Request:

* multipart/form-data
* file
* metadata fields (title, specialty, source_name, source_type, version_label)

Response:

```json
{
  "document_id": "uuid",
  "status": "uploaded"
}
```

## POST /documents/{document_id}/index

Parses, chunks, embeds, and stores vectors.

Response:

```json
{
  "document_id": "uuid",
  "status": "indexed",
  "chunks_created": 148
}
```

## GET /documents

Returns indexed documents and metadata.

## POST /ask

Main question-answering endpoint.

Request:

```json
{
  "question": "What is the first-line treatment for hypertension according to the uploaded protocol?",
  "specialty": "cardiology",
  "top_k": 5,
  "document_ids": []
}
```

Response:

```json
{
  "answer": "According to the uploaded guideline, first-line treatment is ...",
  "refused": false,
  "citations": [
    {
      "document_id": "uuid",
      "title": "Hypertension Guideline",
      "page_number": 12,
      "section_title": "Initial pharmacologic treatment",
      "chunk_id": "uuid"
    }
  ],
  "retrieved_chunks": 5
}
```

## POST /search

Pure retrieval endpoint for semantic search without answer generation.

## POST /feedback

Stores user feedback for a prior answer.

---

## 10. Chunking strategy

### Recommended chunking rules

* chunk size: 400–800 tokens
* overlap: 50–100 tokens
* preserve section boundaries where possible
* attach page number and heading metadata
* do not merge unrelated sections

### Why this matters

Medical documents are hierarchical. Retrieval quality improves when chunks preserve:

* section headings
* tables context
* page references
* source identity

---

## 11. Prompting strategy

## System prompt principles

The LLM should be instructed to:

* answer only from provided context
* cite supporting sources
* avoid unsupported inference
* explicitly say when evidence is insufficient
* keep tone clinical and concise
* never claim to replace clinician judgment

## Example system prompt

```text
You are a clinical knowledge assistant for doctors. Use only the retrieved document context provided to answer the question. If the answer is not supported by the context, say that the available documents do not provide enough evidence. Cite the source document title and section/page for each important claim. Do not invent facts.
```

## Example answer policy

* direct answer first
* then bullet summary if helpful
* then citations
* then note uncertainty if relevant

---

## 12. Safety and guardrails

## MVP safety rules

* answer only from retrieved context
* refuse unsupported answers
* include source citations
* include disclaimer that this is clinician-support only
* log high-risk prompts
* do not use real patient data

## High-risk prompt handling

Flag or refuse prompts like:

* emergency real-time treatment decisions
* exact dosing requests without source evidence
* diagnosis from patient symptoms alone
* patient-specific recommendations from insufficient context

## Example fallback response

```text
I cannot provide a source-supported answer from the currently indexed documents. Please consult the relevant local guideline or specialist source.
```

---

## 13. Evaluation plan

You need evaluation to make this look serious.

## Evaluation goals

Measure:

* retrieval quality
* answer grounding
* citation correctness
* refusal quality
* latency

## Simple evaluation dataset

Create 30–50 manually written questions from your uploaded medical documents.
For each question, define:

* expected source document
* expected section
* ideal answer points

## Metrics

* Recall@k for retrieval
* MRR or hit-rate for relevant chunks
* groundedness pass/fail
* citation accuracy
* answer completeness
* refusal appropriateness

## Manual review rubric

Score 1–5 on:

* relevance
* correctness
* clarity
* evidence support
* safety

---

## 14. Development milestones

## Phase 1 — Backend MVP

Deliverables:

* FastAPI app scaffold
* file upload
* PDF/DOCX parsing
* chunking and embeddings
* pgvector storage
* /ask endpoint with citations

## Phase 2 — Retrieval quality

Deliverables:

* metadata filters
* better chunking
* prompt iteration
* optional reranker
* semantic search endpoint

## Phase 3 — Safety and logging

Deliverables:

* refusal logic
* prompt risk tagging
* full query/retrieval/answer logs
* feedback endpoint

## Phase 4 — Demo readiness

Deliverables:

* lightweight frontend
* seeded guideline set
* evaluation report
* architecture diagram
* README screenshots

---

## 15. 4-week build plan

## Week 1

* scaffold FastAPI app
* set up Postgres + pgvector
* implement document upload and parse flow
* save document metadata

## Week 2

* implement chunking and embedding pipeline
* store chunks and vectors
* build semantic retrieval service
* test with 2–3 documents

## Week 3

* implement /ask endpoint
* add prompt builder and citation formatting
* add refusal behavior
* log questions and answers

## Week 4

* improve retrieval quality
* add specialty/version filters
* write tests
* create README, diagrams, and demo video

---

## 16. README structure

Your GitHub README should include:

* project summary
* architecture diagram
* tech stack
* setup instructions
* API examples
* evaluation approach
* safety limitations
* screenshots/demo GIF
* future improvements

---

## 17. Resume-ready bullets

Use bullets like these:

* Built a clinician-support RAG assistant using **Python, FastAPI, PostgreSQL/pgvector, and LLM APIs** to answer questions from trusted medical guidelines.
* Implemented document ingestion, chunking, embedding generation, semantic retrieval, and citation-backed answer generation.
* Added metadata filtering, refusal logic, and audit logging to improve answer safety and traceability.
* Designed evaluation workflows for retrieval accuracy, groundedness, and citation correctness.

---

## 18. Interview talking points

When presenting this project, explain:

* why you chose a doctor-facing knowledge assistant instead of diagnosis automation
* how RAG reduces hallucinations compared with pure prompting
* how metadata and versioning matter in healthcare documents
* how you handled unsupported questions safely
* how you would evolve the system for production

---

## 19. Future extensions

After MVP, you can add:

* reranking models
* table extraction
* multilingual retrieval
* clinician persona modes
* source comparison mode
* role-based access control
* human review workflow
* summarization of synthetic patient cases against guideline docs

---

## 20. Minimal success criteria

The project is successful if it can:

1. index at least 5 trusted medical documents
2. answer at least 20 test questions with citations
3. refuse unsupported questions reliably
4. expose a clean FastAPI interface
5. be explained clearly in GitHub and interviews

---

## 21. Best first implementation choices

To keep scope manageable, start with:

* FastAPI
* Postgres + pgvector
* one embedding provider
* one LLM provider
* PDF-only support first
* no frontend until backend works
* public medical guidelines only

---

## 22. Final portfolio positioning

### Project title for GitHub

**AI Clinical Knowledge Assistant**

### Project subtitle

A citation-grounded RAG system for doctor-facing question answering over trusted medical documents.

### Best positioning for recruiters

This project shows strong alignment with:

* AI engineer roles
* applied AI roles
* data/ML platform roles
* healthcare AI product roles
* consulting roles needing production-minded AI design
