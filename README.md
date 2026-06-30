*This project has been created as part of the 42 curriculum by yaimghar*

# RAG Against the Machine

## Description

A Retrieval-Augmented Generation (RAG) system that answers questions about the vLLM codebase. The system indexes the vLLM repository, retrieves relevant code snippets and documentation using BM25 search, and generates answers using the Qwen/Qwen3-0.6B language model.

## System Architecture

The pipeline has 4 main components:

1. **Ingestion** (`ingestion.py`) — Reads all `.py` and `.md` files from the vLLM repository, chunks them into pieces of max 2000 characters, builds a BM25 index, and saves everything to disk.

2. **Retrieval** (`retrieval.py`) — Loads the BM25 index, takes a question as input, searches for the top-k most relevant chunks, and returns their file paths and character positions.

3. **Generation** (`generation.py`) — Loads Qwen/Qwen3-0.6B, reads the text of retrieved chunks from the actual files, builds a prompt with context, and generates a natural language answer.

4. **Evaluation** (`evaluation.py`) — Compares retrieved sources against ground truth annotations using recall@k metrics with a 5% minimum overlap threshold.

## Chunking Strategy

Files are split into fixed-size chunks of up to 2000 characters (configurable via `--max_chunk_size`). Each chunk stores its `file_path`, `first_character_index`, `last_character_index`, and `text`. Python (`.py`) and Markdown (`.md`) files are processed separately to allow future improvements with language-specific chunking strategies.

## Retrieval Method

The system uses **BM25** (via the `bm25s` library) for retrieval. BM25 is a term-frequency based ranking algorithm that scores documents by how well their words match the query, considering word rarity (IDF) and document length normalization. The index is built once during ingestion and loaded from disk for each search operation.

## Performance Analysis

| Metric | Docs | Code |
|--------|------|------|
| Recall@1 | 0.600 | 0.360 |
| Recall@3 | 0.760 | 0.510 |
| Recall@5 | 0.820 | 0.600 |
| Recall@10 | 0.860 | 0.650 |

Both pass the minimum thresholds: 80% recall@5 for docs and 50% for code.

## Design Decisions

- **BM25 over TF-IDF**: BM25 provides better ranking with document length normalization.
- **Fixed-size chunking**: Simple and fast. Each chunk is at most 2000 characters, ensuring it fits within the LLM context window.
- **Qwen/Qwen3-0.6B**: Small model that runs on CPU without GPU requirements.
- **Pydantic models**: Used for data validation and automatic JSON serialization/deserialization.
- **Python Fire CLI**: Minimal boilerplate for creating CLI commands.
- **Context limiting**: Only top chunks up to 4000 characters are passed to Qwen to avoid truncation of the question.

## Challenges Faced

- **Qwen output format**: Qwen initially generated tool-calling responses instead of answers. Fixed by using `apply_chat_template` with `enable_thinking=False` and a clear system prompt.
- **Prompt truncation**: Large contexts caused the question to be cut off. Fixed by limiting context size to 4000 characters and using `truncation=True` with `max_length=2048`.
- **CPU performance**: Without GPU, answer generation takes ~18 seconds per question. Mitigated by reducing `max_new_tokens` to 80.
- **File encoding**: Some vLLM files contain non-UTF-8 characters. Fixed with `errors="ignore"`.

## Instructions

### Prerequisites

- Python 3.10+
- uv (package manager)

### Installation

```bash
git clone gitlublink
cd rag_against_the_machine
uv sync
```

### Setup

Place the vLLM repository in the data directory:

```bash
cp vllm-0.10.1.zip data/raw/
cd data/raw && unzip vllm-0.10.1.zip && cd ../..
```

Place the dataset files:

```bash
cp dataset_code_public.json data/datasets/AnsweredQuestions/
cp dataset_docs_public.json data/datasets/AnsweredQuestions/
cp dataset_code_public.json data/datasets/UnansweredQuestions/
cp dataset_docs_public.json data/datasets/UnansweredQuestions/
```

## Example Usage

### Index the repository

```bash
uv run python -m student index --max_chunk_size 2000
```

### Search for a single query

```bash
uv run python -m student search "How to configure OpenAI server?" --k 5
```

### Search a dataset

```bash
uv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results
```

### Answer a single question

```bash
uv run python -m student answer "How to configure OpenAI server?" --k 10
```

### Answer a dataset

```bash
uv run python -m student answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer
```

### Evaluate search results

```bash
uv run python -m student evaluate \
    --student_results_path data/output/search_results/dataset_docs_public.json \
    --ground_truth_path data/datasets/AnsweredQuestions/dataset_docs_public.json \
    --k 10
```

## Resources

- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Retrieval-Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401)
- [Qwen/Qwen3-0.6B on HuggingFace](https://huggingface.co/Qwen/Qwen3-0.6B)
- [vLLM Project](https://github.com/vllm-project/vllm)
- [bm25s Library](https://github.com/xhluca/bm25s)
- [Python Fire](https://github.com/google/python-fire)

### AI Usage

AI (Claude) was used as a learning assistant for:
- Understanding RAG concepts and pipeline architecture
- Debugging pydantic model validation errors
- Prompt engineering for Qwen/Qwen3-0.6B
- Structuring the CLI with Python Fire
All code was reviewed, understood, and tested manually.