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


RAG = Retrieval + Generation
🔍 Retrieval (البحث): كنقلبو على المعلومات فشي مصدر (PDF، DB، API…)
🤖 Generation (التوليد): AI كيستعمل داك المعلومات ويكتب جواب مفهوم

علاش  RAG مهم؟
كيخلي AI مايكذبش بزاف
use your data
كيكون up-to-date

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

"Create a searchable index using BM25" (Index = a data structure that makes searching fast)
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


# bm25

4:10 PM
BM25 uses word matching and scoring.

When you index chunks:

chunk 0: "class LLMEngine handles memory allocation..."
chunk 1: "def process_batch handles requests..."
chunk 2: "## Memory Management PagedAttention..."
BM25 internally builds a table:

word "memory"     → appears in chunk 0, chunk 2
word "handles"    → appears in chunk 0, chunk 1
word "batch"      → appears in chunk 1
word "allocation" → appears in chunk 0
When you search "memory management":

BM25 looks up:
"memory"     → chunk 0 (1 time), chunk 2 (1 time)
"management" → chunk 2 (1 time)

scores:
chunk 0 → score 0.6  (has "memory" but not "management")
chunk 1 → score 0.0  (has neither)
chunk 2 → score 0.9  (has both "memory" and "management")

returns top-2: [chunk 2, chunk 0]
In short:

more matching words = higher score = higher rank
BM25 also considers:

how rare the word is (rare words matter more)
how long the chunk is (shorter chunks ranked higher if same words)
That's the math behind BM25 — but bm25s handles all of it automatically.

Clear? Now write index function!

- kholasa
BM25 input  → question (tokenized)
BM25 output → chunk indices + scores

BM25 already sorted! BM25 returns results by relevance score

# index
return:
results, scores = retriever.retrieve(query, k=5)

results → [[2, 0, 7, 15, 42]]   ← just numbers (chunk indices)
scores  → [[0.9, 0.6, 0.5, 0.3, 0.1]]  ← relevance scores


شنو هو BM25؟
👉 BM25 هو واحد الخوارزمية ديال البحث (ranking algorithm)
bach tl9a ansab document 7asab words li f so2al

ex:
tokenized_query = bm25s.tokenize("How does vLLM handle memory?")
# tokenized_query = ["how", "does", "vllm", "handle", "memory"]

results, scores = retriever.retrieve(tokenized_query, k=5)
# results = [[2847, 156, 9043, 521, 78]]  ← chunk indices
# scores  = [[0.95, 0.82, 0.71, 0.55, 0.42]]  ← relevance scores

tokenized_query → the question split into words (input)
results         → which chunks are most relevant (output)
scores          → how relevant each chunk is (output)
# overlap
Two chunks from same file:
file: docs/features/lora.md

correct:  [============================]
           4000                    6000

yours:              [============================]
                    5000                    7000

The overlap is the shared part:
correct:  [============================]
           4000                    6000

yours:              [============================]
                    5000                    7000

overlap:            [===============]
                    5000        6000   = 1000 chars

How to calculate overlap in code:
pythonoverlap_start = max(4000, 5000) = 5000  # latest start
overlap_end   = min(6000, 7000) = 6000  # earliest end
overlap       = overlap_end - overlap_start = 1000

If no overlap:
correct:  [========]
           0    2000

yours:                    [========]
                          4000  6000

overlap_start = max(0, 4000)    = 4000
overlap_end   = min(2000, 6000) = 2000
overlap       = 2000 - 4000     = -2000 → negative → no overlap

5% rule:
correct size = 6000 - 4000 = 2000
overlap = 1000
percentage = 1000/2000 = 50% >= 5% → FOUND ✅

But also must be same file:
correct: docs/lora.md  4000-6000
yours:   docs/lora.md  5000-7000  ← same file ✅

correct: docs/lora.md  4000-6000
yours:   vllm/engine.py 5000-7000 ← different file ❌


# recall@k
When k_val = 5:
question 1 → check top 5 sources → found? → 1.0
question 2 → check top 5 sources → not found? → 0.0
question 3 → check top 5 sources → found? → 1.0
...
question 100 → check top 5 sources → found? → 1.0

scores = [1.0, 0.0, 1.0, ..., 1.0]
recall@5 = sum(scores) / 100 = 0.820
Same loop runs 4 times — once for each k value:
k_val=1  → check top 1 source per question  → Recall@1: 0.600
k_val=3  → check top 3 sources per question → Recall@3: 0.760
k_val=5  → check top 5 sources per question → Recall@5: 0.820
k_val=10 → check top 10 sources per question → Recall@10: 0.860


# QWEN
BM25 found these 5 chunks (sorted by relevance):
1. docs/usage/reproducibility.md [0:1000]      ← most relevant
2. tests/utils.py [14000:15000]
3. examples/offline_inference/reproducibility.py [0:1000]
4. .buildkite/nightly-benchmarks/README.md [6000:7000]
5. tests/tool_use/utils.py [8000:9000]

Qwen read top chunks (until max_context=4000)
→ found the answer in reproducibility.md
→ generated: "set the global seed for V0 and turn off multiprocessing for V1"