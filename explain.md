# RAG
RAG is a technique that enables an AI model to retrieve relevant information from external sources before generating a response, rather than relying only on its internal knowledge.

Retrieval = AI kayqleb 3la ma3lomat mn source (documents, PDFs, database, website...).
Augmented = kayzid had lma3lomat l prompt.
Generation = b3d mn hadchi kaywld ljawab.

Chno kaydir RAG?
RAG kayzid qbl ma LLM yjawb.

User Question
      │
      ▼
Retriever (RAG)
      │
      ├── Kayqleb f PDFs / Database / Website / Documents
      ▼
Relevant Information
      ▼
LLM
      ▼
Final Answer

# big rag example
User:
"How much is Dior Sauvage 100ml?"

Bla RAG:
LLM ymkn ygol: "Around $120."
Walakin hadchi ymkn maykounch thaman dyalk.

M3a RAG:
Kayqleb f database dyal store dyalk.
Kayl9a: Dior Sauvage 100ml = 1,150 MAD.
Kay3ti had lma3loma l LLM.

LLM kayjawb:
"The current price of Dior Sauvage 100ml is 1,150 MAD."

3lach RAG kay3ti ajwiba a7san?
✅ Kayst3ml real data machi tkhmin.
✅ Kayqra documents li ma kanch LLM t3llm mnha.
✅ Kayjib latest information (stock, prices, policies...).
✅ Kay9ll lhallucinations (ikhtira3 lma3lomat).

# libraries allowed to use
transformers  → handles loading Qwen, no need to build LLM from scratch
bm25s         → handles search, no need to implement BM25 math
fire          → handles CLI, no need to parse sys.argv manually
tqdm          → handles progress bars, one line of code
pydantic      → handles validation, just define your models

# uv
 is a Python package manager js like pip
pyproject.toml          ← you define what you need
      ↓
uv resolves versions    ← finds compatible versions of everything
      ↓
uv.lock                 ← locks exact versions (reproducible)
      ↓
.venv/                  ← creates virtual environment automatically
      ↓
installs packages       ← downloads and installs everything

uv.lock is a file that locks the exact versions of every package installed.

# fire cli comand line
Fire turned your methods into commands automatically

import fire
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def multiply(self, a: int, b: int) -> int:
        return a * b

fire.Fire(Calculator)

do like:
python calc.py add 3 5
# Output: 8
python calc.py multiply 4 6
# Output: 24


# My tasks
1. Ingest vLLM repo      → read files, chunk, index
2. Search knowledge base → BM25 finds relevant chunks
3. Answer questions      → Qwen reads chunks, generates answer
4. Evaluate quality      → recall@k measures how good your search is


# all steps details of step 1 (Knowledge Base Ingestion System)
"Read and process all files from the vLLM repository"
walk through data/raw/vllm-0.10.1/
find all .py files  → Python code
find all .md files  → Markdown docs
read their content

"Implement intelligent chunking"
.py files  → chunk by functions/classes
           → keep functions together, don't split them

.md files  → chunk by sections (## headers)
           → keep paragraphs together

max size   → 2000 characters per chunk

"Create a searchable index using BM25" (Index = a data structure that makes searching fast.Index = a data structure that makes searching fast.)
take all chunks
feed them to bm25s
build the index

"Store the index for fast retrieval"
save chunks    → data/processed/chunks/
save bm25 index → data/processed/bm25_index/

next time you search:
→ load from disk (fast)
→ no need to re-index everything

The CLI command:
bashuv run python -m student index --max_chunk_size 2000
- reads all files
- chunks them
- builds BM25 index
- saves everything to disk
- must finish in under 5 minutes

What gets saved to disk:
data/processed/
├── chunks/
│   ├── py_chunks.json    ← all python chunks
│   └── md_chunks.json    ← all markdown chunks
└── bm25_index/
    └── index.pkl         ← saved BM25 index

After that you just load the index for searching.


# # all steps details of step 1 (Retrieval System)
"Implement semantic search over the indexed knowledge base"
load BM25 index from disk
take a question
search the index
return relevant chunks

"Return top-k most relevant code snippets"
k=5  → return 5 best chunks
k=10 → return 10 best chunks
k is configurable via CLI argument

"Each result must include"
python# every result must have these 3 fields
{
    "file_path": "vllm/engine/llm_engine.py",
    "first_character_index": 1500,
    "last_character_index": 3200
}
That's the MinimalSource pydantic model from the subject.

"Support batch processing of multiple questions"
- single question
python -m student search "how does vLLM handle memory?"

- batch - process whole dataset at once
python -m student search_dataset
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json
    --k 10
    --save_directory data/output/search_results

"Achieve at least 80% recall@5"
docs questions → your top 5 results must contain 
                 correct source 80% of the time

code questions → your top 5 results must contain
                 correct source 50% of the time

What retrieval.py does step by step:
1. load index from data/processed/bm25_index/
2. load chunks from data/processed/chunks/
3. take question as input
4. search BM25 index with question
5. get top-k chunk indices
6. look up those chunks
7. return list of MinimalSource objects

Output for one question:
json{
    "question_id": "q1",
    "question": "How does vLLM handle memory?",
    "retrieved_sources": [
        {
            "file_path": "vllm/engine/llm_engine.py",
            "first_character_index": 1500,
            "last_character_index": 3200
        },
        {
            "file_path": "docs/memory.md",
            "first_character_index": 500,
            "last_character_index": 1500
        }
    ]
}

# step 4 Answer Generation System
Step by step what generation.py does:
1. load Qwen model (once)
2. take question + retrieved chunks as input
3. read chunk texts from files using character positions
4. build prompt with chunks as context
5. run Qwen → generate answer
6. return MinimalAnswer pydantic object


# cli command line
index
bashuv run python -m student index --max_chunk_size 2000
- calls ingestion.py
- reads vLLM files, chunks them, builds BM25 index
- saves everything to disk

search
bashuv run python -m student search "how does vLLM handle memory?" --k 5
- calls retrieval.py
- searches index
- prints top-k results to terminal

search_dataset
bashuv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results
- calls retrieval.py in a loop
- processes all questions in dataset
- saves results to JSON file

answer
bashuv run python -m student answer "how does vLLM handle memory?" --k 10
- calls retrieval.py + generation.py
- retrieves chunks
- generates answer with Qwen
- prints answer to terminal

answer_dataset
bashuv run python -m student answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer
- calls generation.py in a loop
- reads search results from file
- generates answers for all questions
- saves full JSON to file

evaluate
bashuv run python -m student evaluate \
    --student_answer_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json \
    --k 10
- calls evaluation.py
- compares your results vs ground truth
- prints recall@k scores

# models
MinimalSource              → where in a file the answer is (path + char positions)
UnansweredQuestion         → a question with no answer
AnsweredQuestion           → a question with correct answer (ground truth)
RagDataset                 → list of questions (the dataset files)
MinimalSearchResults       → your search results for one question
MinimalAnswer              → your search results + your generated answer
StudentSearchResults       → all your search results (saved to file)
StudentSearchResultsAndAnswer → all your answers (saved to file)
- all must extend basemodel automatic validation
                            JSON loading/saving
                            type checking

